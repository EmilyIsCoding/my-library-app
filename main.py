import argparse
import os
import psycopg2
import requests
from dotenv import load_dotenv
load_dotenv()

from list_functions import add_list

endpoint = "https://openlibrary.org/search.json"

parser = argparse.ArgumentParser(
    description="Welcome to your personal library app. Keep track of your Books and stay organized using Lists!"
    )

# Search commands
group = parser.add_mutually_exclusive_group()
group.add_argument("-query", nargs="+", type=str, help="Enter a search query")
group.add_argument("-title", nargs="+", type=str, help="Title of the book")
group.add_argument("-author", nargs="+", type=str, help="Author of the book")

# List/Book commands
group.add_argument("-g", "--get", nargs="+", help="View a book list by name")
group.add_argument("-a", "--add", nargs="+", type=str, help="Add a list")
# group.add_argument("-e", "--edit", nargs="+", help="Edit a book list by id")
# might also be subparse...
group.add_argument("-d", "--delete", help="Delete a book list by id")
group.add_argument("-b", "--book", metavar=("Add a book to a list"),
                   nargs="+", help="Add a book to a list based on its # in the title search results.")
# might need subparse for the above ^ a subparse of query?
args = parser.parse_args()

hostname=os.getenv('HOSTNAME')
database=os.getenv('DATABASE')
pg_user=os.getenv('PG_USER')
pg_password=os.getenv('PG_PASSWORD')
port_id=os.getenv('PORT_ID')

conn = None
cur = None

# Run this the first time
# try:
#     conn=psycopg2.connect(
#         host=hostname,
#         database=database,
#         user=pg_user,
#         password=pg_password,
#         port=port_id
#     )

#     cur=conn.cursor()

#     cur.execute("""CREATE TABLE IF NOT EXISTS lists(
#                 list_id SERIAL PRIMARY KEY,
#                 list_name VARCHAR (100) NOT NULL
#                 );
#                 """)

#     cur.execute("""CREATE TABLE IF NOT EXISTS books(
#                 book_id SERIAL PRIMARY KEY,
#                 title VARCHAR(255),
#                 author VARCHAR(255),
#                 completion_status VARCHAR(50),
#                 open_library_link VARCHAR(255)
#                 );
#                 """)
    
#     cur.execute("""CREATE TABLE IF NOT EXISTS books_lists(
#                 list_id integer REFERENCES lists(list_id),
#                 book_id integer REFERENCES books(book_id),
#                 PRIMARY KEY (list_id, book_id)
#                 );
#                 """)
    
#     conn.commit()
# except Exception as error:
#     print(error)
# finally:
#     if cur is not None:
#         cur.close()
#     if conn is not None:
#         conn.close()

def query_book(url):
    r = requests.get(url)
    print(r.json()["numFound"])
    print(len(r.json()["docs"]))
    for index, doc in enumerate(r.json()["docs"]):
        print(f"{index + 1}). {doc.get('title', 'Untitled')} by {doc.get('author_name', 'Unavailable')} {doc.get('first_publish_year', '')}.")
              
        print(f"Average Ratings: {doc.get('ratings_average', 'Unrated')}")
        print(f"Link: https://openlibrary.org{doc.get('key', '')}")
        print(f"{doc.get('first_sentence', '')} \n")

# Finding a book or author by search query
if args.query:
    try:
        url = f"{endpoint}?q={args.query}&limit=100"
        query_book(url)
    except Exception as error:
        print(error)

# Finding a book by author
if args.author:
    try:
        url = f"{endpoint}?author={args.author}&limit=100"
        query_book(url)
    except Exception as error:
        print(error)

# Finding a book by title
if args.title:
    try:
        url = f"{endpoint}?title={args.title}&limit=100"
        query_book(url)
    except Exception as error:
        print(error)



# Get a list and the books in it
# if args.get:
#     try:
#         conn = psycopg2.connect(
#             host=hostname,
#             database=database,
#             user=pg_user,
#             password=pg_password,
#             port=port_id
#         )
#         cur = conn.cursor()
#         list_name = " ".join(args.get)
#         sql = "SELECT * FROM books_lists WHERE list_name = (%s)"
#         cur.execute(sql, (list_name,))
#         for record in cur.fetchall():
#             print(record)
#         conn.commit()

#     except Exception as error:
#         print(error)
#     finally:
#         if cur is not None:      
#             cur.close()
#         if conn is not None:
#             conn.close()
# Need to insert some books into the lists first

# Add a list
if args.add:
    add_list(args.add)


# Delete a list
if args.delete:
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
        cur.execute(sql, (args.delete,))
        conn.commit()
    except Exception as error:
        print(error)
    finally:
        if cur is not None:      
            cur.close()
        if conn is not None:
            conn.close()


# Add book to a list
# Logic: user searches for a book in query/title/author
# Then user should be able to add the book based on it's # to a list they specify
# Args: Query, #, List

if args.book:
    try:
        book_title = args.book

        url = f"{endpoint}?title={book_title}&limit=100"
        r = requests.get(url)
        
        query_book(url)

        number_book = input("Select a book from the list by number or input 'Q' to quit: ")
        if number_book.upper() == "Q":
            print("Exiting input book.")
        elif int(number_book) > len(r.json()["docs"]) or int(number_book) < 1:
            print("Please input a valid number.")
        elif int(number_book) - 1 <= len(r.json()["docs"]):
            book = r.json()["docs"][int(number_book) - 1]
        else:
            print("Please insert a valid input")

            try:
                conn=psycopg2.connect(
                host=hostname,
                database=database,
                user=pg_user,
                password=pg_password,
                port=port_id
                )
                cur=conn.cursor()

                cur.execute("SELECT * FROM lists;")
                rows=cur.fetchall()
                conn.commit()
                
                for row in rows:
                    print(row)

            except Exception as error:
                print(error)
            finally:
                if cur is not None:      
                    cur.close()
                if conn is not None:
                    conn.close()

            # list_to_add = input(f"Select the list to add {book['title']} to: ")

        # add error handler if not int or Q?

    except Exception as error:
        print(error)