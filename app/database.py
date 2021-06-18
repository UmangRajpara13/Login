import boto3
from boto3.dynamodb.conditions import Key

class database:
    def __init__(self):
        dynamodb = boto3.resource(service_name='dynamodb', region_name='eu-central-1')
        self.table = dynamodb.Table('users')

    def query_email(self, email):

        response = self.table.query(
            KeyConditionExpression=Key('email').eq(email)
        )
        items = response['Items']
        if not items:
            return False
        else:
            return True

    def register(self, email):

        self.table.put_item(
            Item={
                'email': email,
                'Validity': 'None',
                'MAC': '000',
            }
        )

    def fetch_user(self, email):
        response = self.table.get_item(
            Key={
                'email': email,
            }
        )
        item = response['Item']
        return item

    def get_password_hash(self, email):
        response = self.table.get_item(
            Key={
                'email': email,
            }
        )
        item = response['Item']
        return item.get('password')

