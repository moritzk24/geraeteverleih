import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session


def extract_inventar(db: Session) -> pd.DataFrame:
    return pd.read_sql(text("SELECT * FROM alt_inventar"), db.connection())


def extract_ausleihen(db: Session) -> pd.DataFrame:
    return pd.read_sql(text("SELECT * FROM alt_ausleihen"), db.connection())
