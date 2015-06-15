import mysql.connector
from mysql.connector import Error
from settings import CLEAR_TABLE_BEFORE_WORK

def connect(connection_data):
    db_ip = connection_data["host"]
    db_port = connection_data["port"]
    db_login = connection_data["user"]
    db_pass = connection_data["pass"]
    db_name  = connection_data["database"]
    try:
        connection = mysql.connector.connect(host = db_ip,
                                      port=db_port,
                                       user = db_login,
                                       password = db_pass,
                                       charset = 'utf8')
        if not connection.is_connected():
            print('Connection failed\n')
            return None
        #print('Connected to MySQL server\n')
    except mysql.connector.Error as err:
        print(err)
        return None
    try:
        connection.database = db_name
        return connection
    except mysql.connector.Error as err:
        if err.errno == 1049: #errorcode.ER_BAD_DB_ERROR:
            _create_database(cursor, db_name)
            connection.database = db_name
            return connection
        else:
            print(err)
            return None

def prepare(connection, db_name, table_name):
    '''Create database and table.'''
    cursor = connection.cursor()
    #  Creating table
    try:
        print("Preparing table: ", table_name)

        command = (
        "CREATE TABLE IF NOT EXISTS " + table_name +
        "(" +
        " id SERIAL," +
        " path varchar(150) NOT NULL," +
        " md5 varchar(32) NOT NULL," +
        " size_of_file int NOT NULL," +
        " type_of_file varchar(10) NOT NULL," +
        " description varchar(150)" +
        ")"
        )
        cursor.execute(command)
        connection.commit()

        if CLEAR_TABLE_BEFORE_WORK:
            print("Table cleared\n")
            command = ("TRUNCATE TABLE " + table_name)
            cursor.execute(command)
            connection.commit()
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.\n")
        else:
            print(err.msg)
    else:
        print("OK\n")
    cursor.close()

def _create_database(cursor, db_name):
    try:
        cursor.execute(
            "CREATE DATABASE " + db_name + " DEFAULT CHARACTER SET 'utf8'")
        connection.commit()
    except mysql.connector.Error as err:
        print("Failed creating database: {}\n".format(err))
        exit(1)

def upload_file_info(connection, table_name, file_info):
    cursor = connection.cursor()
    query = "INSERT INTO " + table_name + \
    "(path, md5, size_of_file, type_of_file, description)" + \
    " VALUES(%s,%s,%s,%s,%s)"
    args = (file_info["path"], file_info["md5"], file_info["size"], \
        file_info["type"], file_info["description"], )
    cursor.execute(query, args)
    connection.commit()
    cursor.close()

def upload_tree(connection, table_name, logged_tree):
    print("writing tree to " + table_name + "\n")
    i = 0
    for file_info in logged_tree:
        upload_file_info(connection, table_name, file_info)
        i += 1
    print (i, "files written\n")

def fetch_next_file(connection, table_name, file_extention):
    '''Get file from databse that suits !hardcoded! requirements.
    All rows in database with same md5 will be updated (description).'''
    cursor = connection.cursor()
    query = (" \
    SET @max_size = (SELECT MAX(`size_of_file`) FROM `" + table_name + \
    "` WHERE `type_of_file` = '" + file_extention + \
    "' AND `description` = '' LIMIT 1); \
    \
    SET @max_md5 = (SELECT `md5` FROM `" + table_name + \
    "` WHERE `size_of_file` = @max_size AND `type_of_file` = '" + \
    file_extention + "' LIMIT 1); \
    \
    UPDATE `" + table_name + "` SET description = 'file is being tested now' \
    WHERE md5 = @max_md5; \
    \
    SELECT path, md5, size_of_file, description FROM `" + table_name  + \
    "` WHERE md5 = @max_md5 AND `type_of_file` = '" + file_extention + \
    "' LIMIT 1; \
    ")
    file_to_find = {}
    try:
        for result in cursor.execute(query, multi = True):
            for path, md5, size_of_file, description in cursor:
                #print(path, md5, size_of_file)
                file_to_find["path"] = path
                file_to_find["md5"] = md5
                file_to_find["size_of_file"] = size_of_file
                file_to_find["description"] = description
    except mysql.connector.Error as err:
        if err.errno == 1213: #  Deadlock
            #print("Deadlock avoided\n")
            # In case of Deadlock when fetching - drop thread
            #and try to reconnect
            cursor.close()
            return []
        else:
            print(err)
            exit(1)
    cursor.close()
    return file_to_find

def report_button(connection, table_name, md5, button_name):
    '''Drive info about found buttonname to database.'''
    cursor = connection.cursor()
    query = (" \
    UPDATE `" + table_name + "` SET description = '" + button_name + \
    "' WHERE md5 = '" + md5 + "'; \
    ")
    try:
        cursor.execute(query)
    except mysql.connector.Error as err:
        if err.errno == 1213: #  Deadlock
            #print("Deadlock avoided\n")
            cursor.close()
            return False
        else:
            print(err)
            exit(1)
    connection.commit()
    cursor.close()
    return True

def get_total_size(connection, table_name, file_extention):
    '''Calculates total size of files with provided extention in bytes.
    File copies are concantenated.'''
    cursor = connection.cursor()
    query = ("SELECT size_of_file" + \
    " FROM " + table_name  + \
    " WHERE type_of_file = " + "'" + file_extention + "'"
    )
    cursor.execute(query)
    total_size = 0
    for size_of_file in cursor:
        #print (size_of_file)
        total_size += size_of_file[0]
    cursor.close()
    return total_size

def check_test_completion(connection_data, file_extention):
    '''Returns True if database have no unchecked files
    with provided extention.'''
    db_name = connection_data["database"]
    table_name = connection_data["table_name"]
    connection = connect(connection_data)
    cursor = connection.cursor()
    query = ("SELECT id" + \
    " FROM " + table_name  + \
    " WHERE type_of_file = " + "'" + file_extention + "'" + \
    " AND description = ''"
    )
    cursor.execute(query)
    untested_files = []
    for file_id in cursor:
        untested_files.append(file_id[0])
    #print(untested_files)
    cursor.close()
    return len(untested_files) == 0
