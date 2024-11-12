from src.EXTRACT.read_data import read_data, read_all_tables
import csv
import os

# currency is smallest so we shall use it for our tests

def test_read_data_outputs_correct_csv():
    read_data('currency')
    with open('data/currency.csv', 'r') as file:
        data = csv.reader(file)
        list_data = [row for row in data]
    expected = [['currency_id', 'currency_code', 'created_at', 'last_updated'],
                ['1', 'GBP', '2022-11-03 14:20:49.962000', '2022-11-03 14:20:49.962000'],
                ['2', 'USD', '2022-11-03 14:20:49.962000', '2022-11-03 14:20:49.962000'],
                ['3', 'EUR', '2022-11-03 14:20:49.962000', '2022-11-03 14:20:49.962000']]
    assert list_data == expected

def test_read_data_does_not_append():
    read_data('currency')
    read_data('currency')
    with open('data/currency.csv', 'r') as file:
        data = csv.reader(file)
        list_data = [row for row in data]
    expected = [['currency_id', 'currency_code', 'created_at', 'last_updated'],
                ['1', 'GBP', '2022-11-03 14:20:49.962000', '2022-11-03 14:20:49.962000'],
                ['2', 'USD', '2022-11-03 14:20:49.962000', '2022-11-03 14:20:49.962000'],
                ['3', 'EUR', '2022-11-03 14:20:49.962000', '2022-11-03 14:20:49.962000']]
    assert list_data == expected

def test_read_all_tables_has_created_files_in_data():
    read_all_tables()
    file_names = os.listdir(path='data')
    expected = ['payment_type.csv',
                'sales_order.csv',
                'payment.csv',
                'currency.csv',
                'transaction.csv',
                'staff.csv',
                'department.csv',
                'purchase_order.csv',
                'address.csv',
                'counterparty.csv',
                'design.csv']
    assert file_names == expected
