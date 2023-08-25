import json
import psycopg2
from psycopg2 import sql
import json
import os
import jwt
from datetime import datetime, timedelta
from functools import wraps



JWT_SECRET = 'Pushkar'
DEFAULT_LIMIT = int(os.environ.get('DEFAULT_LIMIT', 2))
DEFAULT_OFFSET = int(os.environ.get('DEFAULT_OFFSET', 0))

conn = psycopg2.connect(
    host="localhost",
    port="5432",
    dbname="local",
    user="local",
    password="Saini150101"
)


def jwt_authentication(f):
    @wraps(f)
    def decorated_function(event, context):
        try:
            token = event['headers']['Authorization'].split(' ')[1]
            decoded_token = jwt.decode(token, 'Pushkar', algorithms=['HS256'])
            # print(token)
            # print(decoded_token)
            return f(event, context, decoded_token)
        except Exception as e:
            # print(e)
            return {"statusCode": 401, "body": "Invalid token"}

    return decorated_function

@jwt_authentication
def create(event, context,decoded_token):

    cursor = conn.cursor()
    body = json.loads(event['body'])
    name = body['name']
    email = body['email']
    try:
        cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s)", (name, email))
    except:
        return({'body':'user already exist'})
        # print(f"Cannot insert: {e}")
    conn.commit()
    # cursor.close()
    # conn.close()

    response = {
        "statusCode": 200,
        "body": json.dumps({
            'message' : 'user created successfully',
            'data' : {
                'name' :name,
                "email": email
            }
        })
    }

    return response

@jwt_authentication
def listing(event, context, decoded_token):

    cursor = conn.cursor()

    if event['queryStringParameters']:
        limit = int(event['queryStringParameters'].get('limit', DEFAULT_LIMIT))
        offset = int(event['queryStringParameters'].get('offset', DEFAULT_OFFSET))
    else:
        limit = DEFAULT_LIMIT
        offset = DEFAULT_OFFSET

    if event.get('queryStringParameters') is not None:
        search_by = event['queryStringParameters'].get('search_by')
    else:
        search_by = None
    
    my_array = ['name', 'id']

    if event.get('queryStringParameters') is not None:
        search_term = event['queryStringParameters'].get('search_term')
    else:
        search_term = None

    if search_term is not None:
        cursor.execute('SELECT * FROM users WHERE name LIKE %s OR email LIKE %s',('%' + search_term + '%','%' + search_term + '%'))
    elif search_by is not None:
        if search_by == my_array[0]:
            cursor.execute("SELECT id, name, email FROM users ORDER BY name ASC LIMIT %s OFFSET %s",(limit, offset))        
        elif search_by == my_array[1]:
            cursor.execute("SELECT id, name, email FROM users ORDER BY id ASC LIMIT %s OFFSET %s",(limit, offset))
        else:
            return {"statusCode": 400, "body": "You have two options either pass name or id in the parameters"}
    else:
        cursor.execute('SELECT * FROM users LIMIT %s OFFSET %s', (limit, offset))

    # print("Your decode token is",decoded_token['email'])
    entries=[]
    for row in cursor.fetchall():
        entry = {
            'id': row[0],
            'name': row[1],
            'email': row[2],
            'is_friend': False
        }

        # Checking if the user has any friends
        try:
            cursor.execute('SELECT name FROM users WHERE email = %s', (decoded_token['email'],))
            result= cursor.fetchone()
            user_name=result[0]
            # print("Your user_name is ",user_name)
        except Exception as e:
            print(e)
        try:
            cursor.execute('SELECT is_accepted FROM notify WHERE (sender = %s AND receiver = %s) OR (sender = %s AND receiver = %s) AND is_accepted = true', (str(user_name), row[1], row[1], str(user_name)))
            friend_row = cursor.fetchone()
            print("Your friend row is",friend_row,"sender",user_name," ",row[1])
            
        except Exception as e:
            print(e)
        if friend_row is not None:
            entry['is_friend'] = friend_row[0]
        entries.append(entry)
        

    cursor.close
    conn.close

    response = {
        'statusCode': 200,
        'body': json.dumps(entries)
    }
    return response

@jwt_authentication
def update(event,context,decoded_token):
    id=int(event['pathParameters']['id'])
    body=json.loads(event['body'])
    name=body['name']
    email=body['email']

    cursor=conn.cursor()
    cursor.execute("UPDATE users SET name = %s, email = %s WHERE id = %s", (name, email, id))
    conn.commit()
    # conn.close()
    # cursor.close()
    response = {
            'statusCode': 200,
            'body': json.dumps({
            'message' : 'data updated successfully',
            'data' : {
                'updated_name' :name,
                "updated_email": email
            }
        }),
        }
    return response

@jwt_authentication
def retrieve(event,context,decoded_token):
    id=int(event['pathParameters']['id'])
    cursor=conn.cursor()
    cursor.execute('SELECT name,email FROM users WHERE id=%s',(id,))
    row = cursor.fetchone()
    response={}
    
    if row is not None:
        response={
            "statusCode":200,
            "body":json.dumps({
                'name': row[0],
                'email': row[1]
            })
        }
    else:
        return ("User not found")
    return response

@jwt_authentication
def delete(event,context,decoded_token):
    id=int(event['pathParameters']['id'])
    cursor=conn.cursor()
    cursor.execute('SELECT id FROM users WHERE id=%s',(id,))
    row=cursor.fetchone()
    try:
        if row is not None:
            cursor.execute('DELETE FROM users WHERE id=%s',(id,))  
            conn.commit()
            response={
                "statuscode":200,
                'body':json.dumps({
                    'id':id,
                    'message':'user deleted successfully'
                })
            }
        else:
            return ("User Not Found")
    except Exception as e:
        print({e})
    return response



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
                'messages': messages,
                'token': token
            }
        })
    }

    return response



