from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .models import StoreStatus, BusinessHours, StoreTimezone
import pytz
import csv


def generate_report(report_id: str, db: Session):
    report_file = f"{report_id}.csv"
    with open(report_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["store_id", "uptime_last_hour", "downtime_last_hour", "uptime_last_day", "downtime_last_day", "uptime_last_week", "downtime_last_week"])

        store_ids = db.query(StoreStatus.store_id).distinct().all()
        for store_id_tuple in store_ids:
            store_id = store_id_tuple[0]
            result = calculate_uptime_downtime(store_id, db)
            writer.writerow([result["store_id"], result["uptime_last_hour"], result["downtime_last_hour"], result["uptime_last_day"], result["downtime_last_day"], result["uptime_last_week"], result["downtime_last_week"]])

    reports[report_id] = report_file



def interpolate_uptime_downtime(store_id, status_data, business_hours, timezone_str):
    timezone = pytz.timezone(timezone_str)
    uptime, downtime = timedelta(), timedelta()

    for i in range(len(status_data) - 1):
        start_time = status_data[i].timestamp_utc.astimezone(timezone)
        end_time = status_data[i + 1].timestamp_utc.astimezone(timezone)
        status = status_data[i].status

        print(business_hours)
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



def calculate_uptime_downtime(store_id: str, db: Session):
    status_data = db.query(StoreStatus).filter(StoreStatus.store_id == store_id).order_by(StoreStatus.timestamp_utc).all()

    # Query timezone information and use 'America/Chicago' as default if not found
    timezone_record = db.query(StoreTimezone).filter(StoreTimezone.store_id == store_id).first()
    timezone_str = timezone_record.timezone_str if timezone_record else 'America/Chicago'

    # Query business hours and convert to tuples, otherwise use default 24/7
    business_hours_data = db.query(BusinessHours).filter(BusinessHours.store_id == store_id).all()
    if business_hours_data:
        business_hours = [(bh.day_of_week, bh.start_time_local, bh.end_time_local) for bh in business_hours_data]
    else:
        business_hours = [(day, datetime.min.time(), datetime.max.time()) for day in range(7)]

    # Calculate uptime and downtime for the last hour, day, and week
    uptime_last_hour, downtime_last_hour = interpolate_uptime_downtime(store_id, status_data[-2:], business_hours, timezone_str)
    uptime_last_day, downtime_last_day = interpolate_uptime_downtime(store_id, status_data[-25:], business_hours, timezone_str)
    uptime_last_week, downtime_last_week = interpolate_uptime_downtime(store_id, status_data[-169:], business_hours, timezone_str)

    return {
        "store_id": store_id,
        "uptime_last_hour": uptime_last_hour,
        "downtime_last_hour": downtime_last_hour,
        "uptime_last_day": uptime_last_day / 60,
        "downtime_last_day": downtime_last_day / 60,
        "uptime_last_week": uptime_last_week / 60,
        "downtime_last_week": downtime_last_week / 60,
    }

