import os
import psycopg2
from dotenv import load_dotenv
load_dotenv()

hostname = os.getenv('HOSTNAME')
database = os.getenv('DATABASE')
pg_user = os.getenv('PG_USER')
pg_password = os.getenv('PG_PASSWORD')
port_id = os.getenv('PORT_ID')

# def connect():
#     if conn is None:
#         try:
#             conn=psycopg2.connect(
#                 host=hostname,
#                 database=database,
#                 user=pg_user,
#                 password=pg_password,
#                 port=port_id
#             )
#             print('Connection opened successfully')
#         except Exception as error:
#             print(error)


def add_list(args):
    conn = None
    cur = None

    try:
        conn=psycopg2.connect(
            host=hostname,
            database=database,
            user=pg_user,
            password=pg_password,
            port=port_id
        )
        cur=conn.cursor()

        new_list_name = " ".join(args)
        sql = "INSERT INTO lists(list_name) VALUES(%s)"
        cur.execute(sql, (new_list_name,))
        conn.commit()
        print(f"'{new_list_name}' list is created")
    except Exception as error:
        print(error)
    finally:
        if cur is not None:      
            cur.close()
        if conn is not None:
            conn.close()


def delete_list(args):
    conn = None
    cur = None

    try:
        conn=psycopg2.connect(
            host=hostname,
            database=database,
            user=pg_user,
            password=pg_password,
            port=port_id
        )
        cur=conn.cursor()

        sql = "DELETE FROM lists WHERE list_id = (%s)"
        cur.execute(sql, (args,))
        conn.commit()
        print("List has been deleted")
    except Exception as error:
        print(error)
    finally:
        if cur is not None:      
            cur.close()
        if conn is not None:
            conn.close()
    