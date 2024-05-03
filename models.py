from sqlalchemy import Table, ForeignKey, Integer, String, create_engine, text, Column
from sqlalchemy.orm import DeclarativeBase, relationship, mapped_column, Session, Mapped
from typing import List as TypingList


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

import os
from dotenv import load_dotenv
load_dotenv()

database_url = os.getenv('DATABASE_URL')

# SQLAlchemy with PSQL
engine = create_engine(database_url)
Base.metadata.create_all(bind=engine)


with Session(engine) as session:
    list = List(list_name="SQLAlchemy ORM")
    session.add(list)
    session.commit()
    # result = session.query(List).all()
    # print(result)