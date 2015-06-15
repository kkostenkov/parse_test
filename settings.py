import os
import socket
#SEARCHPATH = "C:\xxx"
SEARCHPATH = 'C:\Program Files'
DB_NAME = "windir.db"
# local IP with underscores
TABLE_NAME = str(socket.gethostbyname(socket.gethostname())).replace(".", "_")
DB_LOGIN = 'bdadmin'
DB_PASS = 'testpass'
DB_IP = "localhost"
DB_PORT = "3306"
EXTENTION_TO_FIND = "exe"
CLEAR_TABLE_BEFORE_WORK = True
ALLOWED_APP_RUNTIME = 5 # seconds
DB_WATCHDOG_TIME = 5 # seconds
TESTING_THREADS_ALLOWED = 10
MAIL_SERV = "smtp.bbb.com"
MAIL_PORT = 443
MAIL_LOGIN = "login1"
MAIL_PASS = "password1"
MAIL_TO = ["aaa@bbb.xxx",] #list of addresses


if DB_NAME[-3:] == ".db":
    DB_NAME = DB_NAME[:-3]

CONN_SETTINGS = {"host":DB_IP,
            "port":DB_PORT,
            "user":DB_LOGIN,
            "pass":DB_PASS,
            "database":DB_NAME,
            "table_name":TABLE_NAME}

MAIL_SETTINGS = {"server":MAIL_SERV,
                 "port":MAIL_PORT,
                 "login":MAIL_LOGIN,
                 "password":MAIL_PASS,
                 "address":MAIL_TO,
                 }