@jwt_authentication
def friend_request_send(event, context,decoded_token):
    body = json.loads(event['body'])
    sender = body['sender']
    receiver = body['receiver']
    print(sender)
    print(receiver)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM notify WHERE sender = %s AND receiver = %s AND is_pending = %s", (sender, receiver, True))
        row = cursor.fetchone()
        if row[0] > 0:
            # Friend request already exists
            response = {
                "statusCode": 400,
                "body": json.dumps({
                    'message': 'You already sent a friend request to this user'
                })
            }
            return response
        cursor.execute("INSERT INTO notify (sender, receiver, is_pending, is_accepted, is_rejected) VALUES (%s, %s, %s, %s, %s)", (sender, receiver, True, False, False))
        conn.commit()
        print("Entry is going.")
        try:
            cursor.execute("INSERT INTO user_table (\"user\", message) VALUES (%s, %s)", (sender, 'Friend request sent to ' + receiver))
            conn.commit()
        except Exception as E:
            print (E)
    except Exception as E:
        print(E)
    response = {
        "statusCode": 200,
        "body": json.dumps({
            'message': 'friend request sent successfully'
        })
    }
    return response
    
@jwt_authentication
def friend_request_accept(event, context,decoded_token):
    body = json.loads(event['body'])
    sender = body['sender']
    receiver = body['receiver']
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM notify WHERE sender = %s AND receiver = %s AND is_accepted = %s", (sender, receiver, True))
        row = cursor.fetchone()
        if row[0] > 0:
            # Friend request already exists
            response = {
                "statusCode": 400,
                "body": json.dumps({
                    'message': 'You already accepted a friend request to this user'
                })
            }
            return response
        cursor.execute("UPDATE notify SET is_accepted = %s, is_rejected = %s, is_pending = %s WHERE sender = %s AND receiver = %s", (True, False, False, sender, receiver))
        conn.commit()
        cursor.execute("INSERT INTO user_table (\"user\", message) VALUES (%s, %s)", (receiver, 'Friend request accepted from ' + sender))
        conn.commit()
    except:
        print("not working")
    response = {
        "statusCode": 200,
        "body": json.dumps({
            'message': 'friend request accepted'
        })
    }
    return response

@jwt_authentication
def friend_request_rejected(events,context,decoded_token):
    body=json.loads(events['body'])
    sender=body['sender']
    receiver=body['receiver']
    cursor=conn.cursor()
    cursor.execute("UPDATE notify SET is_rejected=%s, is_accepted=%s, is_pending=%s WHERE sender=%s AND receiver=%s",(True,False,False,sender,receiver))
    conn.commit()
    cursor.execute("INSERT INTO user_table (\"user\",message) VALUES (%s,%s)",(receiver, 'Friend request rejected from ' + sender))
    conn.commit()
    response = {
        "statusCode": 200,
        "body": json.dumps({
            'message': 'friend request rejected'
        })
    }
    return response

@jwt_authentication
def friend_remove(events,context,decode_token):
    cursor = conn.cursor()
    body = json.loads(events['body'])
    sender = body['sender']
    receiver = body['receiver']
    print(decode_token)
    cursor.execute("SELECT name FROM users WHERE email=%s",(decode_token['email'],))
    user_name = cursor.fetchone()[0]
    print(user_name)
    try:
        cursor.execute("SELECT is_accepted FROM notify WHERE ((sender=%s and receiver=%s) OR (sender=%s and receiver=%s)) AND is_accepted=True",(user_name,receiver,receiver,user_name))
        result = cursor.fetchone()
        if result is None:
            return {"statusCode": 404, "body": "No accepted friend request found"}
        cursor.execute("UPDATE notify SET is_accepted = false WHERE ((sender=%s and receiver=%s) OR (sender=%s and receiver=%s)) AND is_accepted=True",(user_name, receiver, receiver,user_name))
        conn.commit()
        try:
            cursor.execute("UPDATE users SET is_friend = false WHERE name=%s RETURNING *", (receiver,))
            updated_row = cursor.fetchone()
            if updated_row is not None:
                print("Updated row:", updated_row)
                conn.commit()
            else:
                print("No row updated")
        except Exception as e:
            print(e)  
        return {"statusCode": 200, "body": "Friend removed successfully"}
    except Exception as e:
        print(e)
        return {"statusCode": 500, "body": "An error occurred while removing friend"} 
    # cursor.execute('SELECT name FROM users WHERE email = %s', (decode_token['email'],))
    # user_name = cursor.fetchone()
    # sender=user_name
    # receiver = body['receiver']
    # cursor.execute('SELECT email FROM users WHERE name = %s', (receiver,))
    # receiver_result = cursor.fetchone()
    # if receiver_result is None:
    #     return {"statusCode": 400, "body": "Invalid receiver name"}
    # try:
    #     cursor.execute('UPDATE users SET is_friend = false WHERE (name = %s AND email = %s) OR (name = %s AND email = %s)',
    #                     (sender, receiver_result[0], receiver, decode_token['email']))
    #     cursor.execute('UPDATE notify SET is_accepted = false WHERE (sender = %s AND receiver = %s) OR (sender = %s AND receiver = %s) AND is_accepted = true',
    #                     (decode_token['email'], receiver_result[0], receiver, decode_token['email']))
    #     conn.commit()
    #     return {"statusCode": 200, "body": "Friend is removed successfully"}
    # except Exception as e:
    #     print(e)


