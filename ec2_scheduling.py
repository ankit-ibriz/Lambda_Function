import boto3

def lambda_handler(event, context):
    
    ec2_client = boto3.client('ec2')

    instances = get_instances_by_tag(ec2_client, 'Environment', 'Test')

    if event.get('detail-type') == 'Scheduled Event':
        action = event.get('action')

        if action == 'START':
            start_instances(ec2_client, instances)
        elif action == 'STOP':
            stop_instances(ec2_client, instances)

def get_instances_by_tag(ec2_client, tag_key, tag_value):
    response = ec2_client.describe_instances(
        Filters=[
            {
                'Name': f'tag:{tag_key}',
                'Values': [tag_value]
            }
        ]
    )

    instances = []

    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instances.append(instance['InstanceId'])

    return instances

def start_instances(ec2_client, instances):
    response = ec2_client.start_instances(InstanceIds=instances)
    print(f'Starting instances: {response["StartingInstances"]}')

def stop_instances(ec2_client, instances):
    response = ec2_client.stop_instances(InstanceIds=instances)
    print(f'Stopping instances: {response["StoppingInstances"]}')
