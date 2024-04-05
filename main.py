import argparse
import os
import psycopg2
import requests
from dotenv import load_dotenv
load_dotenv()

endpoint = "https://openlibrary.org/search.json"

parser = argparse.ArgumentParser(
    description="Organize a list of books you've read, are reading, or want to read"
    )
# Search commands
group = parser.add_mutually_exclusive_group()
group.add_argument("-query", nargs="+", type=str, help="Enter a search query")
group.add_argument("-title", nargs="+", type=str, help="Title of the book")
group.add_argument("-author", nargs="+", type=str, help="Author of the book")

# List/Book commands
# group.add_argument("-g", "--get", help="View a book list")
group.add_argument("-a", "--add", nargs="+", type=str, help="Add a list")
# group.add_argument("-u", "--update", help="Update a book list")
# group.add_argument("-d", "--delete", help="Delete a book list")
group.add_argument("-b", "--book", metavar=("Title, # in title List, List name"),
                   nargs=3, help="Add a book to a list based on its # in the title search results.")
args = parser.parse_args()

hostname = os.getenv('HOSTNAME')
database = os.getenv('DATABASE')
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
port_id = os.getenv('PORT_ID')

print(hostname, database, username, password, port_id)

conn = None
cur = None

# ERROR: connection to server at "localhost" (::1), port 5432 failed: FATAL:  password authentication failed for user "SonEm"
# postgres

try:
    conn = psycopg2.connect(
        host=hostname,
        database=database,
        user=username,
        password=password,
        port=port_id
    )

    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS lists(
                list_id SERIAL PRIMARY KEY,
                list_name VARCHAR (100) NOT NULL
                );
                """)

    cur.execute("""CREATE TABLE IF NOT EXISTS books(
                book_id SERIAL PRIMARY KEY,
                title VARCHAR(255),
                author VARCHAR(255),
                completion_status VARCHAR(50),
                open_library_link VARCHAR(255)
                );
                """)
    
    cur.execute("""CREATE TABLE IF NOT EXISTS books_lists(
                list_id integer REFERENCES lists(list_id),
                book_id integer REFERENCES books(book_id),
                PRIMARY KEY (list_id, book_id)
                );
                """)
    
    conn.commit()

except Exception as error:
    print(error)
finally:
    if cur is not None:
        cur.close()
    if conn is not None:
        conn.close()

def query_book(url):
    r = requests.get(url)
    print(r.json()["numFound"])
    for index, doc in enumerate(r.json()["docs"]):
        print(f"{index + 1}). {doc['title']} by {doc['author_name']} {doc['first_publish_year']}.")
        print(f"Average Ratings: {doc['ratings_average']}")
        print(f"Link: https://openlibrary.org/{doc['key']}")
        print(f"{doc['first_sentence']} \n")

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

# Why does this give me so few results??


# Add a list
if args.add:
    try:
        conn = psycopg2.connect(
            host=hostname,
            database=database,
            user=username,
            password=password,
            port=port_id
        )

        new_list_name = " ".join(args.add)
        print(new_list_name)

        cur = conn.cursor()
        sql = "INSERT INTO lists(list_name) VALUES(%s)"
        cur.execute(sql, (new_list_name,))

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
        book_title = args.book[0]
        num_list = args.book[1]
        list_name = args.book[2]

        url = f"{endpoint}?title={book_title}&limit=100"
        r = requests.get(url)
        print(r.json()["numFound"])
        if r.json()["docs"][int(num_list) - 1]:
            book = r.json()['docs'][int(num_list) - 1]
            print(f"{book['title']} by {book['author_name']} {book['first_publish_year']} will be appended to {list_name}")
            # Replace this later with PSQL
    except Exception as error:
        print(error)


# Maybe to allow for spaces...... just make infinite args and have the user explicitly separate with commas or something