import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    # Specify the AWS services you want to check for tags
    services_to_check = ['ec2', 'rds', 's3']

    # Specify the SNS topic ARN where you want to send the notification
    sns_topic_arn = 'arn:aws:sns:us-east-1:750529513992:Tagged_Untagged_Notification'

    untagged_resources = []

    for service in services_to_check:
        client = boto3.client(service)

        if service == 's3':
            response = client.list_buckets()

            for bucket in response['Buckets']:
                try:
                    bucket_tags = client.get_bucket_tagging(Bucket=bucket['Name']).get('TagSet')

                    if not bucket_tags:
                        untagged_resources.append(f"S3 Bucket: {bucket['Name']}")
                except ClientError as e:
                    if e.response['Error']['Code'] == 'NoSuchTagSet':
                        untagged_resources.append(f"S3 Bucket: {bucket['Name']}")

        elif service == 'rds':
            response = client.describe_db_instances()

            for instance in response['DBInstances']:
                instance_tags = instance.get('TagList')

                if not instance_tags:
                    untagged_resources.append(f"RDS Instance: {instance['DBInstanceIdentifier']}")

        elif service == 'ec2':
            response = client.describe_instances()

            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instance_tags = instance.get('Tags')

                    if not instance_tags:
                        untagged_resources.append(f"EC2 Instance: {instance['InstanceId']}")

    if untagged_resources:
        sns_client = boto3.client('sns')
        message = "Improperly tagged or untagged resources found:\n\n" + "\n".join(untagged_resources)
        sns_client.publish(TopicArn=sns_topic_arn, Message=message)
