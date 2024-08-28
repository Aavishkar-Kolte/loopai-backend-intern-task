# Store Monitoring Backend API

This project is part of a take-home interview assignment for backend internship position at Loopai. The goal is to build a backend system that monitors restaurant stores' online status based on provided data sources and generates reports for restaurant owners.

## Problem Statement

Develop backend APIs that will help restaurant owners monitor the online status of their stores. The system must process data from multiple sources, handle periodic updates, and provide detailed uptime and downtime reports for the last hour, day, and week.

## Data Sources

1. **Store Status Data**: A CSV file containing the online status of stores polled roughly every hour (`store_id, timestamp_utc, status`).
2. **Business Hours Data**: A CSV file detailing the business hours of stores in local time (`store_id, dayOfWeek, start_time_local, end_time_local`).
3. **Timezone Data**: A CSV file containing the timezone information for stores (`store_id, timezone_str`).

## Requirements

- The data is not static; the system should handle periodic updates.
- Data needs to be ingested into a SQL database.
- APIs should be designed to trigger report generation and retrieve the generated report.

## API Endpoints

### 1. `/trigger_report`

- **Description**: Triggers the generation of a report based on the current data stored in the database.
- **Input**: None
- **Output**: Returns a `report_id` (random string) used for polling the report status.

### 2. `/get_report`

- **Description**: Retrieves the status of the report generation or the final report in CSV format.
- **Input**: `report_id`
- **Output**:
  - If report generation is still in progress: Returns `"Running"`.
  - If report generation is complete: Returns `"Complete"` along with the generated CSV file.

## Report Schema

The generated report will have the following schema:

`store_id, uptime_last_hour(in minutes), uptime_last_day(in hours), uptime_last_week(in hours), downtime_last_hour(in minutes), downtime_last_day(in hours), downtime_last_week(in hours)`

## Local Setup

Follow these steps to set up the project locally on your machine:

### 1. Clone the Repository

Clone the repository to your local machine using the following command:

```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Create a Virtual Environment

Create a virtual environment to isolate the dependencies for this project. You can use `venv` to create it:

```bash
# On Windows
python -m venv venv

# On macOS and Linux
python3 -m venv venv
```

Activate the virtual environment:

```bash
# On Windows
venv\Scripts\activate

# On macOS and Linux
source venv/bin/activate
```

### 3. Install Dependencies

Install the required Python packages using `pip` and the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

This project uses a `.env` file to manage environment variables securely. Create a `.env` file in the root directory of the project and add the required environment variables. Here's an example of what the `.env` file might look like:

```dotenv
DB_URL=postgresql://<username>:<password>@<host>:<port>/<database_name>
```

Make sure to replace `<username>`, `<password>`, `<host>`, `<port>`, and `<database_name>` with your actual PostgreSQL credentials.

### 5. Start the FastAPI Server

Start the FastAPI server using the `fastapi` CLI:

```bash
fastapi dev src/main.py
```

The server should now be running at `http://127.0.0.1:8000`.

### 6. Test the API

You can test the API using a tool like `curl`, `Postman`, or directly in your browser (for GET requests). Alternatively, you can access the interactive API documentation provided by FastAPI at `http://127.0.0.1:8000/docs`.

### 7. Deactivate the Virtual Environment

After you're done working, deactivate the virtual environment by running:

```bash
deactivate
```
