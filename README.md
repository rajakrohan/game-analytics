# FastAPI Game Analytic App

This repository contains a FastAPI application for uploading, processing, and querying game data from a CSV file. The app provides endpoints for uploading CSV data, querying data, and exploring the stored records.

## Setup Instructions

to run FastAPI: uvicorn main:app --reload --host 0.0.0.0 --port 8001

### 1. Clone the Repository

First, clone the repository to your local machine:
Refactor the database credentials.

Docker-Setup

docker build -t fastapi-game-analytic-app .

docker run -d -p 8001:8001 fastapi-game-analytic-app


Curls:

curl -X 'POST' \
  'http://127.0.0.1:8001/upload_csv/' \
  -H 'Content-Type: application/json' \
  -d '{"csv_url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSCtraqtnsdYd4FgEfqKsHMR2kiwqX1H9uewvAbuqBmOMSZqTAkSEXwPxWK_8uYQap5omtMrUF1UJAY/pub?gid=1439814054&single=true&output=csv"}'


Data Explorer
GET /data_explorer/

This endpoint allows you to explore and filter the stored data. You can query by any field in the CSV, including age, name, and release date.

Query Parameters:
age=<value>: Exact match for age (numerical field).
name=<substring>: Substring match for name (string field).
release_date=<value>: Exact match for release_date (date field).
release_date__gt=<value>: Get records where release_date is greater than the specified date.
release_date__lt=<value>: Get records where release_date is less than the specified date.

curl -X 'GET' 'http://127.0.0.1:8001/data_explorer/?name=Raj'

To query for records where release_date is greater than 2020-01-01:
bash
curl -X 'GET' 'http://127.0.0.1:8001/data_explorer/?release_date__gt=2020-01-01'

To query for records where release_date is less than 2022-01-01:
bash
Copy code

curl -X 'GET' 'http://127.0.0.1:8001/data_explorer/?release_date__lt=2022-01-01'
