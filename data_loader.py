#!/usr/bin/env python3
"""
Data loader module for Stores Infrastructure Administration
Loads and processes data from the Excel spreadsheet
"""
import pandas as pd
from datetime import datetime, timedelta
import os
import json
import uuid
import re
import difflib
from collections import Counter

class StoresDataLoader:
    def __init__(self, excel_file="STORES_INFRASTRUCTURE_ADMINISTRATION_enhanced.xlsx"):
        self.excel_file = excel_file
        self.data = {}
        self.item_history_file = "item_history.json"
        self.checkout_records_file = "checkout_records.json"
        self.item_history = self.load_item_history()
        self.checkout_records = self.load_checkout_records()
        self.load_data()
    
    def load_data(self):
        """Load data from all Excel sheets"""
        try:
            if not os.path.exists(self.excel_file):
                print(f"Warning: Excel file {self.excel_file} not found. Using empty data.")
                self._create_empty_data_structure()
                return
            
            excel_file = pd.ExcelFile(self.excel_file)
            
            # Load each sheet
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(self.excel_file, sheet_name=sheet_name)
                self.data[sheet_name] = df
                
            print(f"Successfully loaded data from {len(excel_file.sheet_names)} sheets")
            
        except Exception as e:
            print(f"Error loading Excel file: {e}")
            self._create_empty_data_structure()
    
    def _create_empty_data_structure(self):
        """Create empty data structure when Excel file is not available"""
        sheets = [
            'Dashboard', 'Electric', 'Plumbing', 'Carpentry', 'Painting', 
            'Aircon', 'Ceiling Tiles', 'Decoration', 'Parking & Signage', 
            'Safety', 'Access Control', 'Maintenance Log', 'Suppliers & Contractors'
        ]
        
        for sheet in sheets:
            if sheet == 'Dashboard':
                self.data[sheet] = pd.DataFrame({
                    'KPI': ['Total Items', 'Low Stock Items', 'Categories', 'Active Suppliers'],
                    'Value': [0, 0, 11, 0]
                })
            elif sheet in ['Maintenance Log']:
                self.data[sheet] = pd.DataFrame(columns=[
                    'Date', 'Task Completed', 'Category', 'Technicians Involved',
                    'Time Taken', 'Special Notes / Challenges', 'Before & After Photos Link', 'Impact'
                ])
            elif sheet in ['Suppliers & Contractors']:
                self.data[sheet] = pd.DataFrame(columns=[
                    'Supplier Name', 'Category Supplied', 'Contact Person', 
                    'Phone/Email', 'Contract Expiry Date', 'Preferred / Approved Vendor Indicator'
                ])
            else:
                # Inventory categories
                self.data[sheet] = pd.DataFrame(columns=[
                    'Item Code', 'Description', 'Quantity on Hand', 'Unit of Measure',
                    'Location', 'Min. Stock Level', 'Max. Stock Level', 'Supplier',
                    'Last Purchase Date', 'Warranty Expiry (if applicable)', 'Cost/Unit', 'Total Value (auto-calc)'
                ])
    
    def get_dashboard_data(self):
        """Get dashboard summary data"""
        dashboard_data = {}
        
        # Get KPI data from Dashboard sheet
        if 'Dashboard' in self.data and not self.data['Dashboard'].empty:
            for _, row in self.data['Dashboard'].iterrows():
                dashboard_data[row['KPI']] = row['Value'] if pd.notna(row['Value']) else 0
        
        # Calculate statistics from inventory categories
        total_items = 0
        low_stock_items = 0
        categories_with_items = 0
        
        inventory_categories = ['Electric', 'Plumbing', 'Carpentry', 'Painting', 'Aircon', 
                              'Ceiling Tiles', 'Decoration', 'Parking & Signage', 'Safety', 'Access Control']
        
        for category in inventory_categories:
            if category in self.data and not self.data[category].empty:
                df = self.data[category]
                # Count items in this category
                category_items = len(df)
                total_items += category_items
                
                if category_items > 0:
                    categories_with_items += 1
                
                # Check for low stock items
                for _, row in df.iterrows():
                    if pd.notna(row.get('Quantity on Hand')) and pd.notna(row.get('Min. Stock Level')):
                        try:
                            quantity = float(row['Quantity on Hand'])
                            min_level = float(row['Min. Stock Level'])
                            if quantity <= min_level:
                                low_stock_items += 1
                        except (ValueError, TypeError):
                            continue
        
        # Update dashboard data with calculated values
        dashboard_data.update({
            'Total Items': total_items,
            'Low Stock Items': low_stock_items,
            'Categories with Items': categories_with_items,
            'Total Categories': len(inventory_categories)
        })
        
        return dashboard_data
    
    def get_category_data(self, category):
        """Get data for a specific inventory category"""
        if category in self.data:
            return self.data[category].to_dict('records')
        return []
    
    def get_all_categories(self):
        """Get list of all inventory categories"""
        inventory_categories = ['Electric', 'Plumbing', 'Carpentry', 'Painting', 'Aircon', 
                              'Ceiling Tiles', 'Decoration', 'Parking & Signage', 'Safety', 'Access Control']
        
        categories_info = []
        for category in inventory_categories:
            if category in self.data:
                df = self.data[category]
                total_items = len(df)
                low_stock = 0
                total_value = 0
                
                # Calculate statistics
                for _, row in df.iterrows():
                    # Check for low stock
                    if pd.notna(row.get('Quantity on Hand')) and pd.notna(row.get('Min. Stock Level')):
                        try:
                            quantity = float(row['Quantity on Hand'])
                            min_level = float(row['Min. Stock Level'])
                            if quantity <= min_level:
                                low_stock += 1
                        except (ValueError, TypeError):
                            pass
                    
                    # Calculate total value
                    if pd.notna(row.get('Total Value (auto-calc)')):
                        try:
                            value = float(row['Total Value (auto-calc)'])
                            total_value += value
                        except (ValueError, TypeError):
                            pass
                
                categories_info.append({
                    'name': category,
                    'total_items': total_items,
                    'low_stock': low_stock,
                    'total_value': total_value,
                    'status': 'Low Stock' if low_stock > 0 else 'Normal'
                })
        
        return categories_info
    
    def get_maintenance_log(self):
        """Get maintenance log entries"""
        if 'Maintenance Log' in self.data:
            return self.data['Maintenance Log'].to_dict('records')
        return []
    
    def get_suppliers(self):
        """Get suppliers and contractors data"""
        if 'Suppliers & Contractors' in self.data:
            return self.data['Suppliers & Contractors'].to_dict('records')
        return []
    
    def get_low_stock_items(self):
        """Get all items that are below minimum stock level"""
        low_stock_items = []
        
        inventory_categories = ['Electric', 'Plumbing', 'Carpentry', 'Painting', 'Aircon', 
                              'Ceiling Tiles', 'Decoration', 'Parking & Signage', 'Safety', 'Access Control']
        
        for category in inventory_categories:
            if category in self.data and not self.data[category].empty:
                df = self.data[category]
                for _, row in df.iterrows():
                    if pd.notna(row.get('Quantity on Hand')) and pd.notna(row.get('Min. Stock Level')):
                        try:
                            quantity = float(row['Quantity on Hand'])
                            min_level = float(row['Min. Stock Level'])
                            if quantity <= min_level:
                                item = row.to_dict()
                                item['category'] = category
                                low_stock_items.append(item)
                        except (ValueError, TypeError):
                            continue
        
        return low_stock_items
    
    def search_items(self, query, filters=None):
        """Advanced search for items across all categories with relevance scoring"""
        if not query and not filters:
            return []
        
        results = []
        query = query.lower().strip() if query else ""
        filters = filters or {}
        
        inventory_categories = ['Electric', 'Plumbing', 'Carpentry', 'Painting', 'Aircon', 
                              'Ceiling Tiles', 'Decoration', 'Parking & Signage', 'Safety', 'Access Control']
        
        # Apply category filter
        if filters.get('categories'):
            inventory_categories = [cat for cat in inventory_categories if cat in filters['categories']]
        
        for category in inventory_categories:
            if category in self.data and not self.data[category].empty:
                df = self.data[category]
                for _, row in df.iterrows():
                    item_dict = row.to_dict()
                    item_dict['category'] = category
                    
                    # Apply filters first
                    if not self._passes_filters(item_dict, filters):
                        continue
                    
                    # Calculate relevance score if there's a query
                    relevance_score = 0
                    if query:
                        relevance_score = self._calculate_relevance(item_dict, query)
                        if relevance_score == 0:
                            continue
                    
                    item_dict['relevance_score'] = relevance_score
                    item_dict['search_highlights'] = self._get_highlights(item_dict, query) if query else {}
                    results.append(item_dict)
        
        # Sort by relevance score (descending) if there's a query
        if query:
            results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return results
    
    def _passes_filters(self, item, filters):
        """Check if item passes all applied filters"""
        # Stock status filter
        if filters.get('status'):
            current_stock = self._get_numeric_value(item.get('Quantity on Hand'))
            min_stock = self._get_numeric_value(item.get('Min. Stock Level'))
            
            is_low_stock = current_stock is not None and min_stock is not None and current_stock <= min_stock
            
            if filters['status'] == 'low_stock' and not is_low_stock:
                return False
            elif filters['status'] == 'normal' and is_low_stock:
                return False
            elif filters['status'] == 'out_of_stock' and (current_stock is None or current_stock > 0):
                return False
        
        # Price range filter
        if filters.get('price_min') is not None or filters.get('price_max') is not None:
            unit_cost = self._get_numeric_value(item.get('Cost/Unit'))
            if unit_cost is None:
                return False
            
            if filters.get('price_min') is not None and unit_cost < filters['price_min']:
                return False
            if filters.get('price_max') is not None and unit_cost > filters['price_max']:
                return False
        
        # Quantity range filter
        if filters.get('quantity_min') is not None or filters.get('quantity_max') is not None:
            quantity = self._get_numeric_value(item.get('Quantity on Hand'))
            if quantity is None:
                return False
            
            if filters.get('quantity_min') is not None and quantity < filters['quantity_min']:
                return False
            if filters.get('quantity_max') is not None and quantity > filters['quantity_max']:
                return False
        
        # Location filter
        if filters.get('location'):
            location = str(item.get('Location', '')).lower()
            if filters['location'].lower() not in location:
                return False
        
        # Supplier filter
        if filters.get('supplier'):
            supplier = str(item.get('Supplier', '')).lower()
            if filters['supplier'].lower() not in supplier:
                return False
        
        return True
    
    def _calculate_relevance(self, item, query):
        """Calculate relevance score for search results"""
        score = 0
        query_words = query.split()
        
        # Fields to search with their weights
        search_fields = {
            'Item Code': 100,      # Exact item code match is most important
            'Description': 50,     # Description is very important
            'Location': 20,        # Location somewhat important
            'Supplier': 15,        # Supplier less important
            'Unit of Measure': 10  # Unit of measure least important
        }
        
        for field, weight in search_fields.items():
            field_value = str(item.get(field, '')).lower()
            if not field_value:
                continue
            
            # Exact match bonus
            if query == field_value:
                score += weight * 10
            # Partial exact match
            elif query in field_value:
                score += weight * 5
            
            # Word-by-word matching
            for word in query_words:
                if word in field_value:
                    score += weight
                
                # Fuzzy matching for typos
                best_match = difflib.get_close_matches(word, field_value.split(), n=1, cutoff=0.7)
                if best_match:
                    score += weight * 0.5
        
        # Boost score for items with more complete data
        completeness_bonus = sum(1 for field in search_fields.keys() if item.get(field))
        score += completeness_bonus * 2
        
        return score
    
    def _get_highlights(self, item, query):
        """Get highlighted text snippets for search results"""
        highlights = {}
        query_words = query.split()
        
        search_fields = ['Item Code', 'Description', 'Location', 'Supplier']
        
        for field in search_fields:
            field_value = str(item.get(field, ''))
            if not field_value:
                continue
            
            # Find matches and create highlights
            highlighted_text = field_value
            for word in query_words:
                # Case-insensitive replacement with highlighting
                pattern = re.compile(re.escape(word), re.IGNORECASE)
                highlighted_text = pattern.sub(f'<mark>{word}</mark>', highlighted_text)
            
            if '<mark>' in highlighted_text:
                highlights[field] = highlighted_text
        
        return highlights
    
    def _get_numeric_value(self, value):
        """Safely convert value to numeric"""
        if value is None or value == 'N/A':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def get_search_suggestions(self, partial_query, limit=10):
        """Get search suggestions based on partial query"""
        if not partial_query or len(partial_query) < 2:
            return []
        
        suggestions = set()
        partial_query = partial_query.lower()
        
        inventory_categories = ['Electric', 'Plumbing', 'Carpentry', 'Painting', 'Aircon', 
                              'Ceiling Tiles', 'Decoration', 'Parking & Signage', 'Safety', 'Access Control']
        
        for category in inventory_categories:
            if category in self.data and not self.data[category].empty:
                df = self.data[category]
                for _, row in df.iterrows():
                    # Get suggestions from item codes and descriptions
                    item_code = str(row.get('Item Code', '')).lower()
                    description = str(row.get('Description', '')).lower()
                    
                    # Add item code if it starts with the query
                    if item_code.startswith(partial_query):
                        suggestions.add(row.get('Item Code', ''))
                    
                    # Add description words that start with the query
                    desc_words = description.split()
                    for word in desc_words:
                        if len(word) > 2 and word.startswith(partial_query):
                            suggestions.add(word.title())
                    
                    # Add full description if it contains the query
                    if partial_query in description and len(row.get('Description', '')) < 50:
                        suggestions.add(row.get('Description', ''))
        
        # Sort suggestions by length and relevance
        sorted_suggestions = sorted(list(suggestions))[:limit]
        return sorted_suggestions
    
    def get_filter_options(self):
        """Get available filter options from the data"""
        options = {
            'categories': ['Electric', 'Plumbing', 'Carpentry', 'Painting', 'Aircon', 
                          'Ceiling Tiles', 'Decoration', 'Parking & Signage', 'Safety', 'Access Control'],
            'locations': set(),
            'suppliers': set(),
            'units': set(),
            'price_range': {'min': None, 'max': None},
            'quantity_range': {'min': None, 'max': None}
        }
        
        prices = []
        quantities = []
        
        for category in options['categories']:
            if category in self.data and not self.data[category].empty:
                df = self.data[category]
                for _, row in df.iterrows():
                    # Collect unique values
                    location = str(row.get('Location', '')).strip()
                    if location and location != 'N/A':
                        options['locations'].add(location)
                    
                    supplier = str(row.get('Supplier', '')).strip()
                    if supplier and supplier != 'N/A':
                        options['suppliers'].add(supplier)
                    
                    unit = str(row.get('Unit of Measure', '')).strip()
                    if unit and unit != 'N/A':
                        options['units'].add(unit)
                    
                    # Collect numeric values for ranges
                    price = self._get_numeric_value(row.get('Cost/Unit'))
                    if price is not None:
                        prices.append(price)
                    
                    quantity = self._get_numeric_value(row.get('Quantity on Hand'))
                    if quantity is not None:
                        quantities.append(quantity)
        
        # Convert sets to sorted lists
        options['locations'] = sorted(list(options['locations']))
        options['suppliers'] = sorted(list(options['suppliers']))
        options['units'] = sorted(list(options['units']))
        
        # Set ranges
        if prices:
            options['price_range'] = {'min': min(prices), 'max': max(prices)}
        if quantities:
            options['quantity_range'] = {'min': min(quantities), 'max': max(quantities)}
        
        return options
    
    # Item History and Tracking Methods
    def load_item_history(self):
        """Load item history from JSON file"""
        try:
            if os.path.exists(self.item_history_file):
                with open(self.item_history_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading item history: {e}")
            return {}
    
    def save_item_history(self):
        """Save item history to JSON file"""
        try:
            with open(self.item_history_file, 'w') as f:
                json.dump(self.item_history, f, indent=2)
        except Exception as e:
            print(f"Error saving item history: {e}")
    
    def load_checkout_records(self):
        """Load checkout records from JSON file"""
        try:
            if os.path.exists(self.checkout_records_file):
                with open(self.checkout_records_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading checkout records: {e}")
            return {}
    
    def save_checkout_records(self):
        """Save checkout records to JSON file"""
        try:
            with open(self.checkout_records_file, 'w') as f:
                json.dump(self.checkout_records, f, indent=2)
        except Exception as e:
            print(f"Error saving checkout records: {e}")
    
    def add_item_history_entry(self, item_code, category, action_type, details, user="System"):
        """Add entry to item history"""
        if item_code not in self.item_history:
            self.item_history[item_code] = []
        
        entry = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'category': category,
            'action': action_type,
            'details': details,
            'user': user
        }
        
        self.item_history[item_code].append(entry)
        self.save_item_history()
        return entry
    
    def get_item_history(self, item_code):
        """Get history for specific item"""
        history = self.item_history.get(item_code, [])
        # Sort by timestamp (most recent first)
        return sorted(history, key=lambda x: x['timestamp'], reverse=True)
    
    def checkout_item(self, item_code, category, quantity, user_name, notes=""):
        """Check out an item"""
        checkout_id = str(uuid.uuid4())
        
        checkout_record = {
            'id': checkout_id,
            'item_code': item_code,
            'category': category,
            'quantity': quantity,
            'checkout_time': datetime.now().isoformat(),
            'checked_out_by': user_name,
            'notes': notes,
            'status': 'checked_out',
            'checkin_time': None,
            'returned_quantity': None
        }
        
        self.checkout_records[checkout_id] = checkout_record
        self.save_checkout_records()
        
        # Add to item history
        self.add_item_history_entry(
            item_code, category, 'checkout', 
            f"Checked out {quantity} units by {user_name}. Notes: {notes}",
            user_name
        )
        
        return checkout_record
    
    def checkin_item(self, checkout_id, returned_quantity, notes=""):
        """Check in a previously checked out item"""
        if checkout_id in self.checkout_records:
            record = self.checkout_records[checkout_id]
            record['checkin_time'] = datetime.now().isoformat()
            record['returned_quantity'] = returned_quantity
            record['status'] = 'returned'
            record['return_notes'] = notes
            
            self.save_checkout_records()
            
            # Add to item history
            self.add_item_history_entry(
                record['item_code'], record['category'], 'checkin',
                f"Returned {returned_quantity} units. Notes: {notes}",
                record['checked_out_by']
            )
            
            return record
        return None
    
    def get_checked_out_items(self, user_name=None):
        """Get all currently checked out items"""
        checked_out = []
        for record in self.checkout_records.values():
            if record['status'] == 'checked_out':
                if user_name is None or record['checked_out_by'] == user_name:
                    checked_out.append(record)
        
        return sorted(checked_out, key=lambda x: x['checkout_time'], reverse=True)
    
    def get_overdue_items(self, days_overdue=7):
        """Get items that have been checked out for too long"""
        overdue = []
        cutoff_date = datetime.now() - timedelta(days=days_overdue)
        
        for record in self.checkout_records.values():
            if record['status'] == 'checked_out':
                checkout_time = datetime.fromisoformat(record['checkout_time'])
                if checkout_time < cutoff_date:
                    overdue.append(record)
        
        return sorted(overdue, key=lambda x: x['checkout_time'])
    
    def generate_item_qr_data(self, item_code, category):
        """Generate QR code data for an item"""
        base_url = "http://localhost:5000"  # In production, use actual domain
        return {
            'url': f"{base_url}/item/{category}/{item_code}",
            'item_code': item_code,
            'category': category,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_item_detailed_info(self, item_code, category):
        """Get comprehensive item information including history"""
        # Get basic item data
        items = self.get_category_data(category)
        item_data = None
        
        for item in items:
            if item.get('Item Code') == item_code:
                item_data = item
                break
        
        if not item_data:
            return None
        
        # Get additional tracking data
        history = self.get_item_history(item_code)
        checked_out = self.get_checked_out_items()
        current_checkout = None
        
        for checkout in checked_out:
            if checkout['item_code'] == item_code:
                current_checkout = checkout
                break
        
        return {
            'basic_info': item_data,
            'history': history,
            'current_checkout': current_checkout,
            'qr_data': self.generate_item_qr_data(item_code, category)
        }

# Global instance
data_loader = StoresDataLoader()

def get_data_loader():
    """Get the global data loader instance"""
    return data_loader

def reload_data():
    """Reload data from Excel file"""
    global data_loader
    data_loader = StoresDataLoader()
    return data_loader