#!/usr/bin/env python3
"""
Sign-In/Sign-Out Register Management System
Advanced tracking system for equipment and inventory accountability
"""

import pandas as pd
import json
import os
from datetime import datetime, timedelta
import uuid
import base64
from io import BytesIO
from PIL import Image
import qrcode

class SignOutManager:
    def __init__(self, excel_file='STORES_INFRASTRUCTURE_ADMINISTRATION.xlsx'):
        self.excel_file = excel_file
        self.load_data()
    
    def load_data(self):
        """Load existing sign-out data from Excel"""
        try:
            # Try to load existing sign-out register
            self.signout_data = pd.read_excel(self.excel_file, sheet_name='SignOut Register')
        except:
            # Create empty DataFrame with proper structure if sheet doesn't exist
            self.signout_data = pd.DataFrame(columns=[
                'Transaction ID', 'Item Code', 'Item Name', 'Category',
                'Employee Name', 'Employee ID', 'Department', 'Contact',
                'Work Order/Request No', 'Project Name', 'Purpose',
                'Quantity Taken', 'Expected Return Date', 'Actual Return Date',
                'Time Out', 'Time In', 'Status', 'Condition Out', 'Condition In',
                'Photos Out', 'Photos In', 'Notes', 'Approved By', 'Created Date'
            ])
        
        # Load employees database
        try:
            self.employees_data = pd.read_excel(self.excel_file, sheet_name='Employees')
        except:
            # Create sample employees data
            self.employees_data = pd.DataFrame([
                {'Employee ID': 'FAC001', 'Name': 'Sifiso Shezi', 'Department': 'Facilities', 'Contact': 'sifiso.shezi@derivco.com'},
                {'Employee ID': 'FAC002', 'Name': 'John Smith', 'Department': 'Facilities', 'Contact': 'john.smith@derivco.com'},
                {'Employee ID': 'IT001', 'Name': 'Tech Support', 'Department': 'IT', 'Contact': 'tech@derivco.com'},
                {'Employee ID': 'MNT001', 'Name': 'Maintenance Team', 'Department': 'Maintenance', 'Contact': 'maintenance@derivco.com'},
                {'Employee ID': 'SEC001', 'Name': 'Security Team', 'Department': 'Security', 'Contact': 'security@derivco.com'}
            ])
        
        # Load departments and projects
        self.departments = [
            'Facilities', 'IT', 'Maintenance', 'Security', 'Operations', 
            'Finance', 'HR', 'Marketing', 'Development', 'QA'
        ]
        
        self.common_projects = [
            'Office Renovation', 'Equipment Upgrade', 'Emergency Repair',
            'Preventive Maintenance', 'New Installation', 'Building Maintenance',
            'Security Enhancement', 'Infrastructure Upgrade', 'General Maintenance'
        ]
    
    def create_transaction(self, item_code, item_name, category, employee_data, 
                          work_order='', project='', purpose='', quantity=1, 
                          expected_return_days=7, condition='Good', photos=None, 
                          notes='', approved_by='System'):
        """Create a new sign-out transaction"""
        
        transaction_id = f"SO-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Calculate expected return date
        expected_return = datetime.now() + timedelta(days=expected_return_days)
        
        new_transaction = {
            'Transaction ID': transaction_id,
            'Item Code': item_code,
            'Item Name': item_name,
            'Category': category,
            'Employee Name': employee_data.get('name', ''),
            'Employee ID': employee_data.get('employee_id', ''),
            'Department': employee_data.get('department', ''),
            'Contact': employee_data.get('contact', ''),
            'Work Order/Request No': work_order,
            'Project Name': project,
            'Purpose': purpose,
            'Quantity Taken': quantity,
            'Expected Return Date': expected_return.strftime('%Y-%m-%d %H:%M'),
            'Actual Return Date': '',
            'Time Out': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'Time In': '',
            'Status': 'Checked Out',
            'Condition Out': condition,
            'Condition In': '',
            'Photos Out': self._process_photos(photos) if photos else '',
            'Photos In': '',
            'Notes': notes,
            'Approved By': approved_by,
            'Created Date': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        
        # Add to DataFrame
        new_row = pd.DataFrame([new_transaction])
        self.signout_data = pd.concat([self.signout_data, new_row], ignore_index=True)
        
        # Save to Excel
        self._save_to_excel()
        
        return transaction_id
    
    def return_item(self, transaction_id, condition='Good', photos=None, 
                   notes='', returned_by=''):
        """Process item return"""
        
        # Find the transaction
        mask = self.signout_data['Transaction ID'] == transaction_id
        if not mask.any():
            raise ValueError(f"Transaction {transaction_id} not found")
        
        # Update the transaction
        idx = self.signout_data.index[mask][0]
        self.signout_data.at[idx, 'Actual Return Date'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        self.signout_data.at[idx, 'Time In'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        self.signout_data.at[idx, 'Status'] = 'Returned'
        self.signout_data.at[idx, 'Condition In'] = condition
        
        if photos:
            self.signout_data.at[idx, 'Photos In'] = self._process_photos(photos)
        
        if notes:
            existing_notes = self.signout_data.at[idx, 'Notes']
            self.signout_data.at[idx, 'Notes'] = f"{existing_notes}\nReturn Notes: {notes}"
        
        # Save to Excel
        self._save_to_excel()
        
        return True
    
    def get_active_checkouts(self):
        """Get all items currently checked out"""
        mask = self.signout_data['Status'] == 'Checked Out'
        active = self.signout_data[mask].copy()
        
        # Add overdue status
        if not active.empty:
            active['Expected Return Date'] = pd.to_datetime(active['Expected Return Date'])
            active['Days Overdue'] = (datetime.now() - active['Expected Return Date']).dt.days
            active['Is Overdue'] = active['Days Overdue'] > 0
        
        return active
    
    def get_overdue_items(self):
        """Get all overdue items"""
        active = self.get_active_checkouts()
        if active.empty:
            return pd.DataFrame()
        
        return active[active['Is Overdue']].copy()
    
    def get_employee_history(self, employee_id):
        """Get checkout history for specific employee"""
        mask = self.signout_data['Employee ID'] == employee_id
        return self.signout_data[mask].copy()
    
    def get_item_history(self, item_code):
        """Get checkout history for specific item"""
        mask = self.signout_data['Item Code'] == item_code
        return self.signout_data[mask].copy()
    
    def get_dashboard_stats(self):
        """Get statistics for dashboard"""
        total_transactions = len(self.signout_data)
        active_checkouts = len(self.get_active_checkouts())
        overdue_items = len(self.get_overdue_items())
        total_returned = len(self.signout_data[self.signout_data['Status'] == 'Returned'])
        
        # Calculate averages
        returned_items = self.signout_data[self.signout_data['Status'] == 'Returned'].copy()
        avg_checkout_days = 0
        
        if not returned_items.empty:
            returned_items['Time Out'] = pd.to_datetime(returned_items['Time Out'])
            returned_items['Actual Return Date'] = pd.to_datetime(returned_items['Actual Return Date'])
            returned_items['Days Out'] = (returned_items['Actual Return Date'] - returned_items['Time Out']).dt.days
            avg_checkout_days = returned_items['Days Out'].mean()
        
        # Most active employees
        employee_stats = self.signout_data['Employee Name'].value_counts().head(5).to_dict()
        
        # Most checked out categories
        category_stats = self.signout_data['Category'].value_counts().head(5).to_dict()
        
        return {
            'total_transactions': total_transactions,
            'active_checkouts': active_checkouts,
            'overdue_items': overdue_items,
            'total_returned': total_returned,
            'return_rate': (total_returned / total_transactions * 100) if total_transactions > 0 else 0,
            'avg_checkout_days': round(avg_checkout_days, 1),
            'top_employees': employee_stats,
            'top_categories': category_stats
        }
    
    def search_transactions(self, query='', filters=None):
        """Search through all transactions"""
        df = self.signout_data.copy()
        
        if query:
            # Search across multiple fields
            search_fields = ['Item Name', 'Employee Name', 'Department', 'Project Name', 'Purpose', 'Notes']
            mask = pd.Series([False] * len(df))
            
            for field in search_fields:
                if field in df.columns:
                    mask |= df[field].astype(str).str.contains(query, case=False, na=False)
            
            df = df[mask]
        
        if filters:
            for field, value in filters.items():
                if field in df.columns and value:
                    if isinstance(value, list):
                        df = df[df[field].isin(value)]
                    else:
                        df = df[df[field] == value]
        
        return df
    
    def generate_qr_code(self, transaction_id):
        """Generate QR code for transaction"""
        qr_data = {
            'type': 'signout_transaction',
            'transaction_id': transaction_id,
            'url': f'/signout/transaction/{transaction_id}'
        }
        
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(json.dumps(qr_data))
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return base64.b64encode(buffer.read()).decode()
    
    def _process_photos(self, photos):
        """Process and encode photos for storage"""
        if not photos:
            return ''
        
        photo_data = []
        for photo in photos:
            if isinstance(photo, str) and photo.startswith('data:image'):
                # Already base64 encoded
                photo_data.append(photo)
            else:
                # Process raw image
                try:
                    if isinstance(photo, Image.Image):
                        buffer = BytesIO()
                        photo.save(buffer, format='PNG')
                        encoded = base64.b64encode(buffer.getvalue()).decode()
                        photo_data.append(f"data:image/png;base64,{encoded}")
                except Exception:
                    pass
        
        return json.dumps(photo_data)
    
    def _save_to_excel(self):
        """Save data back to Excel file"""
        try:
            # Read existing workbook to preserve other sheets
            with pd.ExcelWriter(self.excel_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                self.signout_data.to_excel(writer, sheet_name='SignOut Register', index=False)
                self.employees_data.to_excel(writer, sheet_name='Employees', index=False)
        except Exception as e:
            # If file doesn't exist, create new one
            with pd.ExcelWriter(self.excel_file, engine='openpyxl') as writer:
                self.signout_data.to_excel(writer, sheet_name='SignOut Register', index=False)
                self.employees_data.to_excel(writer, sheet_name='Employees', index=False)
    
    def export_report(self, start_date=None, end_date=None, format='excel'):
        """Export sign-out register report"""
        df = self.signout_data.copy()
        
        # Filter by date range if provided
        if start_date:
            df = df[pd.to_datetime(df['Created Date']) >= pd.to_datetime(start_date)]
        if end_date:
            df = df[pd.to_datetime(df['Created Date']) <= pd.to_datetime(end_date)]
        
        if format == 'excel':
            filename = f"SignOut_Register_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
            df.to_excel(filename, index=False)
            return filename
        elif format == 'csv':
            filename = f"SignOut_Register_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
            df.to_csv(filename, index=False)
            return filename
        
        return df

# Initialize the sign-out manager
def get_signout_manager():
    """Get or create SignOut manager instance"""
    if not hasattr(get_signout_manager, 'instance'):
        get_signout_manager.instance = SignOutManager()
    return get_signout_manager.instance