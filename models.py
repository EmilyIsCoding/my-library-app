from sqlalchemy import Table, ForeignKey, Integer, String, create_engine, Column, select, delete
from sqlalchemy.orm import DeclarativeBase, relationship, mapped_column, Session, Mapped
from typing import List as TypingList

import os
from dotenv import load_dotenv
load_dotenv()

database_url = os.getenv('DATABASE_URL')

class Base(DeclarativeBase):
    pass

BookList = Table(
                'books_lists',
                Base.metadata,
                 Column("list_id", ForeignKey('lists.list_id')),
                 Column("book_id", ForeignKey('books.book_id'))
                 )

class List(Base):
    __tablename__ = 'lists'
    list_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    list_name: Mapped[str] = mapped_column(String(100), nullable=False)
    # rename to name on PSQL maybe
    books: Mapped[TypingList["Book"]] = relationship(secondary=BookList, back_populates="lists")

class Book(Base):
    __tablename__ = 'books'
    book_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    author: Mapped[str] = mapped_column(String(100), nullable=False)
    completion_status: Mapped[str] = mapped_column(String(100))
    open_library_link: Mapped[str] = mapped_column(String(100), nullable=False)
    lists: Mapped[TypingList["List"]] = relationship(secondary=BookList, back_populates="books")


def add_list(list_name):
    engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        list = List(list_name=list_name)
        session.add(list)
        print(f"List {list_name} is created.")
        session.commit()

def get_lists():
    engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        stmt = select(List)

        lists = []
        for list in session.scalars(stmt):
            # print(list.list_id, list.list_name)
            numbered_list = f"{list.list_id}. {list.list_name}"
            lists.append(numbered_list)
        # print(lists)
        return lists

def delete_list(list_id):
    engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        session.query(List).filter(List.list_id==list_id).delete()
        session.commit()



def add_book(book_dict):
    engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        book = Book(
            title=book_dict["title"],
            author=book_dict["author"],
            completion_status="0%",
            open_library_link=book_dict["open_library_link"]
            )
        session.add(book)
        print(f"{book_dict['title']} by {book_dict['author']} is created.")
        session.commit()


def add_book_to_list(list_id):
    engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        list = session.query(List).get(list_id)
        book = session.query(Book).order_by(Book.book_id.desc()).first()

        list.books.append(book)
        book.lists.append(list)

        session.commit()
        print(f"Successfully added {book.title} to {list.list_name}")