import mysql.connector
from mysql.connector import Error
import pandas as pd

def create_server_connection(host_name,user_name,user_password):
    connection = None
    try:
        connection = mysql.connector.connect(
            host= host_name,
            user  =user_name,
            passwd = user_password)
        print("MySql Database connection sucessfull")
    
    except Error as err:
        print(f'Error: '+ str(err))
    
    return connection

def create_database(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Database created sucessfully")
    except Error as err:
        print("Error: " + str(err))

def create_db_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host = host_name,
            user = user_name,
            passwd = user_password,
            database = db_name
        )
        print("Mysql database connection sucessfull")
    except Error as e:
        print("Error: " + str(e))    
    return connection

def execute_query(connection, qurey):
    cursor = connection.cursor()
    try:
        cursor.execute(qurey)
        connection.commit()
        print("Query was sucessful")
    except Error as e:
        print("Error: " + str(e))    
    


    

pw = 'pratham@123'
db = 'mysql_python'
connection = create_server_connection("127.0.0.1",'root',pw)


#create_database_qurey = 'Create database mysql_python'
#create_database(connection,create_database_qurey)


create_orders_table = '''
create table orders(
customer_name varchar(30) not null,
product_name varchar(20) not null,
date_ordered date,
quantity int,
unit_price float,
phone_number varchar(20)
);
'''
connection = create_db_connection("127.0.0.1",'root', pw, db) 
execute_query(connection, create_orders_table)






