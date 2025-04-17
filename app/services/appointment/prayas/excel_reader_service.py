import os
import pandas as pd
import json
from datetime import datetime

class ExcelReader:
    def __init__(self):
        pass
        #self.required_columns = ['Date', 'Time', 'Name', 'Mobile']

    def format_date(self, date_value):
        try:
            parsed_date = pd.to_datetime(date_value, errors='coerce')
            if pd.isna(parsed_date):
                raise ValueError(f"Invalid date format: {date_value}")
            return parsed_date.strftime("%Y-%m-%d")
        except Exception:
            return None

    async def extract_appointments_From_excel(self, filepath, storage_service):
        try:
            tenant_name = os.getenv("TENANT_NAME")
            filename = f"{tenant_name}_format_mapper.json"
            print("Format mapper file name",filename)
            column_mapping  = await storage_service.search_file(filename)
            if not column_mapping :
                raise FileNotFoundError(f"Mapping file '{filename}' not found.")
            df = pd.read_excel(filepath)
            reversed_mapping = {v: k for k, v in column_mapping.items()}
            # Check if all mapped columns are present in the Excel file
            for excel_col in reversed_mapping.keys():
                if excel_col not in df.columns:
                    raise ValueError(f"Column '{excel_col}' not found in the Excel file.")
            # Filter and rename columns
            filtered_df = df[list(reversed_mapping.keys())].rename(columns=reversed_mapping)
            # Format the appointment date
            filtered_df['AppointmentDate'] = filtered_df['AppointmentDate'].apply(self.format_date)
            # Warn and drop rows with invalid dates
            invalid_dates = filtered_df['AppointmentDate'].isna().sum()
            if invalid_dates > 0:
                print(f"Warning: {invalid_dates} rows have invalid date formats and will be excluded.")
            filtered_df = filtered_df.dropna(subset=['AppointmentDate'])
            return filtered_df.to_dict(orient='records')
            # # Checking if all required columns are present
            # for col in self.required_columns:
            #     if col not in df.columns:
            #         raise ValueError(f"Column '{col}' not found in the Excel file.")
            # filtered_df = df[self.required_columns]
            # # Format the date column
            # filtered_df['Date'] = filtered_df['Date'].apply(self.format_date)
            # # Warn and drop rows with invalid dates
            # invalid_dates = filtered_df['Date'].isna().sum()
            # if invalid_dates > 0:
            #     print(f"Warning: {invalid_dates} rows have invalid date formats and will be excluded.")
            # filtered_df = filtered_df.dropna(subset=['Date'])
            # return filtered_df.to_dict(orient='records')
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

