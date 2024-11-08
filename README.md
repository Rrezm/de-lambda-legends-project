# de-lambda-legends-project
Required Components
You need to create:

- A job scheduler or orchestration process to run the ingestion job and subsequent processes. You can do this with AWS Eventbridge or with a combination of Eventbridge and AWS Step Functions. Since data has to be visible in the data warehouse within 30 minutes of being written to the database, you need to schedule your job to check for changes frequently.
  
- An S3 bucket that will act as a "landing zone" for ingested data.
  
- A Python application to check for changes to the database tables and ingest any new or updated data. It is strongly recommended that you use AWS Lambda as your computing solution. It is possible to use other computing tools, but it will probably be much harder to orchestrate, monitor and deploy. The data should be saved in the "ingestion" S3 bucket in a suitable format. Status and error messages should be logged to Cloudwatch.
  
- A Cloudwatch alert should be generated in the event of a major error - this should be sent to email.
  
- A second S3 bucket for "processed" data.
  
- A Python application to transform data landing in the "ingestion" S3 bucket and place the results in the "processed" S3 bucket. The data should be transformed to conform to the warehouse schema (see above). The job should be triggered by either an S3 event triggered when data lands in the ingestion bucket, or on a schedule. Again, status and errors should be logged to Cloudwatch, and an alert triggered if a serious error occurs.
  
- A Python application that will periodically schedule an update of the data warehouse from the data in S3. Again, status and errors should be logged to Cloudwatch, and an alert triggered if a serious error occurs.
  
- In the final week of the course, you should be asked to create a simple visualisation such as described above. In practice, this will mean creating SQL queries to answer common business questions. Depending on the complexity of your visualisation tool, other coding may be required too.


## EXTRACT

1. Make s3, setting up iam roles and permissions. Persmissions to connect s3 to lambda.
2. Write lambda code to connect to database, checks data and saves it in the s3 (May need pg8000 in Python to use psql to get data)
3. Set-up an EventBridge rule to trigger the lambda code at defined intervals
4. Connect EventBridge to lambda with Step Functions and State machines (?)
5. Set-up cloudwatch to monitor failures and create a trigger that sends an email in the case of an error

## TRANSFORM

1. Make s3, setting up iam roles and permissions. Persmissions to connect s3 to lambda.
2. Write lambda code to transform the data in the ingestion s3 into star schemas (separate into fact and dimension tables). Use python and pg8000 (psql)
3. Set-up an EventBridge rule to trigger the lambda code at defined intervals
4. Connect EventBridge to lambda with Step Functions and State machines (?)
5. Set-up cloudwatch to monitor failures and create a trigger that sends an email in the case of an error

## LOAD

1. Write lambda code to load the processed data into data warehouse (?)
2. Set-up an EventBridge rule to trigger the lambda code at defined intervals
3. Connect EventBridge to lambda with Step Functions and State machines (?)
4. Set-up cloudwatch to monitor failures and create a trigger that sends an email in the case of an error

## VISUALISATION
BI dashboard with AWS Quicksight, or Jupyter notebook using matplotlib and seaborn.