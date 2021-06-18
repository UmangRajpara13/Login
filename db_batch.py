import boto3
from botocore.config import Config

my_config = Config(

    region_name = 'eu-central-1',
)

client = boto3.client('dynamodb', config=my_config, aws_access_key_id = 'aws_access_key_id',
    aws_secret_access_key = 'aws_secret_access_key')

response = client.get_item(
    TableName='users',
    Key={
        'email': {
            'S': 'user@live.com',
        }
    },
    AttributesToGet=[
        'MAC', 'Validity', 'password'
    ],
    ConsistentRead=False,
    ReturnConsumedCapacity='NONE'
)

# response = client.describe_table(
#     TableName='users'
# )

print(response)
