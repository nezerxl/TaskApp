import mysql.connector
import os
import time

def start():
    userCred.append(input('Enter SQL UserName: '))
    userCred.append(input('Enter SQL Passwd: '))
    cnxInit=mysql.connector.connect(
    host="localhost",
    user=userCred[0],
    password=userCred[1]
    )

    cursor = cnxInit.cursor()

    cursor.execute("SHOW DATABASES")
    databases = [database[0] for database in cursor]

    if "taskapp" not in databases:
        # Create the "taskapp" database if it doesn't exist
        cursor.execute("CREATE DATABASE taskapp")
        print("Created database: taskapp")

    # Switch to the "taskapp" database
    cursor.execute("USE taskapp")

    # Prompt for a username
    userCred.append(input("Enter a username: ")+'todo')

    global utable
    utable = userCred[2]

    # Check if the user table exists
    cursor.execute("SHOW TABLES")
    tables = [table[0] for table in cursor]

    if utable not in tables:
        # Create the user table if it doesn't exist
        create_table_query= f"""
        CREATE TABLE IF NOT EXISTS {utable}(
            Taskid INT PRIMARY KEY AUTO_INCREMENT,
            Name TEXT,
            Description TEXT,
            Status TEXT CHECK (Status IN ("Not Started", "In Progress", "Completed")),
            Priority TEXT CHECK (Priority IN ('1', '2', '3'))
        ) 
        """
        cursor.execute(create_table_query)
        cnxInit.close()
        print(f'Created table: {utable}')
        mainScreen()
        return
    else:
        mainScreen()
        return
    
def getData(table_name):
    flushTable()

    cnx = mysql.connector.connect(
        host="localhost",
        user=userCred[0],
        password=userCred[1],
        database='taskapp'
    )
    cursor=cnx.cursor()


    # Retrieve all rows from the table
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
    headers = [desc[0] for desc in cursor.description]

    # Create a nested list to store the data
    data = []
    for row in rows:
        row=list(row)
        row[0]=str(row[0])
        # Append each row as a list to the main data list
        data.append(list(row))

    cnx.close()

    return ((headers,data))

def prettyTable(headers, data):
    """
    Creates a pretty table using only built-in functions and libraries.
    
    Arguments:
    - headers: A list of strings representing the table headers.
    - data: A list of lists, where each inner list represents a row in the table.
    
    Returns:
    - A string containing the formatted table.
    """ 
    # Determine the maximum width of each column
    column_widths = [max(map(len, column)) for column in zip(headers, *data)]
    
    # Create the separator row
    separator = '+'.join('-' * (width + 2) for width in column_widths)
    separator = f'+{separator}+'
    
    # Create the header row
    header_row = '|'.join(f' {header:{width}} ' for header, width in zip(headers, column_widths))
    header_row = f'|{header_row}|'
    
    # Create the data rows
    data_rows = []
    for row in data:
        data_row = '|'.join(f' {item:{width}} ' for item, width in zip(row, column_widths))
        data_row = f'|{data_row}|'
        data_rows.append(data_row)
    
    # Combine the separator, header row, and data rows
    table = f'{separator}\n{header_row}\n{separator}\n' + '\n'.join(data_rows) + f'\n{separator}'
    
    return table

def mainScreen():
    clrscr()
    print('===TaskApp===\n')
    
    # Retrieve data
    table=prettyTable(getData(utable)[0],getData(utable)[1])
    
    print(f'{table}\n\n\n')

    # User Input
    print('Choose option: (a)dd task | (d)elete task | (u)pdate status | (e)xit')
    userOption=input('-> ')

    # Validating input and execution options
    if userOption not in ['a','d','u','e']:
        print('INVALID INPUT')
        time.sleep(0.75)
        mainScreen()
    elif userOption == 'a':
        addTask()
    elif userOption == 'd':
        delTask()
    elif userOption == 'u':
        updTask()
    elif userOption == 'e':
        print('GoodBye...')
        time.sleep(0.5)
        clrscr()
        exit()

