import boto3
import time

def lambda_handler(event, context):
    request_type = event['RequestType']
    if request_type == 'Create': return on_create(event)
    if request_type == 'Update': return on_update(event)
    if request_type == 'Delete': return on_delete(event)

def on_create(event):
    print('Event Type: Create')
    role_arn = event['ResourceProperties']['TargetAccountRole']
    hosted_zone_id = event['ResourceProperties']['HostedZoneId']
    certificate_flag = bool(event['ResourceProperties'].get('Certificate', False))
    alias_flag = bool(event['ResourceProperties'].get('Alias', False))

    record_name = None
    record_value = None
    record_ttl = None
    domain_name = None
    cert_name = None
    new_certificate = None
    record_type = None
    aws_hosted_zone_id = None

    if certificate_flag:
        domain_name = event['ResourceProperties']['DomainName']
        cert_name = event['ResourceProperties']['CertName']
        record_ttl = int(event['ResourceProperties']['RecordTTL'])
        acm_client = boto3.client('acm')
        new_certificate = acm_client.request_certificate(
            DomainName=cert_name,
            ValidationMethod='DNS',
            DomainValidationOptions=[
                {
                    'DomainName': cert_name,
                    'ValidationDomain': domain_name
                },
            ],
        )
        print(new_certificate)

        time.sleep(10)
        describe_certificate = acm_client.describe_certificate(
            CertificateArn=new_certificate['CertificateArn']
        )
        print(describe_certificate)
        record_value = describe_certificate['Certificate']['DomainValidationOptions'][0]['ResourceRecord']['Value']
        record_name = describe_certificate['Certificate']['DomainValidationOptions'][0]['ResourceRecord']['Name']
        print(record_value)
        print(record_name)
    elif alias_flag:
        aws_hosted_zone_id = event['ResourceProperties']['AwsHostedZoneId']
        record_name = event['ResourceProperties']['RecordName']
        record_value = event['ResourceProperties']['RecordValue']
    else:
        record_name = event['ResourceProperties']['RecordName']
        record_value = event['ResourceProperties']['RecordValue']
        record_type = event['ResourceProperties']['RecordType']

    # Assume a role in the target account
    sts_client = boto3.client('sts')
    assumed_role = sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName=f'cdk-cross-account-record-demo'
    )
    print(f'assumed role {role_arn}')

    # Create a Route 53 client using the assumed role credentials
    route53_client = boto3.client(
        'route53',
        aws_access_key_id=assumed_role['Credentials']['AccessKeyId'],
        aws_secret_access_key=assumed_role['Credentials']['SecretAccessKey'],
        aws_session_token=assumed_role['Credentials']['SessionToken']
    )

    record = {}
    if certificate_flag:
        record = {
                    'Name': record_name,
                    'Type': 'CNAME',
                    'TTL': record_ttl,
                    'ResourceRecords': [{'Value': record_value}]
                }

    elif alias_flag:
        record = {
                    'Name': record_name,
                    'Type': 'A',
                    'AliasTarget': {
                        'HostedZoneId': aws_hosted_zone_id,
                        'DNSName': record_value,
                        'EvaluateTargetHealth': False
                    }
                }
    else:
        record = {
                    'Name': record_name,
                    'Type': record_type,
                    'ResourceRecords': [{'Value': record_value}]
                }

    print(record)

    # Create the Route 53 record in the target account
    response = route53_client.change_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        ChangeBatch={
            'Changes': [{
                'Action': 'CREATE',
                'ResourceRecordSet': record
            }]
        }
    )
    print(f'record response: {response}')

    if certificate_flag:
        return {
            'PhysicalResourceId': record_name.replace(".", ""),
            'Data': {
                'CertificateArn': new_certificate['CertificateArn'],
            }
        }
    else:
        return {
            'PhysicalResourceId': record_name.replace(".", "")
        }

