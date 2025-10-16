#!/usr/bin/env python3
"""
Sign-Out Register Data Manager
Handles reading and processing the Sign-In/Out Register Excel data
"""

import pandas as pd
import numpy as np
from datetime import datetime, time
import os

class SignOutDataManager:
    def __init__(self, excel_file='signout_data_improved.xlsx'):
        self.excel_file = excel_file
        self.df = None
        self.load_data()
    
    def load_data(self):
        """Load and clean the sign-out register data"""
        try:
            # Read the Excel file - check if headers are in row 1 (0-indexed)
            # First try to read normally, then check if we need to use header=1
            test_df = pd.read_excel(self.excel_file, nrows=2)

            # If first column name looks like a title, use header=1
            if 'Derivco' in str(test_df.columns[0]) or 'Unnamed' in str(test_df.columns[0]):
                self.df = pd.read_excel(self.excel_file, header=1)
            else:
                self.df = pd.read_excel(self.excel_file)
            
            # Clean up the data
            self.df = self.df.dropna(how='all')  # Remove completely empty rows
            
            # Apply column mapping if needed (for backward compatibility)
            if 'Item_Name' not in self.df.columns:
                col_mapping = {
                    'Item Name': 'Item_Name',
                    'Borrower Name': 'Borrower_Name',
                    'WO/REQ No.': 'WO_REQ_No',
                    'Project Type': 'Project_Type',
                    'Destination Department / Area': 'Department_Area',
                    'Date/Time Out': 'DateTime_Out',
                    'Expected Return Date': 'Expected_Return',
                    'Date/Time Returned': 'DateTime_Returned',
                    'Notes (e.g., tool unavailable, purpose of use)': 'Notes'
                }
                
                for old_col, new_col in col_mapping.items():
                    if old_col in self.df.columns:
                        self.df.rename(columns={old_col: new_col}, inplace=True)
            
            # Always clean datetime columns and process data
            if len(self.df) > 0:
                self.df = self._clean_datetime_columns()
                print(f"Loaded {len(self.df)} sign-out records")
            else:
                print("No data found in the Excel file")
                self.df = pd.DataFrame()
                
        except Exception as e:
            print(f"Error loading sign-out data: {e}")
            self.df = pd.DataFrame()
    
    def _clean_datetime_columns(self):
        """Clean and standardize datetime columns"""
        df = self.df.copy()
        
        # Define date columns to clean
        date_columns = ['DateTime_Out', 'Expected_Return', 'DateTime_Returned']
        
        for col in date_columns:
            if col in df.columns:
                # Convert to string first to handle various formats
                df[col] = df[col].astype(str)
                # Replace 'Used' and other non-date values with NaN
                df.loc[df[col].isin(['Used', 'nan', 'NaT', 'None']), col] = np.nan
        
        return df
    
    def get_all_transactions(self):
        """Get all sign-out transactions"""
        if self.df is None or self.df.empty:
            return []
        
        transactions = []
        for _, row in self.df.iterrows():
            # Skip rows where Item_Name is NaN
            if pd.isna(row.get('Item_Name')) or row.get('Item_Name') == 'nan':
                continue
                
            transaction = {
                'id': len(transactions) + 1,
                'item_name': str(row.get('Item_Name', '')),
                'borrower_name': str(row.get('Borrower_Name', '')),
                'wo_req_no': str(row.get('WO_REQ_No', '')),
                'project_type': str(row.get('Project_Type', '')),
                'department_area': str(row.get('Department_Area', '')),
                'datetime_out': str(row.get('DateTime_Out', '')),
                'expected_return': str(row.get('Expected_Return', '')),
                'datetime_returned': str(row.get('DateTime_Returned', '')),
                'notes': str(row.get('Notes', '')),
                'status': self._determine_status(row)
            }
            
            # Clean up 'nan' strings
            for key, value in transaction.items():
                if value == 'nan':
                    transaction[key] = ''
            
            transactions.append(transaction)
        
        return transactions
    
    def _determine_status(self, row):
        """Determine the status of a transaction (Returned, Outstanding, etc.)"""
        returned = str(row.get('DateTime_Returned', ''))
        expected = str(row.get('Expected_Return', ''))
        
        if returned and returned not in ['nan', '', 'Used']:
            return 'Returned'
        elif returned == 'Used':
            return 'Used/Consumed'
        elif expected == 'Same Day':
            return 'Same Day Return'
        else:
            return 'Outstanding'
    
    def get_dashboard_stats(self):
        """Get statistics for the sign-out dashboard"""
        if self.df is None or self.df.empty:
            return {
                'total_transactions': 0,
                'outstanding_items': 0,
                'returned_today': 0,
                'overdue_items': 0,
                'most_borrowed_items': [],
                'active_borrowers': []
            }
        
        transactions = self.get_all_transactions()
        
        # Calculate statistics
        total_transactions = len(transactions)
        outstanding_items = len([t for t in transactions if t['status'] == 'Outstanding'])
        returned_today = len([t for t in transactions if 'today' in t.get('datetime_returned', '').lower()])
        overdue_items = len([t for t in transactions if t['status'] == 'Outstanding' and t.get('expected_return') == 'Same Day'])
        
        # Most borrowed items
        item_counts = {}
        for t in transactions:
            item = t['item_name']
            if item:
                item_counts[item] = item_counts.get(item, 0) + 1
        
        most_borrowed = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        most_borrowed_items = [{'name': item, 'count': count} for item, count in most_borrowed]
        
        # Active borrowers
        borrower_counts = {}
        for t in transactions:
            if t['status'] == 'Outstanding':
                borrower = t['borrower_name']
                if borrower:
                    borrower_counts[borrower] = borrower_counts.get(borrower, 0) + 1
        
        active_borrowers = [{'name': name, 'items': count} for name, count in borrower_counts.items()]
        
        return {
            'total_transactions': total_transactions,
            'outstanding_items': outstanding_items,
            'returned_today': returned_today,
            'overdue_items': overdue_items,
            'most_borrowed_items': most_borrowed_items,
            'active_borrowers': active_borrowers
        }
    
    def get_recent_transactions(self, limit=10):
        """Get the most recent transactions"""
        transactions = self.get_all_transactions()
        # Return the most recent transactions (assuming they're in chronological order)
        return transactions[-limit:] if len(transactions) > limit else transactions
    
    def get_transactions_by_month(self, months=['August', 'September'], year=2024):
        """Get transactions for specific months"""
        import re
        from dateutil import parser
        
        transactions = self.get_all_transactions()
        filtered_transactions = []
        
        for transaction in transactions:
            datetime_out = transaction.get('datetime_out', '')
            if not datetime_out or datetime_out == 'nan' or datetime_out == '':
                continue
            
            try:
                # Try to parse the date string
                # Handle various date formats that might be in the Excel
                date_str = str(datetime_out).strip()
                
                # Skip obviously non-date values
                if date_str.lower() in ['nan', 'none', '', 'used']:
                    continue
                
                # Try to parse the date
                parsed_date = None
                
                # Common date patterns to try
                date_patterns = [
                    r'(\d{1,2})/(\d{1,2})/(\d{4})',  # MM/DD/YYYY or DD/MM/YYYY
                    r'(\d{4})-(\d{1,2})-(\d{1,2})',  # YYYY-MM-DD
                    r'(\d{1,2}-\w{3}-\d{2,4})',      # DD-MMM-YY or DD-MMM-YYYY
                ]
                
                # Try different parsing approaches
                try:
                    parsed_date = parser.parse(date_str, dayfirst=True)
                except:
                    # If dateutil fails, try manual pattern matching
                    for pattern in date_patterns:
                        match = re.search(pattern, date_str)
                        if match:
                            try:
                                parsed_date = parser.parse(date_str, dayfirst=True)
                                break
                            except:
                                continue
                
                if parsed_date:
                    month_name = parsed_date.strftime('%B')  # Full month name
                    transaction_year = parsed_date.year
                    
                    # Check if transaction is in the target months and year
                    if month_name in months and transaction_year == year:
                        filtered_transactions.append(transaction)
                        
            except Exception as e:
                # Skip problematic dates but log them for debugging
                print(f"Could not parse date '{datetime_out}': {e}")
                continue
        
        return filtered_transactions
    
    def get_filtered_dashboard_stats(self, transactions):
        """Get dashboard statistics for a filtered set of transactions"""
        if not transactions:
            return {
                'total_transactions': 0,
                'outstanding_items': 0,
                'returned_today': 0,
                'overdue_items': 0,
                'most_borrowed_items': [],
                'active_borrowers': []
            }
        
        # Calculate statistics based on the filtered transactions
        total_transactions = len(transactions)
        outstanding_items = len([t for t in transactions if t['status'] == 'Outstanding'])
        
        # For "returned today", let's count items returned in the last few days since we're looking at historical data
        from datetime import datetime, timedelta
        today = datetime.now()
        recent_days = today - timedelta(days=7)  # Last 7 days
        
        returned_recently = 0
        for t in transactions:
            if t['status'] == 'Returned' and t.get('datetime_returned'):
                try:
                    from dateutil import parser
                    returned_date = parser.parse(str(t['datetime_returned']), dayfirst=True)
                    if returned_date >= recent_days:
                        returned_recently += 1
                except:
                    continue
        
        # Calculate overdue items (Outstanding items with "Same Day" return expectation)
        overdue_items = len([t for t in transactions if t['status'] == 'Outstanding' and t.get('expected_return') == 'Same Day'])
        
        # Most borrowed items from filtered data
        item_counts = {}
        for t in transactions:
            item = t['item_name']
            if item:
                item_counts[item] = item_counts.get(item, 0) + 1
        
        most_borrowed = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        most_borrowed_items = [{'name': item, 'count': count} for item, count in most_borrowed]
        
        # Active borrowers from filtered outstanding items
        borrower_counts = {}
        for t in transactions:
            if t['status'] == 'Outstanding':
                borrower = t['borrower_name']
                if borrower:
                    borrower_counts[borrower] = borrower_counts.get(borrower, 0) + 1
        
        active_borrowers = [{'name': name, 'items': count} for name, count in borrower_counts.items()]
        
        return {
            'total_transactions': total_transactions,
            'outstanding_items': outstanding_items,
            'returned_today': returned_recently,
            'overdue_items': overdue_items,
            'most_borrowed_items': most_borrowed_items,
            'active_borrowers': active_borrowers
        }
    
    def get_outstanding_items(self):
        """Get all outstanding (not returned) items"""
        transactions = self.get_all_transactions()
        return [t for t in transactions if t['status'] == 'Outstanding']
    
    def search_transactions(self, query="", filters=None):
        """Search transactions by item name, borrower, or other criteria"""
        transactions = self.get_all_transactions()
        
        if not query and not filters:
            return transactions
        
        results = []
        query_lower = query.lower() if query else ""
        
        for transaction in transactions:
            # Text search across multiple fields
            searchable_text = f"{transaction['item_name']} {transaction['borrower_name']} {transaction['department_area']} {transaction['notes']}".lower()
            
            if query_lower and query_lower not in searchable_text:
                continue
            
            # Apply filters if provided
            if filters:
                if 'status' in filters and transaction['status'] != filters['status']:
                    continue
                if 'borrower' in filters and filters['borrower'] not in transaction['borrower_name']:
                    continue
                if 'department' in filters and filters['department'] not in transaction['department_area']:
                    continue
            
            results.append(transaction)
        
        return results
    
    def add_transaction(self, transaction_data):
        """Add a new sign-out transaction (placeholder for future functionality)"""
        # This would typically append to the Excel file
        # For now, return success
        return {
            'success': True,
            'message': 'Transaction added successfully',
            'transaction_id': len(self.get_all_transactions()) + 1
        }
    
    def return_item(self, transaction_id, return_notes=""):
        """Mark an item as returned (placeholder for future functionality)"""
        # This would typically update the Excel file
        return {
            'success': True,
            'message': f'Item from transaction {transaction_id} marked as returned',
            'return_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_compliance_analysis(self):
        """Get detailed compliance analysis for facilities management"""
        if self.df is None or self.df.empty:
            return {
                'missing_wo_count': 0,
                'missing_wo_percentage': 0,
                'unreturned_count': 0,
                'unreturned_percentage': 0,
                'total_transactions': 0,
                'missing_wo_transactions': [],
                'unreturned_tools': [],
                'estimated_tool_value': 0,
                'actual_vs_recorded_ratio': 5,
                'visible_productivity': 20
            }
        
        all_transactions = self.get_all_transactions()
        total_transactions = len(all_transactions)
        
        if total_transactions == 0:
            return {
                'missing_wo_count': 0,
                'missing_wo_percentage': 0,
                'unreturned_count': 0,
                'unreturned_percentage': 0,
                'total_transactions': 0,
                'missing_wo_transactions': [],
                'unreturned_tools': [],
                'estimated_tool_value': 0,
                'actual_vs_recorded_ratio': 5,
                'visible_productivity': 20
            }
        
        # Analyze missing WO/REQ numbers
        # Real analysis: supervisor names instead of proper work orders indicates missing WO/REQ
        supervisor_names = {
            'Erasmus Ngwane', 'Brindley Harrington', 'Not Provided', 'Not provided', 
            'not provided', 'N/A', 'n/a', 'None', 'none', ''
        }
        
        missing_wo_transactions = []
        for transaction in all_transactions:
            wo_req = transaction.get('wo_req_no', '').strip()
            
            # Check if WO/REQ is missing, a supervisor name, or clearly not a work order
            is_missing = False
            
            if not wo_req or wo_req.lower() in ['nan', 'none', 'null', '']:
                is_missing = True
            elif wo_req in supervisor_names:
                is_missing = True
            elif wo_req.replace(' ', '').isalpha() and len(wo_req.split()) <= 3:
                # Looks like a person's name (only letters, 1-3 words)
                is_missing = True
            elif not any(x in wo_req.upper() for x in ['WO', 'REQ', 'TICKET', '#']) and not any(c.isdigit() for c in wo_req):
                # No work order indicators and no numbers - likely supervisor name
                is_missing = True
                
            if is_missing:
                missing_wo_transactions.append(transaction)
        
        missing_wo_count = len(missing_wo_transactions)
        missing_wo_percentage = round((missing_wo_count / total_transactions) * 100, 1) if total_transactions > 0 else 0
        
        # Analyze unreturned tools
        unreturned_tools = []
        from datetime import datetime, timedelta
        
        for transaction in all_transactions:
            if transaction.get('status', '').lower() != 'returned':
                # Calculate days outstanding
                datetime_out = transaction.get('datetime_out')
                days_outstanding = 'Unknown'
                
                if datetime_out:
                    try:
                        if isinstance(datetime_out, str):
                            # Try to parse the date string
                            from dateutil import parser
                            out_date = parser.parse(datetime_out)
                        else:
                            out_date = datetime_out
                        
                        if isinstance(out_date, datetime):
                            days_outstanding = (datetime.now() - out_date).days
                        
                    except:
                        days_outstanding = 'Unknown'
                
                transaction_copy = transaction.copy()
                transaction_copy['days_outstanding'] = days_outstanding
                unreturned_tools.append(transaction_copy)
        
        unreturned_count = len(unreturned_tools)
        unreturned_percentage = round((unreturned_count / total_transactions) * 100, 1) if total_transactions > 0 else 0
        
        # Estimate tool value (average R500 per tool)
        estimated_tool_value = unreturned_count * 500
        
        # Calculate productivity metrics
        # With 87%+ missing WO/REQ, the situation is CRITICAL
        if missing_wo_percentage > 80:
            actual_vs_recorded_ratio = 10  # For every 1 properly logged task, 10 tasks might be done
            visible_productivity = 10  # Only 10% of work is properly logged in system
        elif missing_wo_percentage > 60:
            actual_vs_recorded_ratio = 8  # For every 1 recorded task, 8 might be done
            visible_productivity = 15  # Only 15% of work is visible in system
        elif missing_wo_percentage > 30:
            actual_vs_recorded_ratio = 5
            visible_productivity = 25
        else:
            actual_vs_recorded_ratio = 2
            visible_productivity = 50
        
        return {
            'missing_wo_count': missing_wo_count,
            'missing_wo_percentage': missing_wo_percentage,
            'unreturned_count': unreturned_count,
            'unreturned_percentage': unreturned_percentage,
            'total_transactions': total_transactions,
            'missing_wo_transactions': missing_wo_transactions[:20],  # Limit for display
            'unreturned_tools': unreturned_tools[:20],  # Limit for display
            'estimated_tool_value': f"{estimated_tool_value:,}",
            'actual_vs_recorded_ratio': actual_vs_recorded_ratio,
            'visible_productivity': visible_productivity
        }

# Global instance
_signout_manager = None

def get_signout_manager():
    """Get the global sign-out data manager instance"""
    global _signout_manager
    if _signout_manager is None:
        _signout_manager = SignOutDataManager()
    return _signout_manager

def reload_signout_data():
    """Reload the sign-out data from Excel file"""
    global _signout_manager
    _signout_manager = SignOutDataManager()
    return _signout_manager

# Management Analytics Methods
class ManagementAnalytics:
    def __init__(self, signout_manager):
        self.signout_manager = signout_manager
        self.transactions = signout_manager.get_all_transactions()
        
    def get_stewardship_scorecard(self, filtered_transactions=None):
        """Calculate individual stewardship scores and accountability metrics"""
        transactions = filtered_transactions or self.transactions
        
        borrower_stats = {}
        
        for transaction in transactions:
            borrower = transaction.get('borrower_name', '').strip()
            if not borrower:
                continue
                
            if borrower not in borrower_stats:
                borrower_stats[borrower] = {
                    'total_borrowed': 0,
                    'returned': 0,
                    'outstanding': 0,
                    'used_consumed': 0,
                    'same_day': 0,
                    'overdue_count': 0,
                    'no_wo_number': 0,
                    'return_times': [],
                    'stewardship_score': 0
                }
            
            stats = borrower_stats[borrower]
            stats['total_borrowed'] += 1
            
            # Count by status
            status = transaction['status']
            if status == 'Returned':
                stats['returned'] += 1
            elif status == 'Outstanding':
                stats['outstanding'] += 1
            elif status == 'Used/Consumed':
                stats['used_consumed'] += 1
            elif status == 'Same Day Return':
                stats['same_day'] += 1
                
            # Check for missing WO number
            wo_number = transaction.get('wo_req_no', '').strip()
            if not wo_number or wo_number.lower() in ['nan', 'not provided', 'none', '']:
                stats['no_wo_number'] += 1
                
            # Check for overdue (Outstanding + Same Day expected)
            if status == 'Outstanding' and transaction.get('expected_return') == 'Same Day':
                stats['overdue_count'] += 1
        
        # Calculate stewardship scores
        for borrower, stats in borrower_stats.items():
            if stats['total_borrowed'] == 0:
                continue
                
            # Score calculation (0-100)
            return_rate = (stats['returned'] + stats['used_consumed'] + stats['same_day']) / stats['total_borrowed']
            wo_compliance = (stats['total_borrowed'] - stats['no_wo_number']) / stats['total_borrowed']
            overdue_penalty = min(stats['overdue_count'] * 5, 30)  # Max 30 point penalty
            
            base_score = (return_rate * 60) + (wo_compliance * 40)  # Return rate weighted more
            final_score = max(0, base_score - overdue_penalty)
            
            stats['return_rate'] = return_rate * 100
            stats['wo_compliance_rate'] = wo_compliance * 100
            stats['stewardship_score'] = round(final_score, 1)
        
        return dict(sorted(borrower_stats.items(), key=lambda x: x[1]['stewardship_score'], reverse=True))
    
    def get_work_order_compliance(self, filtered_transactions=None):
        """Analyze work order compliance and tracking"""
        transactions = filtered_transactions or self.transactions
        
        total_transactions = len(transactions)
        missing_wo = 0
        valid_wo = 0
        wo_patterns = {}
        department_compliance = {}
        
        for transaction in transactions:
            wo_number = transaction.get('wo_req_no', '').strip()
            department = transaction.get('department_area', '').strip()
            
            if department not in department_compliance:
                department_compliance[department] = {'total': 0, 'with_wo': 0}
            
            department_compliance[department]['total'] += 1
            
            if not wo_number or wo_number.lower() in ['nan', 'none', '', 'not provided']:
                missing_wo += 1
            else:
                valid_wo += 1
                department_compliance[department]['with_wo'] += 1
                
                # Analyze WO patterns
                if wo_number.startswith('WO'):
                    wo_patterns['Work Order'] = wo_patterns.get('Work Order', 0) + 1
                elif wo_number.startswith('REQ'):
                    wo_patterns['Request'] = wo_patterns.get('Request', 0) + 1
                elif wo_number.isdigit():
                    wo_patterns['Numeric'] = wo_patterns.get('Numeric', 0) + 1
                else:
                    wo_patterns['Other'] = wo_patterns.get('Other', 0) + 1
        
        # Calculate compliance rates by department
        for dept_data in department_compliance.values():
            if dept_data['total'] > 0:
                dept_data['compliance_rate'] = (dept_data['with_wo'] / dept_data['total']) * 100
            else:
                dept_data['compliance_rate'] = 0
        
        return {
            'total_transactions': total_transactions,
            'missing_wo': missing_wo,
            'valid_wo': valid_wo,
            'compliance_rate': (valid_wo / total_transactions * 100) if total_transactions > 0 else 0,
            'wo_patterns': wo_patterns,
            'department_compliance': department_compliance,
            'estimated_untracked_value': missing_wo * 150  # Assume R150 avg tool value
        }
    
    def get_financial_impact(self, filtered_transactions=None):
        """Calculate financial impact of non-returns and inefficiencies"""
        transactions = filtered_transactions or self.transactions
        
        # Estimated tool values (you can adjust these)
        tool_values = {
            'Cordless Drill': 800,
            'Step Ladder': 350,
            'Network Cable': 50,
            'Ladder': 400,
            'Janus Plug': 25,
            'default': 150  # Default value for unknown items
        }
        
        outstanding_value = 0
        replacement_costs = 0
        outstanding_items = []
        
        for transaction in transactions:
            if transaction['status'] == 'Outstanding':
                item_name = transaction['item_name']
                value = tool_values.get(item_name, tool_values['default'])
                outstanding_value += value
                outstanding_items.append({
                    'item': item_name,
                    'borrower': transaction['borrower_name'],
                    'value': value,
                    'days_out': self._calculate_days_outstanding(transaction)
                })
        
        # Calculate replacement costs for long overdue items
        for item in outstanding_items:
            if item['days_out'] > 14:  # Over 2 weeks
                replacement_costs += item['value']
        
        return {
            'outstanding_value': outstanding_value,
            'replacement_costs': replacement_costs,
            'total_financial_risk': outstanding_value + replacement_costs,
            'outstanding_items': outstanding_items,
            'avg_item_value': outstanding_value / len(outstanding_items) if outstanding_items else 0
        }
    
    def get_management_insights(self, filtered_transactions=None):
        """Generate management insights and trends"""
        transactions = filtered_transactions or self.transactions
        
        # Usage patterns
        daily_usage = {}
        hourly_usage = {}
        item_popularity = {}
        department_usage = {}
        
        for transaction in transactions:
            datetime_out = transaction.get('datetime_out', '')
            item_name = transaction.get('item_name', '')
            department = transaction.get('department_area', '')
            
            # Parse datetime for patterns
            try:
                from dateutil import parser
                parsed_date = parser.parse(str(datetime_out), dayfirst=True)
                day_name = parsed_date.strftime('%A')
                hour = parsed_date.hour
                
                daily_usage[day_name] = daily_usage.get(day_name, 0) + 1
                hourly_usage[hour] = hourly_usage.get(hour, 0) + 1
            except:
                pass
            
            # Item popularity
            if item_name:
                item_popularity[item_name] = item_popularity.get(item_name, 0) + 1
            
            # Department usage
            if department:
                department_usage[department] = department_usage.get(department, 0) + 1
        
        # Find peak times
        peak_day = max(daily_usage.items(), key=lambda x: x[1]) if daily_usage else ('N/A', 0)
        peak_hour = max(hourly_usage.items(), key=lambda x: x[1]) if hourly_usage else (0, 0)
        
        return {
            'daily_usage': daily_usage,
            'hourly_usage': hourly_usage,
            'peak_day': peak_day,
            'peak_hour': peak_hour,
            'most_popular_items': sorted(item_popularity.items(), key=lambda x: x[1], reverse=True)[:10],
            'department_usage': department_usage,
            'usage_efficiency': self._calculate_usage_efficiency(transactions)
        }
    
    def get_alerts_notifications(self, filtered_transactions=None):
        """Generate alerts and notifications for management"""
        transactions = filtered_transactions or self.transactions
        alerts = []
        
        # High-risk borrowers (>5 outstanding)
        borrower_outstanding = {}
        for transaction in transactions:
            if transaction['status'] == 'Outstanding':
                borrower = transaction['borrower_name']
                borrower_outstanding[borrower] = borrower_outstanding.get(borrower, 0) + 1
        
        for borrower, count in borrower_outstanding.items():
            if count >= 5:
                alerts.append({
                    'type': 'HIGH_RISK_BORROWER',
                    'severity': 'HIGH',
                    'message': f'{borrower} has {count} outstanding items',
                    'action_required': 'Contact for immediate return'
                })
        
        # Overdue items
        overdue_count = len([t for t in transactions if t['status'] == 'Outstanding' and t.get('expected_return') == 'Same Day'])
        if overdue_count > 0:
            alerts.append({
                'type': 'OVERDUE_ITEMS',
                'severity': 'MEDIUM',
                'message': f'{overdue_count} items are overdue (Same Day return)',
                'action_required': 'Follow up on returns'
            })
        
        # Low WO compliance
        wo_analysis = self.get_work_order_compliance(transactions)
        if wo_analysis['compliance_rate'] < 70:
            alerts.append({
                'type': 'LOW_WO_COMPLIANCE',
                'severity': 'MEDIUM',
                'message': f'Work Order compliance at {wo_analysis["compliance_rate"]:.1f}%',
                'action_required': 'Improve WO tracking process'
            })
        
        return sorted(alerts, key=lambda x: x['severity'], reverse=True)
    
    def get_policy_compliance(self, filtered_transactions=None):
        """Track policy compliance and adherence"""
        transactions = filtered_transactions or self.transactions
        
        total = len(transactions)
        compliance_metrics = {
            'proper_checkout': 0,  # Has all required fields
            'wo_number_provided': 0,
            'return_on_time': 0,
            'condition_noted': 0
        }
        
        violations = []
        
        for transaction in transactions:
            # Check for proper checkout (all required fields)
            required_fields = ['item_name', 'borrower_name', 'department_area']
            if all(transaction.get(field) and str(transaction.get(field)).strip() not in ['', 'nan'] 
                   for field in required_fields):
                compliance_metrics['proper_checkout'] += 1
            else:
                violations.append({
                    'transaction_id': transaction.get('id'),
                    'type': 'INCOMPLETE_CHECKOUT',
                    'item': transaction.get('item_name'),
                    'borrower': transaction.get('borrower_name')
                })
            
            # WO number check
            wo_number = transaction.get('wo_req_no', '').strip()
            if wo_number and wo_number.lower() not in ['nan', 'none', '', 'not provided']:
                compliance_metrics['wo_number_provided'] += 1
            
            # Return timing (not overdue)
            if transaction['status'] != 'Outstanding' or transaction.get('expected_return') != 'Same Day':
                compliance_metrics['return_on_time'] += 1
        
        # Calculate percentages
        for metric in compliance_metrics:
            compliance_metrics[metric] = (compliance_metrics[metric] / total * 100) if total > 0 else 0
        
        return {
            'compliance_metrics': compliance_metrics,
            'violations': violations,
            'overall_compliance': sum(compliance_metrics.values()) / len(compliance_metrics)
        }
    
    def _calculate_days_outstanding(self, transaction):
        """Calculate days since item was borrowed"""
        try:
            from dateutil import parser
            from datetime import datetime
            
            datetime_out = transaction.get('datetime_out', '')
            if not datetime_out:
                return 0
            
            borrowed_date = parser.parse(str(datetime_out), dayfirst=True)
            days_out = (datetime.now() - borrowed_date).days
            return max(0, days_out)
        except:
            return 0
    
    def _calculate_usage_efficiency(self, transactions):
        """Calculate overall usage efficiency metrics"""
        if not transactions:
            return 0
        
        total_transactions = len(transactions)
        successful_returns = len([t for t in transactions if t['status'] in ['Returned', 'Used/Consumed']])
        
        return (successful_returns / total_transactions * 100) if total_transactions > 0 else 0