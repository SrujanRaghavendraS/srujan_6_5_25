
## API Overview

### Trigger Report
- **Endpoint:** `GET /trigger_report`
- **Description:** Triggers the generation of a report for monitoring store uptime/downtime. The process runs in the background, and a unique `report_id` is returned, which can be used to check the status of the report.

#### **Parameters:** None  
#### **Response Model:**  
`
{
    "report_id": "123e4567-e89b-12d3-a456-426614174000"
}
`

---

###  Get Report Status
- **Endpoint:** `GET /get_report/{report_id}`
- **Description:** Retrieves the status of a previously triggered report. If the report is completed, it returns **"Completed"**, otherwise **"Started"** or **"Not Found"**.

#### **Parameters:**  
- `report_id` (path parameter) - The unique identifier of the report to check its status.

#### **Responses:**
**If the report is still being generated:**  
`
{
    "report_id": "123e4567-e89b-12d3-a456-426614174000",
    "status": "Started"
}
`

**If the report has been successfully generated:**  
`
{
    "report_id": "123e4567-e89b-12d3-a456-426614174000",
    "status": "Completed"
}
`

**If the report ID is invalid or not found:**  
`
{
    "report_id": "invalid-report-id",
    "status": "Not Found"
}
`



## Additional Notes
- The report generation runs **asynchronously** in the background using **FastAPI’s BackgroundTasks**.
- The generated report is stored as a CSV file, named `{report_id}.csv`, containing:
  - **store_id**
  - **uptime and downtime** for the **last hour, last day, and last week**.
- The `/get_report/` API **does not return the CSV file** directly; it only provides the status of the report.



## How does the API work internally?  
- When `/trigger_report` is called, it **triggers a background task** called `generate_report`, returning a `report_id`.  
- The background task uses **60 parallel threads** to process the database and compute **uptime/downtime** from the filtered data.  
- **Time Zones** from `store_timezones` are converted to UTC format, filtering data based on `store_id`.  
- **Polling data** is further filtered based on whether poll times fall within working hours.  
- The **calculated data is stored in a CSV file**.  
- When `/get_report/` is used, it checks if the report is `"Started"` or `"Completed"`.  

** Optimization Suggestion:**  
To improve efficiency, convert poll data **to UTC before storing it in the database** to avoid recalculations during report generation.

## Future Improvements
**Efficient Thread Tracking:** Improve handling and tracking of parallel thread execution.  
**Real-time Progress Tracking:** Implement status updates during report generation.  
**CSV File Mutex Locking:** Prevent read/write conflicts when multiple threads access the CSV file.  
**Optimized Thread Calculation:** Dynamically determine the best number of threads for faster processing.  


