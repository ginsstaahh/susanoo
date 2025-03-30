from sqlalchemy import create_engine
from sqlalchemy.orm import Session

username = "postgres"
password = "postgres"
host = "localhost"
port = "5432"
database_name = "susanoo"
database_url = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database_name}"

engine = create_engine(database_url, echo=True)
session = Session(engine)
