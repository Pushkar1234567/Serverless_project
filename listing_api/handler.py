from handler import jwt_authentication
from handler import conn,JWT_SECRET,DEFAULT_LIMIT,DEFAULT_OFFSET,json

@jwt_authentication
def listing(event, context, decoded_token):

    cursor = conn.cursor()

    # Get the limit and offset from the query string parameters
    limit = int(event['queryStringParameters'].get('limit', DEFAULT_LIMIT))
    offset = int(event['queryStringParameters'].get('offset', DEFAULT_OFFSET))

    # Get the search_by and search_term from the query string parameters
    search_by = event['queryStringParameters'].get('search_by')
    print("Your search_by is ",search_by)
    search_term = event['queryStringParameters'].get('search_term')

    if search_term is not None:
        cursor.execute('SELECT * FROM users WHERE name LIKE %s OR email LIKE %s',('%' + search_term + '%','%' + search_term + '%'))
    if search_by == 'name':
        cursor.execute("SELECT * FROM users ORDER BY name ASC LIMIT %s OFFSET %s",(limit, offset))        
    if search_by == 'id':
        cursor.execute("SELECT * FROM users ORDER BY id ASC LIMIT %s OFFSET %s",(limit, offset))
        try:
            a=cursor.fetchall()
            if a is not None:
                print(a)
            else:
                print("quarry is not executed")
        except Exception as e:
            print(e)
    elif search_by is not None:
        return {"statusCode": 400, "body": "You have two options either pass name or id in the parameters"}
    else:
        cursor.execute('SELECT * FROM users LIMIT %s OFFSET %s', (limit, offset))

    try:
        cursor.execute('SELECT name FROM users WHERE email = %s', (decoded_token['email'],))
        user_name = cursor.fetchone()[0]
        print(user_name)
        print("Your user_name is ",user_name)
    except Exception as e:
        print(e)

    # Join the users and notify tables to get the is_accepted value
    cursor.execute('SELECT u.id, u.name, u.email, n.is_accepted FROM users u LEFT JOIN notify n ON (u.name = n.sender AND n.receiver = %s) OR (u.name = n.receiver AND n.sender = %s) WHERE u.email <> %s', (user_name, user_name, decoded_token['email']))
    
    entries=[]
    for row in cursor.fetchall():
        entry = {
            'id': row[0],
            'name': row[1],
            'email': row[2],
            'is_friend': False
        }

        if row[3] is not None:
            entry['is_friend'] = row[3]
        
        entries.append(entry)
        

    cursor.close
    conn.close

    response = {
        'statusCode': 200,
        'body': json.dumps(entries)
    }
    return response


    # cursor = conn.cursor()

    # if event['queryStringParameters']:
    #     limit = int(event['queryStringParameters'].get('limit', DEFAULT_LIMIT))
    #     offset = int(event['queryStringParameters'].get('offset', DEFAULT_OFFSET))
    # else:
    #     limit = DEFAULT_LIMIT
    #     offset = DEFAULT_OFFSET

    # search_by = event['queryStringParameters'].get('search_by')
    # print("value of search by is ",search_by)
    # if search_by is not None and search_by not in ['name', 'id']:
    #     return {"statusCode": 400, "body": "Invalid search_by parameter. You can only search by 'name' or 'id'."}
    # search_term = event['queryStringParameters'].get('search_term')

    # if search_term is not None:
    #     cursor.execute('SELECT * FROM users WHERE name LIKE %s OR email LIKE %s',('%' + search_term + '%','%' + search_term + '%'))
    # if search_by == 'name':
    #     cursor.execute("SELECT id, name, email FROM users ORDER BY name ASC LIMIT %s OFFSET %s",(limit, offset))        
    # elif search_by == 'id':
    #     try:
    #         cursor.execute("SELECT id, name, email FROM users ORDER BY id ASC LIMIT %s OFFSET %s",(limit, offset))
    #         print("id quary is executing")
    #     except Exception as e:
    #         print(e)
    # else:
    #     cursor.execute('SELECT * FROM users LIMIT %s OFFSET %s', (limit, offset))

    # # if event.get('queryStringParameters') is not None:
    # #     search_by = event['queryStringParameters'].get('search_by')
    # # else:
    # #     search_by = None
    
    # # my_array = ['name', 'id']

    # # if event.get('queryStringParameters') is not None:
    # #     search_term = event['queryStringParameters'].get('search_term')
    # # else:
    # #     search_term = None

    # # if search_term is not None:
    # #     cursor.execute('SELECT * FROM users WHERE name LIKE %s OR email LIKE %s',('%' + search_term + '%','%' + search_term + '%'))
    # # elif search_by is not None:
    # #     if search_by == my_array[0]:
    # #         cursor.execute("SELECT id, name, email FROM users ORDER BY name ASC LIMIT %s OFFSET %s",(limit, offset))        
    # #     elif search_by == my_array[1]:
    # #         cursor.execute("SELECT id, name, email FROM users ORDER BY id ASC LIMIT %s OFFSET %s",(limit, offset))
    # #     else:
    # #         return {"statusCode": 400, "body": "You have two options either pass name or id in the parameters"}
    # # else:
    # #     cursor.execute('SELECT * FROM users LIMIT %s OFFSET %s', (limit, offset))

    # try:
    #     cursor.execute('SELECT name FROM users WHERE email = %s', (decoded_token['email'],))
    #     user_name = cursor.fetchone()[0]
    #     print(user_name)
        
    #     # print("Your user_name is ",user_name)
    # except Exception as e:
    #     print(e)

    # # print("Your decode token is",decoded_token['email'])
    # entries=[]
    # cursor.execute('SELECT id, name, email FROM users')
    # for row in cursor.fetchall():
    #     entry = {
    #         'id': row[0],
    #         'name': row[1],
    #         'email': row[2],
    #         'is_friend': False
    #     }

    #     # Checking if the user has any friends
    #     try:
    #         cursor.execute('SELECT is_accepted FROM notify WHERE (sender = %s AND receiver = %s) OR (sender = %s AND receiver = %s) AND is_accepted = true', (str(user_name), row[1], row[1], str(user_name)))
    #         friend_row = cursor.fetchone()
    #         # print("Your friend row is",friend_row,"sender",user_name," ",row[1])
            
    #     except Exception as e:
    #         print(e)
    #     if friend_row is not None:
    #         entry['is_friend'] = friend_row[0]
    #     entries.append(entry)
        

    # cursor.close
    # conn.close

    # response = {
    #     'statusCode': 200,
    #     'body': json.dumps(entries)
    # }
    # return response
