# Store Monitoring Backend API

This project is part of a take-home interview assignment for an internship position. The goal is to build a backend system that monitors restaurant stores' online status based on provided data sources and generates reports for restaurant owners.

## Problem Statement

We need to develop backend APIs that will help restaurant owners monitor the online status of their stores. The system must process data from multiple sources, handle periodic updates, and provide detailed uptime and downtime reports for the last hour, day, and week.

## Data Sources

1. **Store Status Data**: A CSV file containing the online status of stores polled roughly every hour (`store_id, timestamp_utc, status`).
2. **Business Hours Data**: A CSV file detailing the business hours of stores in local time (`store_id, dayOfWeek, start_time_local, end_time_local`).
3. **Timezone Data**: A CSV file containing the timezone information for stores (`store_id, timezone_str`).

## System Requirements

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
