import json
import time
import socket
import boto3

ELB = boto3.client('elbv2')


def handler(event: dict, context: dict) -> dict:
    '''
    Args:
        event (dict): The event object containing the RDS proxy endpoint and
            NLB target group ARN and the database port.
            Example:
            {
                'rds_proxy_endpoint': 'rds-proxy-endpoint',
                'nlb_target_group_arn': 'nlb-target-group-arn',
                'db_port': 5432
            }
        context (dict): The context object containing the AWS Lambda function
            context.

    Returns:
        dict: A dictionary containing the RDS proxy endpoint, NLB target group
        ARN, database port, RDS proxy IPs, NLB target group targets, and NLB
        target group health.
    '''
    rds_proxy_endpoint = event.get('rds_proxy_endpoint')
    nlb_target_group_arn = event.get('nlb_target_group_arn')
    db_port = event.get('db_port')
    timeout = event.get('timeout')

    if not all([rds_proxy_endpoint, nlb_target_group_arn, db_port]):
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': ('rds_proxy_endpoint, nlb_target_group_arn, '
                          'and db_port are required.')
            })
        }

    ips = resolve_rds_proxy_ips(rds_proxy_endpoint, timeout)
    targets = get_targets(ips, db_port)

    register_targets(nlb_target_group_arn, targets)

    desired_targets = {
        (target['Id'], target['Port']) for target in targets
    }
    wait_healthy(nlb_target_group_arn, desired_targets, timeout)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'rds_proxy_endpoint': rds_proxy_endpoint,
            'nlb_target_group_arn': nlb_target_group_arn,
            'db_port': db_port,
            'rds_proxy_ips': ips,
            'nlb_target_group_targets': targets,
            'nlb_target_group_health': describe_target_health(
                nlb_target_group_arn)
        })
    }


def resolve_rds_proxy_ips(
        rds_proxy_endpoint: str,
        timeout: int) -> list[str]:
    '''
    Resolve private A records for `rds_proxy_endpoint`. Retry for up to ~60s
    by default. We run inside the VPC so we should get the proxy's private
    ENI IPs.
    '''
    sleep_time = 2
    attempts = int(timeout / sleep_time)
    for _ in range(attempts):
        infos = socket.getaddrinfo(
            rds_proxy_endpoint, None, socket.AF_INET, socket.SOCK_STREAM)
        addrs = sorted({info[4][0] for info in infos})
        if addrs:
            return addrs
        time.sleep(sleep_time)
    raise TimeoutError(f'DNS A records not found for {rds_proxy_endpoint} '
                       f'after {timeout} seconds.')


def get_targets(ips: list[str], port: int) -> list[dict]:
    return [{'Id': ip, 'Port': int(port)} for ip in ips]


def register_targets(target_group_arn: str, targets: list[dict]) -> None:
    if targets:
        ELB.register_targets(TargetGroupArn=target_group_arn, Targets=targets)


def describe_target_health(target_group_arn: str) -> list[dict]:
    return ELB.describe_target_health(
        TargetGroupArn=target_group_arn).get('TargetHealthDescriptions', [])


def wait_healthy(
        target_group_arn: str,
        desired_targets: set[tuple[str, int]],
        timeout: int) -> None:
    '''
    Optionally wait until all desired (ip, port) are healthy in the TG.
    '''
    sleep_time = 2
    attempts = int(timeout // sleep_time)
    for _ in range(attempts):
        descriptions = describe_target_health(target_group_arn)
        healthy_targets = {
            (description['Target']['Id'],
             int(description['Target']['Port']))
            for description in descriptions
            if description['TargetHealth']['State'] == 'healthy'
        }
        if all(desired_target in healthy_targets
               for desired_target in desired_targets):
            return
        time.sleep(sleep_time)
    raise TimeoutError('NLB target group targets not healthy before timeout.')
