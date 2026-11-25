import os, json
import gspread

def workbook():
    client = gspread.service_account_from_dict(json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]), scopes=["https://www.googleapis.com/auth/spreadsheets"])
    return client.open_by_key(os.environ["SHEET_ID"])

def records(book, tab):
    rows = book.worksheet(tab).get_all_values()
    return [dict(zip(rows[0], row)) for row in rows[1:] if any(row)] if rows else []

def config(book):
    return {x["key"]: x["value"] for x in records(book, "SCORING_CONFIG")}

def append(book, tab, rows):
    if rows:
        book.worksheet(tab).append_rows(rows, value_input_option="RAW", insert_data_option="INSERT_ROWS")
