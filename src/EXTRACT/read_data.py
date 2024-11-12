from src.EXTRACT.connection import connect_to_db, close_conn
from pprint import pprint
import csv

def read_data(table_name):
    conn = connect_to_db() # connects to the DB created in previous file 
    result =  conn.run(f"SELECT * FROM {table_name};") # queries all row from 
    keys = conn.run(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}';") # retrives column names/headers for the table
    close_conn(conn)

    new_keys = [i for key in keys for i in key] # Flattens the list so the csv writer does not enounter any issues, otherwise it will appear as tuples 
    with open(f'data/{table_name}.csv', 'w', newline='') as csvfile: # creates csv file in write mode 
        writer = csv.writer(csvfile) # creates csv writer object 
        writer.writerow(new_keys) # writes the headers(column names) as the first row 
        writer.writerows(result) # writes all rows of data from the specified table row by row 

    
def read_all_tables():
    table_names = ['counterparty',
                   'currency',
                   'department',
                   'design',
                   'staff',
                   'sales_order',
                   'address',
                   'payment',
                   'purchase_order',
                   'payment_type',
                   'transaction']
    for name in table_names:
        read_data(name)

