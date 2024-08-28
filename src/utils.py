from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from collections import defaultdict
from .models import StoreStatus, StoreTimezone, BusinessHours
import pytz
import csv
import os


def generate_report(report_id: str, db: Session, reports: dict):
    report_dir = "../reports"
    os.makedirs(report_dir, exist_ok=True)
    report_file = os.path.join(report_dir, f"{report_id}.csv")

    try:
        # Fetch all store status data
        status_data = db.query(StoreStatus).order_by(StoreStatus.store_id, StoreStatus.timestamp_utc).all()
        
        # Fetch all store timezones
        timezones = {tz.store_id: tz.timezone_str for tz in db.query(StoreTimezone).all()}
        
        # Fetch all business hours
        business_hours_data = defaultdict(list)
        for bh in db.query(BusinessHours).all():
            business_hours_data[bh.store_id].append((bh.day_of_week, bh.start_time_local, bh.end_time_local))

        # Organize status data by store_id
        store_status_dict = defaultdict(list)
        for status in status_data:
            store_status_dict[status.store_id].append(status)

        # Process each store's data and write to CSV
        with open(report_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                "store_id", "uptime_last_hour", "downtime_last_hour", 
                "uptime_last_day", "downtime_last_day", 
                "uptime_last_week", "downtime_last_week"
            ])

            # Calculate report data for each store
            for store_id, statuses in store_status_dict.items():
                timezone_str = timezones.get(store_id, 'America/Chicago')  # Default timezone if not found
                business_hours = business_hours_data.get(store_id, [(day, datetime.min.time(), datetime.max.time()) for day in range(7)])  # Default 24/7 if not found

                result = calculate_uptime_downtime(store_id, statuses, business_hours, timezone_str)
                writer.writerow([
                    result["store_id"], result["uptime_last_hour"], result["downtime_last_hour"],
                    result["uptime_last_day"], result["downtime_last_day"],
                    result["uptime_last_week"], result["downtime_last_week"]
                ])
        
        # Update the report status to 'Complete' with the file path
        reports[report_id] = report_file

    except Exception as e:
        # Log or handle the error appropriately
        reports[report_id] = f"Failed: {str(e)}"



def interpolate_uptime_downtime(status_data, business_hours, timezone_str):
    timezone = pytz.timezone(timezone_str)
    uptime, downtime = timedelta(), timedelta()

    for i in range(len(status_data) - 1):
        start_time = status_data[i].timestamp_utc.astimezone(timezone)
        end_time = status_data[i + 1].timestamp_utc.astimezone(timezone)
        status = status_data[i].status

        for day, start, end in business_hours:
            if start_time.weekday() == day:
                # Convert business start and end times to the current datetime
                business_start = start_time.replace(hour=start.hour, minute=start.minute, second=0, microsecond=0)
                business_end = start_time.replace(hour=end.hour, minute=end.minute, second=0, microsecond=0)

                # Adjust intervals to only consider the overlap with business hours
                actual_start = max(business_start, start_time)
                actual_end = min(business_end, end_time)

                if actual_start < actual_end:
                    interval = actual_end - actual_start
                    if status:
                        uptime += interval
                    else:
                        downtime += interval

    return uptime.total_seconds() / 60, downtime.total_seconds() / 60


def calculate_uptime_downtime(store_id: str, status_data, business_hours, timezone_str):
    # Calculate uptime and downtime for the last hour, day, and week
    uptime_last_hour, downtime_last_hour = interpolate_uptime_downtime(status_data[-2:], business_hours, timezone_str)
    uptime_last_day, downtime_last_day = interpolate_uptime_downtime(status_data[-25:], business_hours, timezone_str)
    uptime_last_week, downtime_last_week = interpolate_uptime_downtime(status_data[-169:], business_hours, timezone_str)

    return {
        "store_id": store_id,
        "uptime_last_hour": uptime_last_hour,
        "downtime_last_hour": downtime_last_hour,
        "uptime_last_day": uptime_last_day / 60,
        "downtime_last_day": downtime_last_day / 60,
        "uptime_last_week": uptime_last_week / 60,
        "downtime_last_week": downtime_last_week / 60,
    }
