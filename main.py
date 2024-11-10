from fastapi import FastAPI, HTTPException, Depends
import pandas as pd
import requests
from database import get_db, GameAnalytic
from sqlalchemy.orm import Session
from pydantic import BaseModel
from io import StringIO
from sqlalchemy.exc import SQLAlchemyError
import numpy as np

app = FastAPI()

class CsvUrlRequest(BaseModel):
    csv_url: str

# Helper function to download CSV data
def download_csv(csv_url: str) -> str:
    """Download CSV content from the provided URL and return the raw CSV text."""
    try:
        response = requests.get(csv_url)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to download CSV file.")
        return response.text
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch CSV from URL: {str(e)}")

# Helper function to process the CSV data
def process_csv_data(csv_content: str) -> pd.DataFrame:
    """Parse the CSV content and return a pandas DataFrame."""
    try:
        csv_content_io = StringIO(csv_content)
        return pd.read_csv(csv_content_io)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing CSV content: {str(e)}")

import logging

# Setup basic logging
logging.basicConfig(level=logging.DEBUG)

def clean_row(row):
    """Replace NaN values with None in the row."""
    for col in row.index:
        if isinstance(row[col], float) and np.isnan(row[col]):
            row[col] = None
    return row

def insert_data_into_db(data: pd.DataFrame, db: Session):
    """Insert the CSV data into the database."""
    try:
        for _, row in data.iterrows():
            row = clean_row(row)  # Clean NaN values in the row
            game_analytic = GameAnalytic(
                AppID=row['AppID'],
                Name=row['Name'],
                Release_date=row.get('Release_date', None),
                Required_age=row.get('Required_age', None),
                Price=row.get('Price', None),
                DLC_count=row.get('DLC_count', None),
                About_the_game=row.get('About_the_game', None),
                Supported_languages=row.get('Supported_languages', None),
                Windows=row.get('Windows', None),
                Mac=row.get('Mac', None),
                Linux=row.get('Linux', None),
                Positive=row.get('Positive', None),
                Negative=row.get('Negative', None),
                Score_rank=row.get('Score_rank', None),
                Developers=row.get('Developers', None),
                Publishers=row.get('Publishers', None),
                Categories=row.get('Categories', None),
                Genres=row.get('Genres', None),
                Tags=row.get('Tags', None),
            )
            db.add(game_analytic)
        
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()  # Rollback if there is a database error
        logging.error(f"Database error: {str(e)}")  # Log the exact error
        raise HTTPException(status_code=500, detail="Database error occurred.")
    except Exception as e:
        logging.error(f"Error inserting data: {str(e)}")  # Log general errors
        raise HTTPException(status_code=400, detail=f"Error processing CSV: {str(e)}")

# Define the upload CSV route
@app.post("/upload_csv/")
async def upload_csv(request: CsvUrlRequest, db: Session = Depends(get_db)):
    """Endpoint to upload CSV from a URL, process it, and store in the database."""
    try:
        # Step 1: Download the CSV
        csv_content = download_csv(request.csv_url)

        # Step 2: Process the CSV into a DataFrame
        data = process_csv_data(csv_content)

        # Step 3: Insert the data into the database
        insert_data_into_db(data, db)

        return {"message": "CSV data uploaded and inserted successfully."}

    except HTTPException as e:
        raise e  # Re-raise HTTPExceptions
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing CSV: {str(e)}")

# A route to test querying data
@app.get("/data/")
def get_data(query: str, db: Session = Depends(get_db)):
    try:
        result = db.execute(query).fetchall()
        return {"data": [dict(row) for row in result]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error executing query: {str(e)}")


# Function to parse dates with the correct format
def parse_date(date_str: str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

@app.get("/data_explorer/")
def data_explorer(name: str = None, age: int = None, release_date: str = None, 
                  release_date_gt: str = None, release_date_lt: str = None, 
                  db: Session = Depends(get_db)):
    """
    Allows querying of the stored CSV data by various fields.
    """
    try:
        # Start with all records
        query = db.query(GameAnalytic)

        # Filter by name (substring match)
        if name:
            query = query.filter(GameAnalytic.Name.ilike(f"%{name}%"))
        
        # Filter by age (exact match)
        if age is not None:
            query = query.filter(GameAnalytic.Required_age == age)

        # Filter by release_date (exact match)
        if release_date:
            release_date_parsed = parse_date(release_date)
            query = query.filter(GameAnalytic.Release_date == release_date_parsed)

        # Filter by release_date_gt (greater than match)
        if release_date_gt:
            release_date_gt_parsed = parse_date(release_date_gt)
            query = query.filter(GameAnalytic.Release_date > release_date_gt_parsed)

        # Filter by release_date_lt (less than match)
        if release_date_lt:
            release_date_lt_parsed = parse_date(release_date_lt)
            query = query.filter(GameAnalytic.Release_date < release_date_lt_parsed)

        # Execute the query and convert result into a list
        result = query.all()

        # If no records found, return a message
        if not result:
            return {"message": "No records found matching the query."}

        # Convert results into a list of dictionaries
        result_dict = [row.__dict__ for row in result]  # Get row data as a dict
        # Remove the SQLAlchemy internal attributes like _sa_instance_state
        for row in result_dict:
            row.pop('_sa_instance_state', None)
        
        return {"data": result_dict}

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error occurred: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing the request: {str(e)}")
