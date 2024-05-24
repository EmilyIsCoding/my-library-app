import argparse
import os
import requests
from dotenv import load_dotenv
load_dotenv()
import models

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
group.add_argument("-get", "--get_all_lists", help="Retrieves all lists")
group.add_argument("-a", "--add", nargs="+", type=str, help="Add a list")
# group.add_argument("-e", "--edit", nargs="+", help="Edit a book list by id")
group.add_argument("-d", "--delete", help="Delete a book list by id")
group.add_argument("-b", "--book", metavar=("Add a book to a list"),
                   nargs="+", help="Search by title to add a book to a list")
args = parser.parse_args()

hostname=os.getenv('HOSTNAME')
database=os.getenv('DATABASE')
pg_user=os.getenv('PG_USER')
pg_password=os.getenv('PG_PASSWORD')
port_id=os.getenv('PORT_ID')
database_url = os.getenv('DATABASE_URL')

# conn = None
# cur = None

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
        print(f"{index + 1}). {doc.get('title', 'Untitled')} by {doc.get('author_name', 'No Author Available')} {doc.get('first_publish_year', '')}.")
              
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
if args.get:
    list_name = " ".join(args.get)
    models.get_list(list_name)

# Add a list
if args.add:
    list_name = " ".join(args.add)
    models.add_list(list_name)

# Get all lists
# TODO: I added this in just to grab the data another way, but I'm not sure if I want to add an argument?
if args.get_all_lists:
    lists = models.get_lists()
    for list in lists:
        print(list)

# Delete a list
if args.delete:
    models.delete_list(args.delete)


# Add book to a list
# Logic: user searches for a book in query/title/author
# Then user should be able to add the book based on it's # to a list they specify
# Args: Query, #, List

if args.book:
    try:
        # searches for book
        book_title = args.book

        url = f"{endpoint}?title={book_title}&limit=100"
        r = requests.get(url)
        
        query_book(url)

        # allows user to select book from query results
        number_book = input("Select a book from the list by number or input 'Q' to quit: ")

        if number_book.isdigit() == False and number_book.upper() != "Q":
            print("Please insert a valid input.")
        elif number_book.isdigit() and int(number_book) > len(r.json()["docs"]) or  \
                number_book.isdigit() and int(number_book) < 1:
            print("Please input a valid number.")
        elif number_book.upper() == "Q":
            print("Exiting input book.")
        elif int(number_book) - 1 <= len(r.json()["docs"]):
            book = r.json()["docs"][int(number_book) - 1]
            print(book.get("title"))

            book_dict = {
                "title": book.get('title', 'Untitled'),
                "author": book.get('author_name', 'No Author Available'),
                "open_library_link": f"https://openlibrary.org{book.get('key', '')}"
            }

            # shows list of Lists to user
            lists = models.get_lists()
            list_ids = []
            for list in lists:
                print(list)
                list_ids.append(int(list.split(".")[0]))

            # validates user input for List
            number_list = input(f"\n Select the list to add '{book['title']}' to: ")

            if number_list.isdigit() == False:
                print("Please input a number id.")
            elif int(number_list) not in list_ids:
                print("Please input a valid id.")
            elif number_list.isdigit() and int(number_list) in list_ids:
                models.add_book(book_dict)
                models.add_book_to_list(int(number_list))

            # TODO: Having to search for a book creates a new entry each time... think of a better user flow that's better for the DB too
            # or check by open_library_link before adding to db
            # then we query by it I guess

    except Exception as error:
        print(error)