#!/bin/sh

set -eu

# Default to Production if not provided from GH Action input.
ENV_TAG="${ENVIRONMENT:-Production}"

echo "Selected ENVIRONMENT: $ENV_TAG"

# Choose AWS credentials for bastion lookup based on environment
if [ "$ENV_TAG" = "Development" ]; then
  AWS_ID="$AWS_ACCESS_KEY_ID_TEST"
  AWS_SECRET="$AWS_SECRET_ACCESS_KEY_TEST"
  AWS_REGION="$AWS_DEFAULT_REGION_TEST"
  echo "Using TEST AWS credentials for bastion lookup"
else
  AWS_ID="$AWS_ACCESS_KEY_ID_PROD"
  AWS_SECRET="$AWS_SECRET_ACCESS_KEY_PROD"
  AWS_REGION="$AWS_DEFAULT_REGION_PROD"
  echo "Using PROD AWS credentials for bastion lookup"
fi

bastion="$(AWS_ACCESS_KEY_ID="$AWS_ID" \
           AWS_SECRET_ACCESS_KEY="$AWS_SECRET" \
           AWS_DEFAULT_REGION="$AWS_REGION" \
           aws ec2 describe-instances --filters "Name=tag:Environment,Values=$ENV_TAG" --query 'Reservations[0].Instances[0].PublicDnsName' --output text || true)"

if [ -z "${bastion}" ] || [ "${bastion}" = "None" ]; then
  echo "ERROR: Could not resolve bastion host for Environment=$ENV_TAG (region=$AWS_REGION)."
  echo "Ensure correct AWS credentials/region and that the bastion is tagged Environment=$ENV_TAG."
  exit 1
fi

echo "Bastion: $bastion"
ssh-keyscan "$bastion" > ~/.ssh/known_hosts

echo "localhost:5433:$DATABASE_NAME:$DATABASE_USERNAME:$DATABASE_PASSWORD" > ~/.pgpass
chmod 600 ~/.pgpass

# Ensure key perms inside container
chmod 600 /keys/key || true

# Safely log SSH key fingerprint (no key content)
if FP=$(ssh-keygen -y -f /keys/key 2>/dev/null | ssh-keygen -lf - 2>/dev/null | awk '{print $2}'); then
  echo "Using SSH key fingerprint: $FP"
else
  echo "WARNING: Could not compute SSH key fingerprint from /keys/key"
  echo "If this is a passphrase-protected key or has invalid formatting/line-endings, SSH may fail."
fi

# Try SSH port-forward with common usernames (POSIX loop)
SSH_OK=0
SSH_USER=""
for USER in ec2-user ubuntu; do
  echo "Attempting SSH port-forward as user: $USER"
  if ssh -f -i /keys/key -o IdentitiesOnly=yes -o StrictHostKeyChecking=no \
       -L 5433:database.service.osh.internal:5432 -N "${USER}@${bastion}" 2>/dev/null; then
    SSH_OK=1
    SSH_USER="$USER"
    break
  fi
  echo "SSH as $USER failed; trying next user if available..."
  # brief pause
  sleep 1
done

if [ "$SSH_OK" -ne 1 ]; then
  echo "ERROR: Failed to start SSH port-forward to database via bastion with users: ec2-user ubuntu"
  echo "Check that /keys/key matches the bastion authorized_keys and that the correct username is used."
  exit 1
fi

echo "SSH port-forward established using user: $SSH_USER"

# Wait for the local tunnel to become ready
max_tries=20
try=1
until pg_isready -h localhost -p 5433 -d "$DATABASE_NAME" -U "$DATABASE_USERNAME" >/dev/null 2>&1; do
  if [ "$try" -ge "$max_tries" ]; then
    echo "ERROR: Database tunnel to localhost:5433 not ready after $max_tries attempts."; exit 1
  fi
  echo "Waiting for database tunnel (attempt $try/$max_tries)..."
  sleep 2
  try=$((try+1))
done

echo "Database tunnel is ready. Proceeding with pg_dump."

case "$ENV_TAG" in
  "Rba")
    DUMP_BASE="osh_rba_large"
    ;;
  "Development")
    DUMP_BASE="osh_dev_large"
    ;;
  *)
    DUMP_BASE="osh_prod_large"
    ;;
 esac

pg_dump --clean --no-owner --no-privileges -Fc -h localhost  -d "$DATABASE_NAME" -U "$DATABASE_USERNAME" -p 5433 -f "/dumps/${DUMP_BASE}.dump" -w --verbose
ls -la /dumps

echo "Start anonymization"

docker-entrypoint.sh -c 'shared_buffers=2048MB' -c 'max_connections=10' &

sleep 15s
pg_isready -d anondb -U anondb -h localhost -p 5432

SQL_SCRIPT="DO \$\$
DECLARE
    current_table text;
    column_exists_email boolean;
    column_exists_username boolean;
    column_exists_password boolean;
    column_exists_phone_number boolean;
BEGIN
    FOR current_table IN (SELECT table_name FROM information_schema.tables WHERE table_schema = 'public')
    LOOP
        EXECUTE 'SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = ''' || current_table || ''' AND column_name = ''email'')' INTO column_exists_email;
        EXECUTE 'SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = ''' || current_table || ''' AND column_name = ''username'')' INTO column_exists_username;
        EXECUTE 'SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = ''' || current_table || ''' AND column_name = ''password'')' INTO column_exists_password;
        EXECUTE 'SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = ''' || current_table || ''' AND column_name = ''phone_number'')' INTO column_exists_phone_number;

        IF column_exists_email THEN
            EXECUTE 'UPDATE ' || current_table || ' SET
                email = CASE WHEN email NOT LIKE ''%@speedandfunction.com'' AND email NOT LIKE ''%@opensupplyhub.org'' THEN md5(random()::text) || ''@'' || substring(email from position(''@'' in email) + 1) ELSE email END';

            IF column_exists_username THEN
                EXECUTE 'UPDATE ' || current_table || ' SET
                    username = CASE WHEN email NOT LIKE ''%@speedandfunction.com'' AND email NOT LIKE ''%@opensupplyhub.org'' THEN substr(md5(random()::text), 1, 20) ELSE username END';
            END IF;

            IF column_exists_password THEN
                EXECUTE 'UPDATE ' || current_table || ' SET
                    password = CASE WHEN email NOT LIKE ''%@speedandfunction.com'' AND email NOT LIKE ''%@opensupplyhub.org'' THEN md5(random()::text) ELSE password END';
            END IF;

            IF column_exists_phone_number THEN
                EXECUTE 'UPDATE ' || current_table || ' SET
                    phone_number = CASE WHEN email NOT LIKE ''%@speedandfunction.com'' AND email NOT LIKE ''%@opensupplyhub.org'' THEN md5(random()::text) ELSE phone_number END';
            END IF;
        END IF;
    END LOOP;
END \$\$;"


pg_restore --verbose --clean --if-exists --no-acl --no-owner -d anondb -U anondb -h localhost -p 5432 < "/dumps/${DUMP_BASE}.dump"
psql -U anondb -d anondb -h localhost -p 5432 -c "$SQL_SCRIPT"
pg_dump --clean --no-owner --no-privileges -Fc -d anondb -U anondb -f "/dumps/${DUMP_BASE}_anonymized.dump" -w --verbose

ls -la /dumps

echo "Finished anonymization"

AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID_TEST \
    AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY_TEST \
    AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION_TEST \
    aws s3 cp "/dumps/${DUMP_BASE}_anonymized.dump" "s3://oshub-dumps-anonymized/${DUMP_BASE}_anon.dump"
