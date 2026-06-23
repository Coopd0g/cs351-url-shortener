import json
import boto3
import random
import string
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('TABLE_NAME', 'url-shortener')
BASE_URL = os.environ.get('BASE_URL', 'https://YOUR_API_ID.execute-api.us-east-2.amazonaws.com/prod')

def generate_code(length=6):
    """Generate a random alphanumeric short code."""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))

def lambda_handler(event, context):
    """
    POST /shorten
    Body: { "url": "https://example.com/very/long/url" }
    Returns: { "short_url": "https://.../AbCd1Z", "code": "AbCd1Z" }
    """
    try:
        body = json.loads(event.get('body', '{}'))
        long_url = body.get('url', '').strip()

        if not long_url:
            return {
                'statusCode': 400,
                'headers': cors_headers(),
                'body': json.dumps({'error': 'Missing required field: url'})
            }

        if not long_url.startswith(('http://', 'https://')):
            return {
                'statusCode': 400,
                'headers': cors_headers(),
                'body': json.dumps({'error': 'URL must start with http:// or https://'})
            }

        table = dynamodb.Table(TABLE_NAME)

        # Ensure the code is unique (collision is unlikely but checked)
        code = generate_code()
        for _ in range(5):
            response = table.get_item(Key={'short_code': code})
            if 'Item' not in response:
                break
            code = generate_code()

        table.put_item(Item={
            'short_code': code,
            'long_url': long_url,
            'created_at': datetime.utcnow().isoformat(),
            'click_count': 0
        })

        short_url = f"{BASE_URL}/{code}"
        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps({
                'short_url': short_url,
                'code': code,
                'original_url': long_url
            })
        }

    except Exception as e:
        print(f"Error in shorten: {e}")
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': 'Internal server error'})
        }

def cors_headers():
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS'
    }
