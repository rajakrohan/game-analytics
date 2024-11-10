from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Text, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from sqlalchemy import JSON

# Database configuration constants
DB_USER = "root"
DB_PASSWORD = "root1234"
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "game_analytics"

# Form the complete database URL for MySQL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for our models
Base = declarative_base()

# Define the table structure for the 'game_analytic' table
class GameAnalytic(Base):
    __tablename__ = 'game_analytic'

    AppID = Column(Integer, primary_key=True, nullable=False)
    Name = Column(String(255), nullable=False)
    Release_date = Column(String(50))
    Required_age = Column(Integer)
    Price = Column(Float)
    DLC_count = Column(Integer)
    About_the_game = Column(Text)
    Supported_languages = Column(JSON)
    Windows = Column(Boolean)
    Mac = Column(Boolean)
    Linux = Column(Boolean)
    Positive = Column(Integer)
    Negative = Column(Integer)
    Score_rank = Column(Integer)
    Developers = Column(String(255))
    Publishers = Column(String(255))
    Categories = Column(Text)  # Can hold a comma-separated list of categories
    Genres = Column(Text)      # Can hold a comma-separated list of genres
    Tags = Column(Text)        # Can hold a comma-separated list of tags

# Create the table in the database (if not already created)
Base.metadata.create_all(engine)

print("Table 'game_analytic' created successfully!")

def get_db():
    db = SessionLocal()  # create a new session
    try:
        yield db  # return the session to the endpoint
    finally:
        db.close() 
