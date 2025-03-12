from fastapi import FastAPI, BackgroundTasks
import psycopg2
import uuid
import csv
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from helpers import get_uptime_downtime

app = FastAPI()
queue = []
report_status = {}
start_counter = 0

@app.get('/trigger_report')
def trigger_report(background_tasks: BackgroundTasks):
    report_id = str(uuid.uuid4())  
    queue.append(report_id)
    report_status[report_id] = "Started"
    background_tasks.add_task(generate_report, report_id) 
    return {'report_id': report_id}

def generate_report(report_id):
    global start_counter,completed_counter
    print('report started')
    DB_URL = "postgresql://postgres:password@localhost:5432/loop"
    present_time = datetime.strptime("2024-08-10 22:35:00", "%Y-%m-%d %H:%M:%S")
    
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT store_id FROM store_timezones")
    store_ids = [row[0] for row in cursor.fetchall()]
    print("Store id",store_ids)
    cursor.close()
    conn.close()
    
    max_workers = 60
    store_chunks = [store_ids[i::max_workers] for i in range(max_workers)]
    
    with open(f"{report_id}.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["store_id", "last_hour_uptime", "last_hour_downtime", "last_day_uptime", "last_day_downtime", "last_week_uptime", "last_week_downtime"])
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for chunk in store_chunks:
                start_counter+=1
                futures.append(executor.submit(process_stores, chunk, writer, present_time))
                
    report_status[report_id] = "Completed"

def process_stores(store_ids, writer, present_time):
    DB_URL = "postgresql://postgres:password@localhost:5432/loop"
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()
    
    for store_id in store_ids:
        result = get_uptime_downtime(cursor, store_id, present_time)
        writer.writerow([
            store_id,
            result["last_hour"]["uptime"], result["last_hour"]["downtime"],
            result["last_day"]["uptime"], result["last_day"]["downtime"],
            result["last_week"]["uptime"], result["last_week"]["downtime"]
        ])
    
    cursor.close()
    conn.close()

@app.get('/get_report/{report_id}')
def get_report_status(report_id: str):
    return {'report_id': report_id, 'status': report_status.get(report_id, "Not Found")}
