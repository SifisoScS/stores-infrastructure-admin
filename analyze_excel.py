#!/usr/bin/env python3
"""
Script to analyze the Excel file structure for the Stores Infrastructure Administration
"""
import pandas as pd
import sys

def analyze_excel_file(file_path):
    """Analyze the structure and content of the Excel file"""
    try:
        # Read the Excel file
        excel_file = pd.ExcelFile(file_path)
        
        print("EXCEL FILE ANALYSIS")
        print("=" * 50)
        print(f"File: {file_path}")
        print(f"Number of sheets: {len(excel_file.sheet_names)}")
        print(f"Sheet names: {excel_file.sheet_names}")
        print()
        
        # Analyze each sheet
        for sheet_name in excel_file.sheet_names:
            print(f"SHEET: {sheet_name}")
            print("-" * 30)
            
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            print(f"Rows: {len(df)}")
            print(f"Columns: {len(df.columns)}")
            print(f"Column names: {list(df.columns)}")
            
            # Show first few rows
            print("\nFirst 5 rows:")
            print(df.head())
            print()
            
            # Show data types
            print("Data types:")
            print(df.dtypes)
            print("\n" + "="*50 + "\n")
            
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None

if __name__ == "__main__":
    file_path = "STORES_INFRASTRUCTURE_ADMINISTRATION.xlsx"
    analyze_excel_file(file_path)