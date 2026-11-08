import pandas as pd
from sqlalchemy import create_engine

DATABASE_URL = "postgresql+psycopg2://admin:secret@localhost:5433/books_db"
CSV_FILE = "books.csv"


def main():
    df = pd.read_csv(CSV_FILE)

    engine = create_engine(DATABASE_URL)

    df.to_sql(
        name="books",
        con=engine,
        if_exists="replace",
        index=False,
    )

    print(f"Imported {len(df)} books into the books table.")


if __name__ == "__main__":
    main()
