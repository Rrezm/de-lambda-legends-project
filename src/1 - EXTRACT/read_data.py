from connection import connect_to_db, close_conn
from pprint import pprint
import csv

def read_data():
    conn = connect_to_db() # connects to the DB created in previous file 
    result =  conn.run("SELECT * FROM sales_order;") # queries all row from 
    keys = conn.run("SELECT column_name FROM information_schema.columns WHERE table_name = 'sales_order';") # retrives column names/headers for the table
    close_conn(conn)

    new_keys = [i for key in keys for i in key] # Flattens the list so the csv writer does not enounter any issues, otherwise it will appear as tuples 
    print(keys)
    with open('output.csv', 'w', newline='') as csvfile: # creates csv file in write mode 
        writer = csv.writer(csvfile) # creates csv writer object 
        writer.writerow(new_keys) # writes the headers(column names) as the first row 
        writer.writerows(result) # writes all rows of data from the sales_order table row by row 

    
read_data() # call the function 