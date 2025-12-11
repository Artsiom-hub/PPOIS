import requests


class ExternalBookApi:

    BASE = "https://www.googleapis.com/books/v1/volumes"

    def find_by_isbn(self, isbn: str) -> dict | None:
        params = {"q": f"isbn:{isbn}"}
        r = requests.get(self.BASE, params=params)

        if r.status_code != 200:
            return None

        data = r.json()
        if data["totalItems"] == 0:
            return None

        info = data["items"][0]["volumeInfo"]

        return {
            "title": info.get("title"),
            "authors": info.get("authors", []),
            "publisher": info.get("publisher"),
            "publishedDate": info.get("publishedDate"),
            "description": info.get("description")
        }
