import boto3
from botocore.exceptions import ClientError
import pg8000.native
import os
import time

try:
    db_instance_identifier = os.environ['SOURCE_DATABASE_IDENTIFIER']
    temporary_db_identifier = os.environ['ANONYMIZER_DATABASE_IDENTIFIER']
    database_name = os.environ['SOURCE_DATABASE_NAME']
    database_user = os.environ['SOURCE_DATABASE_USER']
    database_password = os.environ['SOURCE_DATABASE_PASSWORD']
    destination_aws_account = os.environ['DESTINATION_AWS_ACCOUNT']
    temporary_db_instance_size = os.environ['ANONYMIZER_DATABASE_INSTANCE_TYPE']
    temporary_db_subnet_group_name = os.environ['DATABASE_SUBNET_GROUP_NAME']
    temporary_db_security_group_ids = os.environ['DATABASE_SECURITY_GROUP_IDS']
    kms_key = os.environ['KMS_KEY']
    aws_region = os.environ['AWS_REGION']
except:
    print("An exception occurred")
    exit(1)
try:
    source_session = boto3.Session()
except:
    print("session creating error")
    exit(1)
try:
    source = source_session.client('rds')
except:
    print("client creating error")
    exit(1)

print('Get latest automated snapshot of ' + db_instance_identifier + ' database')
snapshots = source.describe_db_snapshots(DBInstanceIdentifier=db_instance_identifier, SnapshotType='automated')

if not snapshots['DBSnapshots']:
    print('No snapshots found for instance identifier {}'.format(db_instance_identifier))
    exit(1)

latest_snapshot = sorted(snapshots['DBSnapshots'], key=lambda x: x['SnapshotCreateTime'], reverse=True)[0]
snapshot_identifier = latest_snapshot['DBSnapshotIdentifier']

print("Create temporary database from " + snapshot_identifier)
try:
    source.restore_db_instance_from_db_snapshot(
        DBInstanceIdentifier=temporary_db_identifier,
        DBSnapshotIdentifier=snapshot_identifier,
        DBInstanceClass=temporary_db_instance_size,
        DBSubnetGroupName=temporary_db_subnet_group_name,
        MultiAZ=False,
        PubliclyAccessible=False,
        AutoMinorVersionUpgrade=False,
        VpcSecurityGroupIds=[temporary_db_security_group_ids],
        DeletionProtection=False
    )
except ClientError as e:
    print("Unexpected error: %s" % e)

db_instance_waiter = source.get_waiter('db_instance_available')
db_instance_waiter.config.delay = 120
db_instance_waiter.config.max_attempts = 120
db_instance_waiter.wait(DBInstanceIdentifier=temporary_db_identifier)
print('Temporary database restored successfully')

print('Get database host and port')
response = source.describe_db_instances(DBInstanceIdentifier=temporary_db_identifier)
database_host = response['DBInstances'][0]['Endpoint']['Address']
database_port = response['DBInstances'][0]['Endpoint']['Port']

print('Anonymize database')
connection_information = dict(
    user=database_user,
    host=database_host,
    port=database_port,
    password=database_password,
    database=database_name,
)

db = pg8000.native.Connection(**connection_information)
db.run(open("anonymize_script.sql", "r").read())
print('Database anonymized successfully!')

anonymized_snapshot_identifier = snapshot_identifier.replace('rds:', '') + '-anonymized'

print('Delete temporary database and create final snapshot: ' + anonymized_snapshot_identifier)
source.delete_db_instance(
    DBInstanceIdentifier=temporary_db_identifier,
    SkipFinalSnapshot=False,
    FinalDBSnapshotIdentifier=anonymized_snapshot_identifier
)

waiters = source.get_waiter('db_snapshot_completed')
waiters.wait(
    DBSnapshotIdentifier=anonymized_snapshot_identifier,
    WaiterConfig={
        'Delay': 15,
        'MaxAttempts': 100
    }
)

print('Database deleted successfully!')

shared_snapshot_identifier = anonymized_snapshot_identifier + "-shared"
response = source.copy_db_snapshot(
    SourceDBSnapshotIdentifier=anonymized_snapshot_identifier,
    TargetDBSnapshotIdentifier=shared_snapshot_identifier,
    KmsKeyId=kms_key,
    CopyTags=True,
    CopyOptionGroup=False,
    SourceRegion=aws_region
)

attempt = 0
while attempt < 300:
    response = source.describe_db_snapshots(DBSnapshotIdentifier=shared_snapshot_identifier)
    snapshot_status = response['DBSnapshots'][0]['Status']

    if snapshot_status == 'available':
        print(f"Snapshot {shared_snapshot_identifier} is now available.")
        break
    else:
        print(f"Snapshot {shared_snapshot_identifier} status: {snapshot_status}. Waiting...")

    time.sleep(60)
    attempt += 1

print("Share snapshot " + shared_snapshot_identifier + " with " + destination_aws_account + " AWS account")
source.modify_db_snapshot_attribute(
    DBSnapshotIdentifier=shared_snapshot_identifier,
    AttributeName='restore',
    ValuesToAdd=[
        destination_aws_account
    ],
    ValuesToRemove=[
        'all',
    ]
)
print('Snapshot exported successfully!')
