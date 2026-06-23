import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('TABLE_NAME', 'url-shortener')

def lambda_handler(event, context):
    """
    GET /{code}
    Looks up the short code in DynamoDB and returns a 301 redirect.
    """
    try:
        code = event.get('pathParameters', {}).get('code', '').strip()

        if not code:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing short code'})
            }

        table = dynamodb.Table(TABLE_NAME)
        response = table.get_item(Key={'short_code': code})

        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': f'Short code not found: {code}'})
            }

        long_url = response['Item']['long_url']

        # Increment click count (fire-and-forget; don't fail if this errors)
        try:
            table.update_item(
                Key={'short_code': code},
                UpdateExpression='SET click_count = click_count + :val',
                ExpressionAttributeValues={':val': 1}
            )
        except Exception:
            pass

        return {
            'statusCode': 301,
            'headers': {
                'Location': long_url,
                'Cache-Control': 'no-cache'
            },
            'body': ''
        }

    except Exception as e:
        print(f"Error in redirect: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }
