In this project there are two main files
1. serverless.yml file
2. handler.py file

Serverless.yml file :-

        The serverless.yml file is used to specify the configuration for your Serverless function, such as the runtime, plugins, and function handlers. It is written in YAML format and describes the functions and their HTTP events.

    --I have defined five functions in the serverless.yml
    --I have also specified the HTTP event for each function, including the  HTTP method and path.
    --Finally, i have included two plugins in the serverless.yml file:          
        (a): serverless-python-requirements 
        (b): serverless-offline
            
            (a): The serverless-python-requirements plugin is used to install   any required Python modules for my function.
            
            (b): serverless-offline plugin is used to test my function locally


handler.py file:-

    - The function is using psycopg2 module to interact with a PostgreSQL database.
    - It has five Lambda function handlers create, listing, update, retrieve and delete, each corresponding to a different HTTP method, and each performing a different database operation.

    Operations:
        (1). The create function handler is for the HTTP POST method and inserts a new user record into the users table in the PostgreSQL database.

        (2). The listing function handler is for the HTTP GET method and returns all user records from the users table.

        (3). The update function handler is for the HTTP PUT method and updates an existing user record in the users table.

        (4). The retrieve function handler is for the HTTP GET method and retrieves a user record by its id from the users table.

        (5). The delete function handler is for the HTTP DELETE method and deletes a user record by its id from the users table.


Note:

A variable is defined inside handler.py named as "conn"
In summary, the conn variable is a global variable that holds the connection object to the PostgreSQL database, allowing the functions in the handler.py file to interact with the database.