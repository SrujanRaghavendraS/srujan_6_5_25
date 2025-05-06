from datetime import datetime, timedelta
def get_filtered_store_data(cursor, store_id, present_time, time_delta):
    start_time = present_time - time_delta
    query = """
    SELECT ss.status, ss.timestamp_utc, sh.start_time_utc, sh.end_time_utc
    FROM store_status ss
    JOIN store_hours sh 
        ON ss.store_id = sh.store_id 
       AND EXTRACT(DOW FROM ss.timestamp_utc) = sh.day_of_week  
    WHERE ss.store_id = %s
      AND ss.timestamp_utc BETWEEN %s AND %s
    ORDER BY ss.timestamp_utc
    """
    cursor.execute(query, (store_id, start_time, present_time))
    k = cursor.fetchall()
    print(len(k))
    return k

# def calculate_uptime_downtime(filtered_data, present_time):
#     if not filtered_data:
#         return 0, 0
    
#     uptime, downtime = 0, 0
#     last_timestamp, last_status = None, None
    
#     for status, timestamp, start_time_utc, end_time_utc in filtered_data:
#         if last_timestamp is None:
#             last_timestamp, last_status = timestamp, status.lower().strip()
#             continue
        
#         time_diff = max((timestamp - last_timestamp).total_seconds() / 60, 0)
#         if last_status == "active":
#             uptime += time_diff
#         else:
#             downtime += time_diff
        
#         last_timestamp, last_status = timestamp, status.lower().strip()
    
#     if last_timestamp:
#         time_diff = max((present_time - last_timestamp).total_seconds() / 60, 0)
#         if last_status == "active":
#             uptime += time_diff
#         else:
#             downtime += time_diff
    
#     return round(uptime, 2), round(downtime, 2)


def calculate_uptime_downtime(filtered_data, present_time):
    if not filtered_data:
        return 0, 0
    
    _, _, start_time, end_time = filtered_data[0]

    day_start = datetime.combine(present_time.date(), start_time)
    day_end = datetime.combine(present_time.date(), end_time)
    

    observations = [
        (status.lower().strip(), timestamp)
        for status, timestamp, s_time, e_time in filtered_data
        if isinstance(timestamp, datetime) and (day_start <= timestamp <= day_end) 
    ]

    observations.sort(key=lambda x: x[1])

    uptime = 0
    downtime = 0
    intervals = []

    current_time = day_start
    last_status = "active"

    for status, timestamp in observations:
        duration = (timestamp - current_time).total_seconds() / 60  
        if last_status == "active" and  status =='active' :
            uptime += duration
        else:
            downtime += duration

        intervals.append((last_status, current_time, timestamp))
        current_time = timestamp
        last_status = status

    if current_time < day_end:
        duration = (day_end - current_time).total_seconds() / 60
        if last_status == "active":
            uptime += duration
        else:
            downtime += duration
        intervals.append((last_status, current_time, day_end))

    return round(uptime, 2), round(downtime, 2)



def get_uptime_downtime(cursor, store_id, present_time):
    try:
        filtered_data_last_hour = get_filtered_store_data(cursor, store_id, present_time, timedelta(hours=1))
        uptime_last_hour, downtime_last_hour = calculate_uptime_downtime(filtered_data_last_hour, present_time)
        
        filtered_data_last_day = get_filtered_store_data(cursor, store_id, present_time, timedelta(days=1))
        uptime_last_day, downtime_last_day = calculate_uptime_downtime(filtered_data_last_day, present_time)
        
        filtered_data_last_week = get_filtered_store_data(cursor, store_id, present_time, timedelta(weeks=1))
        uptime_last_week, downtime_last_week = calculate_uptime_downtime(filtered_data_last_week, present_time)

        return {
            "last_hour": {"uptime": uptime_last_hour, "downtime": downtime_last_hour},
            "last_day": {"uptime": round(uptime_last_day / 60, 2), "downtime": round(downtime_last_day / 60, 2)},
            "last_week": {"uptime": round(uptime_last_week / 60, 2), "downtime": round(downtime_last_week / 60, 2)},
        }
    
    except Exception as e:
        print(f"Error processing store {store_id}: {e}")
        return {
            "last_hour": {"uptime": 0, "downtime": 0},
            "last_day": {"uptime": 0, "downtime": 0},
            "last_week": {"uptime": 0, "downtime": 0},
        }