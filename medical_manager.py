#!/usr/bin/env python3
"""
Medical Services Management System
Professional medical incident tracking and first aid kit management
Hospital-grade digital system for workplace medical services
"""

import pandas as pd
import json
import os
from datetime import datetime, timedelta
import uuid
import base64
from io import BytesIO
from PIL import Image

class MedicalManager:
    def __init__(self, excel_file='medication_data_enhanced.xlsx'):
        self.excel_file = excel_file
        self.load_data()
    
    def load_data(self):
        """Load medical data from Excel"""
        try:
            # Load incident reports
            self.incident_reports = pd.read_excel(self.excel_file, sheet_name='Medical Incidents')
        except:
            self.incident_reports = pd.DataFrame(columns=[
                'Incident ID', 'Date', 'Time', 'Patient Name', 'Employee ID', 
                'Department', 'Age', 'Gender', 'Contact Number',
                'Incident Type', 'Location of Incident', 'Description',
                'Body Part Affected', 'Injury Type', 'Severity Level',
                'Treatment Given', 'Medication Administered', 'Vital Signs',
                'First Aider Name', 'First Aider Cert', 'Witness Name',
                'Referred to Hospital', 'Hospital Name', 'Follow Up Required',
                'Follow Up Date', 'SHE Committee Reported', 'Photos',
                'Additional Notes', 'Status', 'Created By', 'Created Date'
            ])
        
        try:
            # Load first aid kit inventory
            self.medical_inventory = pd.read_excel(self.excel_file, sheet_name='Medical Inventory')
        except:
            # EXACT CONTENTS OF FIRST AID BOX from Paramedic 2.pdf - Items 1-25 as listed
            self.medical_inventory = pd.DataFrame([
                # Item numbers match exactly with Paramedic 2.pdf "CONTENTS OF FIRST AID BOX"
                {'Item No': 1, 'Item Code': 'FAK001', 'Item Name': 'Vomiting bags', 'Quantity': 4, 'Stock': 4, 'Min Level': 1, 'Unit': 'pieces', 'Status': 'Available', 'Location': 'First Aid Box', 'Expiry Date': '2025-12-31'},
                {'Item No': 2, 'Item Code': 'FAK002', 'Item Name': 'Wound cleaning disinfectants', 'Quantity': 1, 'Stock': 1, 'Min Level': 1, 'Unit': 'bottles', 'Status': 'Available', 'Location': 'First Aid Box', 'Expiry Date': '2025-06-30'},
                {'Item No': 3, 'Item Code': 'FAK003', 'Item Name': 'Swelling or cleaning bandages', 'Quantity': 4, 'Stock': 4, 'Min Level': 2, 'Unit': 'pieces', 'Status': 'Available', 'Location': 'First Aid Box', 'Expiry Date': '2026-03-31'},
                {'Item No': 4, 'Item Code': 'FAK004', 'Item Name': 'Contilon wound dressing', 'Quantity': 4, 'Stock': 4, 'Min Level': 2, 'Unit': 'pieces', 'Status': 'Available', 'Location': 'First Aid Box', 'Expiry Date': '2025-09-30'},
                {'Item No': 5, 'Item Code': 'FAK005', 'Item Name': 'Gauze bandages', 'Quantity': 4, 'Stock': 4, 'Min Level': 2, 'Unit': 'pieces', 'Status': 'Available', 'Location': 'First Aid Box', 'Expiry Date': '2025-12-31'},
                {'Item No': 6, 'Item Code': 'FAK006', 'Item Name': 'Roller bandages (10cm x 5cm)', 'Quantity': 4, 'Stock': 4, 'Min Level': 2, 'Unit': 'rolls', 'Status': 'Available', 'Location': 'First Aid Box', 'Expiry Date': '2026-06-30'},
                {'Item No': 7, 'Item Code': 'FAK007', 'Item Name': 'Roller bandages (7.5cm x 5cm)', 'Quantity': 4, 'Stock': 4, 'Min Level': 2, 'Unit': 'rolls', 'Status': 'Available', 'Location': 'First Aid Box', 'Expiry Date': '2026-06-30'},
                {'Item No': 8, 'Item Code': 'FAK008', 'Item Name': 'Roller bandages (5cm x 5cm)', 'Quantity': 4, 'Stock': 4, 'Min Level': 2, 'Unit': 'rolls', 'Status': 'Available', 'Location': 'First Aid Box', 'Expiry Date': '2026-06-30'},
                {'Item No': 9, 'Item Code': 'FAK009', 'Item Name': 'Pressure bandages (10cm x 5cm)', 'Quantity': 4, 'Stock': 4, 'Min Level': 2, 'Unit': 'pieces', 'Status': 'Available', 'Location': 'First Aid Box', 'Expiry Date': '2025-11-30'},
                {'Item No': 10, 'Item Code': 'FAK010', 'Item Name': 'Roller bandages (7.5cm x 5cm)', 'Quantity': 4, 'Stock': 4, 'Min Level': 2, 'Unit': 'rolls', 'Status': 'Available', 'Location': 'First Aid Box', 'Expiry Date': '2026-06-30'},
                {'Item No': 11, 'Item Code': 'FAK011', 'Item Name': 'Non-adherent dressing', 'Quantity': 4, 'Stock': 4, 'Min Level': 2, 'Unit': 'pieces', 'Status': 'Available', 'Location': 'First Aid Box', 'Expiry Date': '2025-10-31'},
                {'Item No': 12, 'Item Code': 'FAK012', 'Item Name': 'Roller bandages (5cm x 5cm)', 'Quantity': 4, 'Stock': 4, 'Min Level': 2, 'Unit': 'rolls', 'Status': 'Available', 'Location': 'First Aid Box', 'Expiry Date': '2026-06-30'},
                {'Item No': 13, 'Item Code': 'FAK013', 'Item Name': 'First aid dressing (5cm x 5cm)', 'Quantity': 4, 'Stock': 4, 'Min Level': 2, 'Unit': 'pieces', 'Status': 'Available', 'Location': 'First Aid Box', 'Expiry Date': '2025-08-31'},
                {'Item No': 14, 'Item Code': 'FAK014', 'Item Name': 'First aid dressing (7.5cm x 7.5cm)', 'Quantity': 1, 'Stock': 1, 'Min Level': 1, 'Unit': 'pieces', 'Status': 'Available', 'Location': 'First Aid Box', 'Expiry Date': '2025-08-31'},
                {'Item No': 15, 'Item Code': 'FAK015', 'Item Name': 'First aid dressing (10cm x 10cm)', 'Quantity': 1, 'Stock': 1, 'Min Level': 1, 'Unit': 'pieces', 'Status': 'Available', 'Location': 'First Aid Box', 'Expiry Date': '2025-08-31'},
                {'Item No': 16, 'Item Code': 'FAK016', 'Item Name': 'First aid dressing (7.5cm x 20cm)', 'Quantity': 1, 'Stock': 1, 'Min Level': 1, 'Unit': 'pieces', 'Status': 'Available', 'Location': 'First Aid Box', 'Expiry Date': '2025-08-31'},
                {'Item No': 17, 'Item Code': 'FAK017', 'Item Name': 'Eye wash (100ml bottle)', 'Quantity': 1, 'Stock': 1, 'Min Level': 1, 'Unit': 'bottles', 'Status': 'Available', 'Location': 'First Aid Box', 'Expiry Date': '2025-04-30'},
                {'Item No': 18, 'Item Code': 'FAK018', 'Item Name': 'Non-allergic adhesive tape', 'Quantity': 1, 'Stock': 1, 'Min Level': 1, 'Unit': 'rolls', 'Status': 'Available', 'Location': 'First Aid Box', 'Expiry Date': '2026-12-31'},
                {'Item No': 19, 'Item Code': 'FAK019', 'Item Name': 'Triangular bandages', 'Quantity': 4, 'Stock': 4, 'Min Level': 2, 'Unit': 'pieces', 'Status': 'Available', 'Location': 'First Aid Box', 'Expiry Date': '2026-09-30'},
                {'Item No': 20, 'Item Code': 'FAK020', 'Item Name': 'Safety pins', 'Quantity': 1, 'Stock': 1, 'Min Level': 1, 'Unit': 'pack', 'Status': 'Available', 'Location': 'First Aid Box', 'Expiry Date': '2030-01-01'},
                {'Item No': 21, 'Item Code': 'FAK021', 'Item Name': 'Pair of scissors', 'Quantity': 1, 'Stock': 1, 'Min Level': 1, 'Unit': 'pieces', 'Status': 'Available', 'Location': 'First Aid Box', 'Expiry Date': '2030-01-01'},
                {'Item No': 22, 'Item Code': 'FAK022', 'Item Name': 'Surgical gloves (Medium)', 'Quantity': 4, 'Stock': 4, 'Min Level': 2, 'Unit': 'pairs', 'Status': 'Available', 'Location': 'First Aid Box', 'Expiry Date': '2025-03-31'},
                {'Item No': 23, 'Item Code': 'FAK023', 'Item Name': 'Resuscitation mask', 'Quantity': 1, 'Stock': 1, 'Min Level': 1, 'Unit': 'pieces', 'Status': 'Available', 'Location': 'First Aid Box', 'Expiry Date': '2027-01-31'},
                {'Item No': 24, 'Item Code': 'FAK024', 'Item Name': 'Instant ice pack', 'Quantity': 4, 'Stock': 4, 'Min Level': 2, 'Unit': 'pieces', 'Status': 'Available', 'Location': 'First Aid Box', 'Expiry Date': '2026-02-28'},
                {'Item No': 25, 'Item Code': 'FAK025', 'Item Name': 'First aid guidance card', 'Quantity': 1, 'Stock': 1, 'Min Level': 1, 'Unit': 'pieces', 'Status': 'Available', 'Location': 'First Aid Box', 'Expiry Date': '2030-01-01'}
            ])
        
        try:
            # Load medical equipment
            self.medical_equipment = pd.read_excel(self.excel_file, sheet_name='Medical Equipment')
        except:
            self.medical_equipment = pd.DataFrame([
                {'Equipment ID': 'MED001', 'Equipment Name': 'AED (Automated External Defibrillator)', 'Location': 'Main Reception', 'Last Service': '2024-06-15', 'Next Service': '2024-12-15', 'Status': 'Active'},
                {'Equipment ID': 'MED002', 'Equipment Name': 'Blood Pressure Monitor', 'Location': 'Medical Room', 'Last Service': '2024-07-01', 'Next Service': '2025-01-01', 'Status': 'Active'},
                {'Equipment ID': 'MED003', 'Equipment Name': 'Portable Oxygen Kit', 'Location': 'Medical Room', 'Last Service': '2024-05-20', 'Next Service': '2024-11-20', 'Status': 'Active'},
                {'Equipment ID': 'MED004', 'Equipment Name': 'Stretcher', 'Location': 'Medical Room', 'Last Service': '2024-08-01', 'Next Service': '2025-02-01', 'Status': 'Active'},
                {'Equipment ID': 'MED005', 'Equipment Name': 'Emergency Response Kit', 'Location': 'Security Office', 'Last Service': '2024-07-15', 'Next Service': '2025-01-15', 'Status': 'Active'}
            ])
        
        try:
            # Load patient treatment records (based on paramedic forms)
            self.patient_records = pd.read_excel(self.excel_file, sheet_name='Patient Treatment Records')
        except:
            # Load real medication data from August 2025
            try:
                # Try to load from the medication data Excel file directly
                medication_df = pd.read_excel('medication_data.xlsx', sheet_name='AUG', header=None)
                
                # Extract real medication records and convert to patient treatment record format
                real_records = []
                for i, row in medication_df.iterrows():
                    if pd.notna(row[0]) and 'Week Ending' not in str(row[0]) and 'Date' not in str(row[0]) and 'MEDICATION' not in str(row[0]):
                        try:
                            date_str = str(row[0])
                            if '2025' in date_str and pd.notna(row[2]):  # Has date and name
                                # Generate record ID
                                record_id = f"PTR-{date_str.split()[0].replace('-', '')}-{str(uuid.uuid4())[:8].upper()}"
                                
                                real_records.append({
                                    'Record ID': record_id,
                                    'Date': date_str.split()[0] if ' ' in date_str else date_str,
                                    'Time': '09:00',  # Default time for medication records
                                    'Location': 'Medical Office',
                                    'Patient Name': str(row[2]) if pd.notna(row[2]) else 'Unknown',
                                    'Age': '',
                                    'Gender': '',
                                    'Contact Number': '',
                                    'Department': str(row[4]) if pd.notna(row[4]) else 'Unknown',
                                    'What happened?': 'Requested medication for symptoms',
                                    'What is the injury?': 'Medical symptoms requiring medication',
                                    'Name of First Aider': str(row[5]) if pd.notna(row[5]) else 'Medical Staff',
                                    'Treatment Given': f"Administered: {str(row[3])}" if pd.notna(row[3]) and str(row[3]) != 'nan' else 'Medication provided',
                                    'Stock replaced by': str(row[5]) if pd.notna(row[5]) else 'Medical Staff',
                                    'Signature of First Aider': str(row[5]) if pd.notna(row[5]) else 'Medical Staff',
                                    'Date of stock replaced': date_str.split()[0] if ' ' in date_str else date_str,
                                    'SAFETY REPRESENTATIVE': 'Facilities Team',
                                    'INVESTIGATOR': '',
                                    'Risk Assessment': 'Low risk - medication administration',
                                    'Assessor': str(row[5]) if pd.notna(row[5]) else 'Medical Staff',
                                    'Section & Date': f"{str(row[4]) if pd.notna(row[4]) else 'Unknown'} - {date_str.split()[0] if ' ' in date_str else date_str}",
                                    'Reported to SHE Committee': 'No',
                                    'Follow Up Required': 'No',
                                    'Status': 'Completed',
                                    'Created By': 'Medical System',
                                    'Created Date': f"{date_str.split()[0] if ' ' in date_str else date_str} 09:00"
                                })
                        except:
                            continue
                
                self.patient_records = pd.DataFrame(real_records if real_records else [], columns=[
                    # Basic Information
                    'Record ID', 'Date', 'Time', 'Location', 
                    
                    # Patient Information (from both PDF forms)
                    'Patient Name', 'Age', 'Gender', 'Contact Number',
                    'Department', 'What happened?', 'What is the injury?',
                    
                    # Treatment Information (FIRST AID PATIENT REPORT REGISTER - Treatment Records)
                    'Name of First Aider', 'Treatment Given',
                    
                    # Stock/Equipment Used (as per paramedic form 2)
                    'Stock replaced by', 'Signature of First Aider',
                    'Date of stock replaced', 
                    
                    # Safety/Investigation section
                    'SAFETY REPRESENTATIVE', 'INVESTIGATOR',
                    
                    # Additional fields for comprehensive tracking
                    'Risk Assessment', 'Assessor', 'Section & Date',
                    'Reported to SHE Committee', 'Follow Up Required',
                    'Status', 'Created By', 'Created Date'
                ])
                
                print(f"Loaded {len(self.patient_records)} real medication records from August 2025")
                
            except Exception as e:
                print(f"Could not load medication data: {e}")
                # Fallback to empty structure
                self.patient_records = pd.DataFrame(columns=[
                    # Basic Information
                    'Record ID', 'Date', 'Time', 'Location', 
                    
                    # Patient Information (from both PDF forms)
                    'Patient Name', 'Age', 'Gender', 'Contact Number',
                    'Department', 'What happened?', 'What is the injury?',
                    
                    # Treatment Information (FIRST AID PATIENT REPORT REGISTER - Treatment Records)
                    'Name of First Aider', 'Treatment Given',
                    
                    # Stock/Equipment Used (as per paramedic form 2)
                    'Stock replaced by', 'Signature of First Aider',
                    'Date of stock replaced', 
                    
                    # Safety/Investigation section
                    'SAFETY REPRESENTATIVE', 'INVESTIGATOR',
                    
                    # Additional fields for comprehensive tracking
                    'Risk Assessment', 'Assessor', 'Section & Date',
                    'Reported to SHE Committee', 'Follow Up Required',
                    'Status', 'Created By', 'Created Date'
                ])
        
        # Define incident types and severity levels
        self.incident_types = [
            'Cut/Laceration', 'Burn', 'Bruise/Contusion', 'Sprain/Strain', 
            'Fracture', 'Allergic Reaction', 'Breathing Difficulty', 'Chest Pain',
            'Fainting/Collapse', 'Eye Injury', 'Chemical Exposure', 'Electric Shock',
            'Heat Exhaustion', 'Seizure', 'Cardiac Event', 'Other'
        ]
        
        self.severity_levels = [
            'Minor - First Aid Only', 'Moderate - Medical Attention Recommended', 
            'Serious - Hospital Treatment Required', 'Critical - Emergency Services Called'
        ]
        
        self.body_parts = [
            'Head', 'Eyes', 'Neck', 'Chest', 'Back', 'Arms', 'Hands/Fingers',
            'Abdomen', 'Legs', 'Feet/Toes', 'Multiple Areas', 'Other'
        ]
    
    def create_incident_report(self, incident_data):
        """Create a new medical incident report"""
        incident_id = f"INC-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        new_incident = {
            'Incident ID': incident_id,
            'Date': incident_data.get('date', datetime.now().strftime('%Y-%m-%d')),
            'Time': incident_data.get('time', datetime.now().strftime('%H:%M')),
            'Patient Name': incident_data.get('patient_name', ''),
            'Employee ID': incident_data.get('employee_id', ''),
            'Department': incident_data.get('department', ''),
            'Age': incident_data.get('age', ''),
            'Gender': incident_data.get('gender', ''),
            'Contact Number': incident_data.get('contact', ''),
            'Incident Type': incident_data.get('incident_type', ''),
            'Location of Incident': incident_data.get('location', ''),
            'Description': incident_data.get('description', ''),
            'Body Part Affected': incident_data.get('body_part', ''),
            'Injury Type': incident_data.get('injury_type', ''),
            'Severity Level': incident_data.get('severity', ''),
            'Treatment Given': incident_data.get('treatment', ''),
            'Medication Administered': incident_data.get('medication', ''),
            'Vital Signs': incident_data.get('vital_signs', ''),
            'First Aider Name': incident_data.get('first_aider', ''),
            'First Aider Cert': incident_data.get('first_aider_cert', ''),
            'Witness Name': incident_data.get('witness', ''),
            'Referred to Hospital': incident_data.get('hospital_referral', 'No'),
            'Hospital Name': incident_data.get('hospital_name', ''),
            'Follow Up Required': incident_data.get('follow_up_required', 'No'),
            'Follow Up Date': incident_data.get('follow_up_date', ''),
            'SHE Committee Reported': incident_data.get('she_reported', 'No'),
            'Photos': self._process_photos(incident_data.get('photos', [])),
            'Additional Notes': incident_data.get('notes', ''),
            'Status': 'Open',
            'Created By': incident_data.get('created_by', 'System'),
            'Created Date': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        
        # Add to DataFrame
        new_row = pd.DataFrame([new_incident])
        self.incident_reports = pd.concat([self.incident_reports, new_row], ignore_index=True)
        
        # Save to Excel
        self._save_to_excel()
        
        return incident_id
    
    def update_medical_inventory(self, item_code, quantity_used, notes=''):
        """Update medical inventory after use"""
        mask = self.medical_inventory['Item Code'] == item_code
        if mask.any():
            idx = self.medical_inventory.index[mask][0]
            current_stock = self.medical_inventory.at[idx, 'Stock']
            new_stock = max(0, current_stock - quantity_used)
            self.medical_inventory.at[idx, 'Stock'] = new_stock
            
            # Log the usage
            usage_log = {
                'Date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'Item': self.medical_inventory.at[idx, 'Item Name'],
                'Quantity Used': quantity_used,
                'Remaining': new_stock,
                'Notes': notes
            }
            
            # Save changes
            self._save_to_excel()
            return True
        return False
    
    def get_low_stock_items(self):
        """Get items that are below minimum level"""
        low_stock = self.medical_inventory[
            self.medical_inventory['Stock'] <= self.medical_inventory['Min Level']
        ].copy()
        return low_stock
    
    def get_expiring_items(self, days_ahead=30):
        """Get items expiring within specified days"""
        cutoff_date = datetime.now() + timedelta(days=days_ahead)
        
        # Convert expiry dates to datetime
        self.medical_inventory['Expiry Date'] = pd.to_datetime(self.medical_inventory['Expiry Date'])
        
        expiring = self.medical_inventory[
            self.medical_inventory['Expiry Date'] <= cutoff_date
        ].copy()
        
        # Calculate days until expiry
        expiring['Days Until Expiry'] = (expiring['Expiry Date'] - datetime.now()).dt.days
        
        return expiring
    
    def get_dashboard_stats(self):
        """Get medical dashboard statistics"""
        total_incidents = len(self.incident_reports)
        open_incidents = len(self.incident_reports[self.incident_reports['Status'] == 'Open'])
        
        # Recent incidents (last 30 days)
        recent_date = datetime.now() - timedelta(days=30)
        try:
            recent_incidents = self.incident_reports[
                pd.to_datetime(self.incident_reports['Created Date'], format='mixed', dayfirst=True) >= recent_date
            ]
        except:
            recent_incidents = self.incident_reports  # Fallback to all incidents if date parsing fails
        
        # Critical incidents
        critical_incidents = len(self.incident_reports[
            self.incident_reports['Severity Level'].str.contains('Critical', na=False)
        ])
        
        # Low stock count
        low_stock_count = len(self.get_low_stock_items())
        
        # Expiring items count
        expiring_count = len(self.get_expiring_items())
        
        # Most common incident types
        incident_types = self.incident_reports['Incident Type'].value_counts().head(5).to_dict()
        
        # Department statistics
        dept_stats = self.incident_reports['Department'].value_counts().head(5).to_dict()
        
        # Patient records statistics  
        total_patient_records = len(self.patient_records)
        active_patient_records = len(self.patient_records[self.patient_records['Status'] == 'Completed'])  # Medication records are "Completed"
        
        # Recent patient records (last 30 days)
        try:
            recent_patient_records = self.patient_records[
                pd.to_datetime(self.patient_records['Created Date'], format='mixed', dayfirst=True) >= recent_date
            ]
        except:
            recent_patient_records = self.patient_records  # Fallback to all patient records if date parsing fails
        
        return {
            'total_incidents': total_incidents,
            'open_incidents': open_incidents,
            'recent_incidents': len(recent_incidents),
            'critical_incidents': critical_incidents,
            'low_stock_items': low_stock_count,
            'expiring_items': expiring_count,
            'total_medical_items': len(self.medical_inventory),
            'equipment_count': len(self.medical_equipment),
            'total_patient_records': total_patient_records,
            'active_patient_records': active_patient_records,
            'recent_patient_records': len(recent_patient_records),
            'incident_types': incident_types,
            'department_stats': dept_stats
        }
    
    def search_incidents(self, query='', filters=None):
        """Search through incident reports"""
        df = self.incident_reports.copy()
        
        if query:
            search_fields = ['Patient Name', 'Department', 'Incident Type', 'Description', 'Treatment Given']
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
    
    def create_patient_record(self, record_data):
        """Create a new patient treatment record matching paramedic forms"""
        record_id = f"PTR-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        new_record = {
            # Basic Information
            'Record ID': record_id,
            'Date': record_data.get('date', datetime.now().strftime('%Y-%m-%d')),
            'Time': record_data.get('time', datetime.now().strftime('%H:%M')),
            'Location': record_data.get('location', ''),
            
            # Patient Information (from both PDF forms)
            'Patient Name': record_data.get('patient_name', ''),
            'Age': record_data.get('age', ''),
            'Gender': record_data.get('gender', ''),
            'Contact Number': record_data.get('contact', ''),
            'Department': record_data.get('department', ''),
            'What happened?': record_data.get('what_happened', ''),
            'What is the injury?': record_data.get('what_injury', ''),
            
            # Treatment Information
            'Name of First Aider': record_data.get('first_aider_name', ''),
            'Treatment Given': record_data.get('treatment_given', ''),
            
            # Stock/Equipment Used
            'Stock replaced by': record_data.get('stock_replaced_by', ''),
            'Signature of First Aider': record_data.get('first_aider_signature', ''),
            'Date of stock replaced': record_data.get('stock_date', ''),
            
            # Safety/Investigation section
            'SAFETY REPRESENTATIVE': record_data.get('safety_rep', ''),
            'INVESTIGATOR': record_data.get('investigator', ''),
            
            # Additional tracking fields
            'Risk Assessment': record_data.get('risk_assessment', ''),
            'Assessor': record_data.get('assessor', ''),
            'Section & Date': record_data.get('section_date', ''),
            'Reported to SHE Committee': record_data.get('she_reported', 'No'),
            'Follow Up Required': record_data.get('follow_up_required', 'No'),
            'Status': record_data.get('status', 'Active'),
            'Created By': record_data.get('created_by', 'System'),
            'Created Date': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        
        # Add to DataFrame
        new_row = pd.DataFrame([new_record])
        self.patient_records = pd.concat([self.patient_records, new_row], ignore_index=True)
        
        # Save to Excel
        self._save_to_excel()
        
        return record_id
    
    def get_patient_records(self, limit=None, filters=None):
        """Get patient treatment records with optional filtering"""
        df = self.patient_records.copy()
        
        if filters:
            for field, value in filters.items():
                if field in df.columns and value:
                    if isinstance(value, list):
                        df = df[df[field].isin(value)]
                    else:
                        df = df[df[field].astype(str).str.contains(str(value), case=False, na=False)]
        
        # Sort by date (newest first)
        if 'Created Date' in df.columns:
            df = df.sort_values('Created Date', ascending=False)
        
        if limit:
            df = df.head(limit)
        
        return df
    
    def get_first_aid_kit_contents(self):
        """Get the complete first aid kit inventory as per paramedic forms"""
        # Return the 25 items from the first aid kit as specified in the paramedic forms
        return self.medical_inventory.copy()
    
    def update_patient_record_status(self, record_id, status, notes=''):
        """Update the status of a patient record"""
        mask = self.patient_records['Record ID'] == record_id
        if mask.any():
            idx = self.patient_records.index[mask][0]
            self.patient_records.at[idx, 'Status'] = status
            if notes:
                current_notes = self.patient_records.at[idx, 'Risk Assessment']
                self.patient_records.at[idx, 'Risk Assessment'] = f"{current_notes}\n{datetime.now().strftime('%Y-%m-%d')}: {notes}" if current_notes else f"{datetime.now().strftime('%Y-%m-%d')}: {notes}"
            
            self._save_to_excel()
            return True
        return False
    
    def _process_photos(self, photos):
        """Process and encode photos for storage"""
        if not photos:
            return ''
        
        photo_data = []
        for photo in photos:
            if isinstance(photo, str) and photo.startswith('data:image'):
                photo_data.append(photo)
        
        return json.dumps(photo_data)
    
    def _save_to_excel(self):
        """Save medical data back to Excel file"""
        try:
            with pd.ExcelWriter(self.excel_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                self.incident_reports.to_excel(writer, sheet_name='Medical Incidents', index=False)
                self.medical_inventory.to_excel(writer, sheet_name='Medical Inventory', index=False)
                self.medical_equipment.to_excel(writer, sheet_name='Medical Equipment', index=False)
                self.patient_records.to_excel(writer, sheet_name='Patient Treatment Records', index=False)
        except Exception as e:
            with pd.ExcelWriter(self.excel_file, engine='openpyxl') as writer:
                self.incident_reports.to_excel(writer, sheet_name='Medical Incidents', index=False)
                self.medical_inventory.to_excel(writer, sheet_name='Medical Inventory', index=False)
                self.medical_equipment.to_excel(writer, sheet_name='Medical Equipment', index=False)
                self.patient_records.to_excel(writer, sheet_name='Patient Treatment Records', index=False)

# Initialize the medical manager
def get_medical_manager():
    """Get or create Medical manager instance"""
    if not hasattr(get_medical_manager, 'instance'):
        get_medical_manager.instance = MedicalManager()
    return get_medical_manager.instance