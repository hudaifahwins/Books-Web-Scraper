import os
import pandas as pd

# Override DATABASE_URL to point to local PostgreSQL before importing api module
os.environ["DATABASE_URL"] = "postgresql+psycopg2://admin:secret@localhost:5433/books_db"

from api import Base, Book, SessionLocal, engine

CSV_FILE = "books.csv"


def main():
    # Drop existing books table and recreate it with the correct schema
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Read books data from local CSV
    df = pd.read_csv(CSV_FILE)
    books = df.to_dict(orient="records")

    db = SessionLocal()
    try:
        for book_data in books:
            book = Book(
                title=book_data["title"],
                price=float(book_data["price"]),
            )
            db.add(book)
        db.commit()
        print(f"Imported {len(books)} books into the books table.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
