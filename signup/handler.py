from handler import jwt_authentication
from handler import conn,JWT_SECRET,DEFAULT_LIMIT,DEFAULT_OFFSET,json,jwt


def signup(event, context):

    body = json.loads(event['body'])
    name = body['name']
    email = body['email']
    password = body['password']

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    if user is not None:
        return {'body': 'Email already exists'}

    cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
    conn.commit()

    cursor.execute("INSERT INTO user_table (\"user\", message) VALUES (%s, %s)", (name, 'You are signed in successfully'))
    conn.commit()

    token = jwt.encode({'email': email}, 'Pushkar', algorithm='HS256')

    response = {
        "statusCode": 200,
        "body": json.dumps({
            'message': 'user created successfully',
            'data': {
                'name': name,
                'email': email,
                'token': token
            }
        })
    }

    return response