import pandas as pd
import json
from datetime import datetime

class ExcelReader:
    def __init__(self, file_path):
        self.required_columns = ['Date', 'Time', 'Name', 'Phone']

    def format_date(self, date_value):
        try:
            parsed_date = pd.to_datetime(date_value, errors='coerce')
            if pd.isna(parsed_date):
                raise ValueError(f"Invalid date format: {date_value}")
            return parsed_date.strftime("%d-%m-%Y")
        except Exception:
            return None

    def extract_appointments_From_excel(self,filepath):
        try:
            df = pd.read_excel(filepath)

            # Checking if all required columns are present
            for col in self.required_columns:
                if col not in df.columns:
                    raise ValueError(f"Column '{col}' not found in the Excel file.")

            filtered_df = df[self.required_columns]

            # Format the date column
            filtered_df['Date'] = filtered_df['Date'].apply(self.format_date)

            # Warn and drop rows with invalid dates
            invalid_dates = filtered_df['Date'].isna().sum()
            if invalid_dates > 0:
                print(f"Warning: {invalid_dates} rows have invalid date formats and will be excluded.")

            filtered_df = filtered_df.dropna(subset=['Date'])

            return filtered_df.to_dict(orient='records')

        except Exception as e:
            print(f"An error occurred: {e}")
            return None

