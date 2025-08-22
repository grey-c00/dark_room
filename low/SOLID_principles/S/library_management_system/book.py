import threading
from enum import Enum

class AvailabilityStatus(Enum):
    AVAILABLE = "Available"
    CHECKED_OUT = "Checked Out"


class Book:
    def __init__(self, title: str, author: str, isbn: str, availability_status: AvailabilityStatus = AvailabilityStatus.AVAILABLE):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.availability_status = availability_status

    def __str__(self) -> str:
        return f"Title: {self.title}, Author: {self.author}, ISBN: {self.isbn}"

    def make_available(self) -> bool:
        self.availability_status = AvailabilityStatus.AVAILABLE
        return True

    def check_out(self) -> bool:
        self.availability_status = AvailabilityStatus.CHECKED_OUT
        return True

    def get_book_id(self) -> str:
        return str(self.isbn)


class BooksManager:
    _books_manager = {}
    _lock = threading.Lock() # we need a class level lock to prevent giving out one book to two users

    def __init__(self):
        pass



    def is_book_available(self, book_id: str) -> bool:
        return book_id in self._books_manager

    @classmethod
    def add_book(cls, book: Book):
        book_id = book.get_book_id()
        with cls._lock:
            if cls.is_book_available(book_id):
                print(f"Book: {book.get_details()} is already present in the library")
                return
            cls._books_manager[book_id] = book

        print(f"Book: {book.__str__()} has been added to the library")