def addTask():
    clrscr()
    print('===TaskApp===\n')
    print('Enter (e) to return to Mainscreen.\n\n\n')
    #User Input
    name=input('Enter TaskName: ')
    exitChk(name)
    desc=input('Enter Description: ')
    exitChk(desc)
    while True:
        status=input('Enter Status (N)ot Started, (I)n Progress, (C)ompleted: ')
        exitChk(status)
        if status not in('N','I','C'):
            print('Status Invalid Enter (N) or (I) or (C) only.')
            continue
        elif status=='N':
            status='Not Started'
            break
        elif status=='I':
            status='In Progress'
            break
        elif status=='C':
            status='Completed'
            break

    while True:
        priority=input('Enter Priority (1), (2), (3): ')
        exitChk(priority)
        if priority not in('1','2','3'):
            print('Priority Invalid Enter (1) or (2) or (3) only.')
            continue
        else:
            break
    
    addtaskQuery=f'''
    INSERT INTO {utable}(Name,Description,Status,Priority)
    VALUES ('{name}','{desc}','{status}','{priority}')'''


    cnx = mysql.connector.connect(
        host="localhost",
        user=userCred[0],
        password=userCred[1],
        database='taskapp'
    )

    cursor=cnx.cursor()
    cursor.execute(addtaskQuery)
    cnx.commit()
    cnx.close()
    print('Task Added Successfully\nReturning to Main Screen...')
    time.sleep(0.75)
    mainScreen()

def delTask():
    clrscr()
    print('===TaskApp===\n')
    print('Enter (e) to return to Mainscreen.\n\n\n')
    table=prettyTable(getData(utable)[0],getData(utable)[1])
    
    print(f'{table}\n\n\n')

    cnx = mysql.connector.connect(
        host="localhost",
        user=userCred[0],
        password=userCred[1],
        database='taskapp'
    )
    cursor=cnx.cursor()
    data=getData(utable)[1]
    taskIDList=[]
    for i in data:
        taskIDList.append((i[0]))
    
    while True:
        delTaskid=(input('Enter TaskId to delete: '))
        exitChk(delTaskid)
        if delTaskid not in taskIDList:
            print('\nTaskID NOT FOUND')
            print(f'Choose from: {taskIDList}\n')
            continue
        else:
            delQuery=f'''
            DELETE FROM {utable}
            WHERE Taskid={int(delTaskid)}
            '''
            cursor.execute(delQuery)
            cnx.commit()
            cnx.close()
            print('Task Deleted Successfully. Returning Home.')
            time.sleep(0.3)
            break

    mainScreen()

def updTask():
    clrscr()
    print('===TaskApp===\n')
    print('Enter (e) to return to Mainscreen.\n\n\n')
    table=prettyTable(getData(utable)[0],getData(utable)[1])
    
    print(f'{table}\n\n\n')

    cnx = mysql.connector.connect(
        host="localhost",
        user=userCred[0],
        password=userCred[1],
        database='taskapp'
    )
    cursor=cnx.cursor()

    data=getData(utable)[1]
    taskIDList=[]
    for i in data:
        taskIDList.append((i[0]))
    
    while True:
        updTaskid=(input('Enter TaskId to UPDATE: '))
        exitChk(updTaskid)
        if updTaskid not in taskIDList:
            print('\nTaskID NOT FOUND')
            print(f'Choose from: {taskIDList}\n')
            continue
        else:
            status=input('Enter NEW Status (N)ot Started, (I)n Progress, (C)ompleted: ')
            exitChk(status)
            if status not in('N','I','C'):
                print('Status Invalid Enter (N) or (I) or (C) only.')
                continue
            elif status=='N':
                status='Not Started'
                break
            elif status=='I':
                status='In Progress'
                break
            elif status=='C':
                status='Completed'
                break
    updTaskQuery=f'''
    UPDATE {utable}
    SET Status='{status}'
    WHERE taskID={int(updTaskid)};
    '''
    cursor.execute(updTaskQuery)
    cnx.commit()
    cnx.close()
    print('Task Updated. Returning Home.')
    time.sleep(0.25)
    mainScreen()

def clrscr():
    if os.name == 'posix':
      _ = os.system('clear')
    else:
      _ = os.system('cls')

def exitChk(userStr):
    if userStr=='e':
        mainScreen()
        return
    else:
        return

def flushTable():
    cnx = mysql.connector.connect(
        host="localhost",
        user=userCred[0],
        password=userCred[1],
        database='taskapp'
    )
    cursor=cnx.cursor()
    
    flushQuery=f'''
    ALTER TABLE {userCred[2]} AUTO_INCREMENT = 1
    SET @counter = 0
    UPDATE {userCred[2]} SET taskid = @counter:=@counter + 1
    'ALTER TABLE {userCred[2]} MODIFY Taskid INT AUTO_INCREMENT;
    '''
    cursor.execute(flushQuery)
    cursor.close()
    cnx.close()

#User Credentials: [userName,userPass,userTable]
userCred=[]

start()    