def on_update(event):
    print('Event Type: Update')
    role_arn = event['ResourceProperties']['TargetAccountRole']
    hosted_zone_id = event['ResourceProperties']['HostedZoneId']
    certificate_flag = bool(event['ResourceProperties'].get('Certificate', False))
    alias_flag = bool(event['ResourceProperties'].get('Alias', False))

    record_name = None
    record_value = None
    record_ttl = None
    domain_name = None
    cert_name = None
    new_certificate = None
    record_type = None
    aws_hosted_zone_id = None

    if certificate_flag:
        acm_client = boto3.client('acm')
        list_certifcates = acm_client.list_certificates()
        for certificate in list_certifcates['CertificateSummaryList']:
            if certificate['DomainName'] == cert_name:
                return {
                    'PhysicalResourceId': record_name.replace(".", ""),
                    'Data': {
                        'CertificateArn': certificate['CertificateArn']
                    }
                }
    elif alias_flag:
        aws_hosted_zone_id = event['ResourceProperties']['AwsHostedZoneId']
        record_name = event['ResourceProperties']['RecordName']
        record_value = event['ResourceProperties']['RecordValue']
    else:
        record_name = event['ResourceProperties']['RecordName']
        record_value = event['ResourceProperties']['RecordValue']
        record_type = event['ResourceProperties']['RecordType']

    # Assume a role in the target account
    sts_client = boto3.client('sts')
    assumed_role = sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName=f'cdk-cross-account-record-demo'
    )
    print(f'assumed role {role_arn}')

    # Create a Route 53 client using the assumed role credentials
    route53_client = boto3.client(
        'route53',
        aws_access_key_id=assumed_role['Credentials']['AccessKeyId'],
        aws_secret_access_key=assumed_role['Credentials']['SecretAccessKey'],
        aws_session_token=assumed_role['Credentials']['SessionToken']
    )

    record = {}
    if certificate_flag:
        record = {
                    'Name': record_name,
                    'Type': 'CNAME',
                    'TTL': record_ttl,
                    'ResourceRecords': [{'Value': record_value}]
                }
    elif alias_flag:
        record = {
                    'Name': record_name,
                    'Type': 'A',
                    'AliasTarget': {
                        'HostedZoneId': aws_hosted_zone_id,
                        'DNSName': record_value,
                        'EvaluateTargetHealth': False
                    }
                }
    else:
        record = {
                    'Name': record_name,
                    'Type': record_type,
                    'ResourceRecords': [{'Value': record_value}]
                }
    print(record)

    # Create the Route 53 record in the target account
    response = route53_client.change_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        ChangeBatch={
            'Changes': [{
                'Action': 'UPSERT',
                'ResourceRecordSet': record
            }]
        }
    )
    print(f'record response: {response}')

    if certificate_flag:
        return {
            'PhysicalResourceId': record_name.replace(".", ""),
            'Data': {
                'CertificateArn': new_certificate['CertificateArn'],
            }
        }
    else:
        return {
            'PhysicalResourceId': record_name.replace(".", "")
        }


def on_delete(event):
    print('Event Type: Delete')
    role_arn = event['ResourceProperties']['TargetAccountRole']
    hosted_zone_id = event['ResourceProperties']['HostedZoneId']
    certificate_flag = bool(event['ResourceProperties'].get('Certificate', False))
    alias_flag = bool(event['ResourceProperties'].get('Alias', False))

    record_name = None
    record_value = None
    record_ttl = None
    domain_name = None
    cert_name = None
    new_certificate = None
    record_type = None
    aws_hosted_zone_id = None

    if certificate_flag:
        cert_name = event['ResourceProperties']['CertName']
        record_ttl = int(event['ResourceProperties']['RecordTTL'])
        acm_client = boto3.client('acm')
        list_certifcates = acm_client.list_certificates()

        for certificate in list_certifcates['CertificateSummaryList']:
            if certificate['DomainName'] == cert_name:
                print(f'deleting certificate {certificate["CertificateArn"]}')
                time.sleep(10)
                describe_certificate = acm_client.describe_certificate(
                    CertificateArn=certificate['CertificateArn']
                )
                record_name = describe_certificate['Certificate']['DomainValidationOptions'][0]['ResourceRecord']['Name']
                record_value = describe_certificate['Certificate']['DomainValidationOptions'][0]['ResourceRecord']['Value']
                acm_client.delete_certificate(
                    CertificateArn=certificate['CertificateArn']
                )
                print(f'deleted certificate {certificate["DomainName"]}')
    elif alias_flag:
        aws_hosted_zone_id = event['ResourceProperties']['AwsHostedZoneId']
        record_name = event['ResourceProperties']['RecordName']
        record_value = event['ResourceProperties']['RecordValue']
    else:
        record_name = event['ResourceProperties']['RecordName']
        record_value = event['ResourceProperties']['RecordValue']
        record_type = event['ResourceProperties']['RecordType']


    # Assume a role in the target account
    sts_client = boto3.client('sts')
    assumed_role = sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName=f'cdk-cross-account-record-demo'
    )
    print(f'assumed role {role_arn}')

    # Create a Route 53 client using the assumed role credentials
    route53_client = boto3.client(
        'route53',
        aws_access_key_id=assumed_role['Credentials']['AccessKeyId'],
        aws_secret_access_key=assumed_role['Credentials']['SecretAccessKey'],
        aws_session_token=assumed_role['Credentials']['SessionToken']
    )

    if certificate_flag:
        record = {
                    'Name': record_name,
                    'Type': 'CNAME',
                    'TTL': record_ttl,
                    'ResourceRecords': [{'Value': record_value}]
                }

    elif alias_flag:
        record = {
                    'Name': record_name,
                    'Type': 'A',
                    'AliasTarget': {
                        'HostedZoneId': aws_hosted_zone_id,
                        'DNSName': record_value,
                        'EvaluateTargetHealth': False
                    }
                }
    else:
        record = {
                    'Name': record_name,
                    'Type': record_type,
                    'ResourceRecords': [{'Value': record_value}]
                }
    print(record)

    # Create the Route 53 record in the target account
    response = route53_client.change_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        ChangeBatch={
            'Changes': [{
                'Action': 'DELETE',
                'ResourceRecordSet': record
            }]
        }
    )
    print(f'record response: {response}')

    return {
        'PhysicalResourceId': event['PhysicalResourceId']
    }

