#!/bin/bash -e

export DATE=`date +%Y%m%d-%H%M%S`
export ANONYMIZED_SNAPSHOT_ID="$DB_INSTANCE_IDENTIFIER-$DATE"
export TEMPORARY_INSTANCE_ID="$DB_INSTANCE_IDENTIFIER-$DATE"

export SNAPSHOT_ID=$(aws rds describe-db-snapshots --include-shared | jq --arg instance_identifier "$DB_INSTANCE_IDENTIFIER" '[.DBSnapshots[] | select(.DBInstanceIdentifier == $instance_identifier)][-1]' | jq '.DBSnapshotArn' |  tr -d '"\\')

echo "Copying shared snapshot $SNAPSHOT_ID"
aws rds copy-db-snapshot \
    --source-db-snapshot-identifier $SNAPSHOT_ID \
    --target-db-snapshot-identifier $ANONYMIZED_SNAPSHOT_ID \
    --kms-key-id $KMS_KEY_ID --output text

echo "Waiting for snapshot $ANONYMIZED_SNAPSHOT_ID to enter 'available' state..."
export ATTEMPT=0
export MAX_ATTEMPT=600
while true
do
    export SNAPSHOT_STATUS=$(aws rds describe-db-snapshots --db-snapshot-identifier $ANONYMIZED_SNAPSHOT_ID --query 'DBSnapshots[0].Status' --output text)
    if [[ $SNAPSHOT_STATUS == "available" ]];
    then
        echo "Snapshot $ANONYMIZED_SNAPSHOT_ID is now available."
        break
    else
        echo "Snapshot $ANONYMIZED_SNAPSHOT_ID status is: $SNAPSHOT_STATUS. Waiting..."
    fi
    if [[ $ATTEMPT -le $MAX_ATTEMPT ]];
    then
        sleep 60s
    else
        echo "Snapshot creation timed out"
        exit 1
    fi
    ATTEMPT=$((ATTEMPT + 1))
done
echo "Copying shared snapshot is finished"

echo "Restoring snapshot $ANONYMIZED_SNAPSHOT_ID to a temporary db instance $TEMPORARY_INSTANCE_ID..."
aws rds restore-db-instance-from-db-snapshot \
    --db-instance-identifier $TEMPORARY_INSTANCE_ID \
    --db-snapshot-identifier $ANONYMIZED_SNAPSHOT_ID \
    --db-instance-class $TEMPORARY_INSTANCE_CLASS \
    --db-subnet-group-name $SUBNET_GROUP_ID \
    --no-multi-az \
    --output text

echo "Waiting for database instance $TEMPORARY_INSTANCE_ID to enter 'available' state..."
aws rds wait db-instance-available --db-instance-identifier $TEMPORARY_INSTANCE_ID
INSTANCE_STATUS=$(aws rds describe-db-instances --db-instance-identifier $TEMPORARY_INSTANCE_ID --query 'DBInstances[0].[DBInstanceStatus]' --output text )
echo "$TEMPORARY_INSTANCE_ID instance state is: $INSTANCE_STATUS"
echo "Finished creating instance $TEMPORARY_INSTANCE_ID from snapshot $ANONYMIZED_SNAPSHOT_ID"

echo "Dump database"
TEMPORARY_INSTANCE_ENDPOINT=$(aws rds describe-db-instances --db-instance-identifier $TEMPORARY_INSTANCE_ID --query 'DBInstances[0].Endpoint.Address' --output text)
echo "$TEMPORARY_INSTANCE_ENDPOINT:5432:$DATABASE_NAME:$DATABASE_USERNAME:$DATABASE_PASSWORD" > ~/.pgpass
chmod 600 ~/.pgpass
pg_dump --clean --no-owner --no-privileges -Fc -h $TEMPORARY_INSTANCE_ENDPOINT  -d $DATABASE_NAME -U $DATABASE_USERNAME -p 5432 -f /dumps/osh_prod_large_anonimized.dump -w --verbose
ls -la /dumps
echo "Dump database is finished"
echo "Copy dump to S3"
aws s3 cp /dumps/osh_prod_large_anonimized.dump s3://oshub-dumps-anonymized/osh_prod_large_anon.dump

echo "Delete temporary database instance"
aws rds delete-db-instance \
    --db-instance-identifier $TEMPORARY_INSTANCE_ID \
    --skip-final-snapshot \
    --output text

echo "done"
