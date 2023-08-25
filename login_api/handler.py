from handler import jwt_authentication
from handler import conn,JWT_SECRET,DEFAULT_LIMIT,DEFAULT_OFFSET,json,jwt


@jwt_authentication
def login(event, context, decoded_token):
    email = decoded_token['email']

    body = json.loads(event['body'])
    password = body['password']
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    if user is None:
        return {'body': 'Email not found'}
    
    if password != user[3]:
        return {'body': 'Incorrect password'}

    token = jwt.encode({'email': email}, 'Pushkar', algorithm='HS256')

    show_messages = False
    if event.get('queryStringParameters') and 'show_messages' in event['queryStringParameters'] and event['queryStringParameters']['show_messages'] == 'true':
        show_messages = True

    messages = []
    if show_messages:
        cursor.execute("SELECT message FROM user_table WHERE \"user\" = %s", (user[1],))
        messages = cursor.fetchall()
    
    response = {
        "statusCode": 200,
        "body": json.dumps({
            'message': 'user authenticated successfully',
            'data': {
                'name': user[1],
                'email': user[2],
                'token': token,
                'messages': messages
            }
        })
    }

    return response