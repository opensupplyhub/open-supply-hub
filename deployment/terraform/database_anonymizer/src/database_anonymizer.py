import boto3
from botocore.exceptions import ClientError
import psycopg

def lambda_handler(event, context):
    db_instance_identifier = 'opensupplyhub-enc-tst'
    temporary_db_identifier = 'database-anonymizer'
    database_name = "db_name"
    database_user = "db_user"
    database_password = "db_pass"
    destination_aws_account="343975343274"

    source_session = boto3.Session()
    source = source_session.client('rds')
    snapshots = source.describe_db_snapshots(DBInstanceIdentifier=db_instance_identifier, SnapshotType='automated')

    if not snapshots['DBSnapshots']:
        return {
            'statusCode': 404,
            'body': 'No snapshots found for instance identifier {}'.format(db_instance_identifier)
        }

    latest_snapshot = sorted(snapshots['DBSnapshots'], key=lambda x: x['SnapshotCreateTime'], reverse=True)[0]
    snapshot_identifier = latest_snapshot['DBSnapshotIdentifier']


    print("\n\nCreate temporary database from " + snapshot_identifier)
    try:
        source.restore_db_instance_from_db_snapshot(
            DBInstanceIdentifier=temporary_db_identifier,
            DBSnapshotIdentifier=snapshot_identifier,
            DBInstanceClass='db.t3.micro',
            DBSubnetGroupName='opensupplyhub-tst',
            MultiAZ=False,
            PubliclyAccessible=False,
            AutoMinorVersionUpgrade=False,
            VpcSecurityGroupIds=[
                'sg-0c865246b5a64b3ca',
            ],
            DeletionProtection=False
        )
    except ClientError as e:
        print("Unexpected error: %s" % e)

    db_instance_waiter = source.get_waiter('db_instance_available')
    db_instance_waiter.config.delay = 120
    db_instance_waiter.config.max_attempts = 120
    db_instance_waiter.wait(DBInstanceIdentifier=temporary_db_identifier)

    response = source.describe_db_instances(DBInstanceIdentifier=temporary_db_identifier)

    database_host = response['DBInstances'][0]['Endpoint']['Address']
    database_port = response['DBInstances'][0]['Endpoint']['Port']

    db = psycopg.connect('%s %s %s %s %s' % (database_host, database_port, database_name, database_user, database_password), serialize=0)
    cur = db.cursor()
    cur.execute(open("anonymize_script.sql", "r").read())
    cur.commit()

    anonymized_snapshot_identifier = snapshot_identifier + '-anonymized'

    source.delete_db_instance(
        DBInstanceIdentifier=temporary_db_identifier,
        SkipFinalSnapshot=False,
        FinalDBSnapshotIdentifier=anonymized_snapshot_identifier
    )

    waiters = source.get_waiter('db_snapshot_completed')
    waiters.wait(DBSnapshotIdentifier=anonymized_snapshot_identifier)

    source.modify_db_snapshot_attribute(
        DBSnapshotIdentifier=anonymized_snapshot_identifier,
        AttributeName='restore',
        ValuesToAdd=[
            destination_aws_account
        ],
        ValuesToRemove=[
            'all',
        ]
    )

    return {
        'statusCode': 200,
        'body': 'Snapshot exported successfully!'
    }
