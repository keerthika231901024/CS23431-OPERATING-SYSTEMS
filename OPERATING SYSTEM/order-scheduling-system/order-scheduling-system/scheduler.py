from datetime import datetime, timedelta
import csv
from zoneinfo import ZoneInfo  # For timezone support

IST = ZoneInfo("Asia/Kolkata")  # Indian Standard Time

def read_orders(file_path):
    orders = []
    with open(file_path, newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 6 or row[0] == "customer_name":
                continue
            orders.append({
                "customer_name": row[0],
                "dish_name": row[1],
                "prep_time": int(row[2]),
                "category": row[3],
                "priority": int(row[4]),
                "timestamp": datetime.strptime(row[5], "%Y-%m-%d %H:%M:%S").replace(tzinfo=IST)
            })
    return orders

def schedule_orders(orders, algorithm="Priority", quantum=5):
    now = datetime.now(IST)
    scheduled_orders = []

    if algorithm == "Priority":
        orders.sort(key=lambda x: x["priority"])
    elif algorithm == "FCFS":
        orders.sort(key=lambda x: x["timestamp"])
    elif algorithm == "SJF":
        orders.sort(key=lambda x: x["prep_time"])
    elif algorithm == "Round Robin":
        return round_robin_schedule(orders, quantum)

    for order in orders:
        start_time = order["timestamp"]
        end_time = start_time + timedelta(minutes=order["prep_time"])

        if now < start_time:
            status = "Pending"
        elif start_time <= now < end_time:
            status = "In Progress"
        else:
            status = "Completed"

        scheduled_orders.append({
            **order,
            "start_time": start_time.strftime("%H:%M:%S"),
            "end_time": end_time.strftime("%H:%M:%S"),
            "status": status
        })

    return scheduled_orders

def round_robin_schedule(orders, quantum):
    now = datetime.now(IST)
    orders = sorted(orders, key=lambda x: x["timestamp"])
    remaining_time = {i: order["prep_time"] for i, order in enumerate(orders)}
    current_time = orders[0]["timestamp"] if orders else now
    finished = set()
    schedule = []

    while len(finished) < len(orders):
        for i, order in enumerate(orders):
            if i in finished:
                continue

            time_slice = min(quantum, remaining_time[i])
            start_time = current_time
            end_time = start_time + timedelta(minutes=time_slice)

            remaining_time[i] -= time_slice
            if remaining_time[i] <= 0:
                finished.add(i)

            if now < start_time:
                status = "Pending"
            elif start_time <= now < end_time:
                status = "In Progress"
            else:
                status = "Completed"

            schedule.append({
                **order,
                "start_time": start_time.strftime("%H:%M:%S"),
                "end_time": end_time.strftime("%H:%M:%S"),
                "status": status,
                "slice": time_slice
            })

            current_time = end_time

    return schedule