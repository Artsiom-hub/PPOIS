class BookCatalogError(Exception):
    pass


class BookNotFound(BookCatalogError):
    def __init__(self, book_id: int):
        super().__init__(f"Book with id={book_id} not found")


class InvalidSearchFilter(BookCatalogError):
    pass
