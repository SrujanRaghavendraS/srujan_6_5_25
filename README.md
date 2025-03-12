Store Monitoring Assignment
API Overview
•	Trigger Report
Endpoint: GET /trigger_report
Description: Triggers the generation of a report for monitoring store uptime/downtime. The process runs in the background, and a unique report_id is returned, which can be used to check the status of the report.
Parameters: None
Response model: 
{
"report_id": "123e4567-e89b-12d3-a456-426614174000"
}
•	Get Report Status
Endpoint: GET /get_report/{report_id}
Description: Retrieves the status of a previously triggered report. If the report is completed, it returns "Completed", otherwise "Started" or "Not Found".
Parameters:
report_id (path parameter) - The unique identifier of the report to check its status.
Responses:
 If the report is still being generated:
{
    "report_id": "123e4567-e89b-12d3-a456-426614174000",
    "status": "Started"
}
If the report has been successfully generated:
{
    "report_id": "123e4567-e89b-12d3-a456-426614174000",
    "status": "Completed"
}
If the report ID is invalid or not found:
{
    "report_id": "invalid-report-id",
    "status": "Not Found"
}
Additional Notes
•	The report generation runs asynchronously in the background using FastAPI's BackgroundTasks.
•	The generated report is stored as a CSV file, named {report_id}.csv, containing: 
•	store_id
•	uptime and downtime for the last hour, last day, and last week.
•	The get_report API does not return the CSV file directly; it only provides the status of the report.


How does the API’s work internally?
As the name suggests this API triggers a function named generate report which is a Background task and returns the report_id .
In the background task there are 60 threads which are working parallelly upon the database and Computations of the up_time and downtime from the filtered data from the database.
Initially based on the Time Zones from store_timezones the start_time_local and end_time_local are converted to utc format and the required data is filtered with using store_id and then the polling data is filtered by checking the poll times whether present inside the working time limits. Since the data is old the present time and date are hardcoded.The calculated data is then stored inside a .csv file
When the get_report endpoint is used the status of the reported started/completed is returned.
It is better to convert the received data from polls to utc format and then append to the database so that further calculations are prevented especially during calculations of uptime and downtime and the same approach is used
Futher Improvements
•	Handling and tracking thread process states efficientely
•	Realtime progress tracking and transfer
•	Have Mutex locks for CSV Files to prevent read-write issues
•	Have a calculation for number of threads and use the proved number of threads for better and fast results

