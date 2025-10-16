#!/usr/bin/env python3
"""
Script to populate the Excel file with sample inventory data
This demonstrates how the system works with real data
"""
import pandas as pd
from datetime import datetime, timedelta
import random

def create_sample_data():
    """Create comprehensive sample inventory data for all categories"""
    
    # Enhanced sample data with diverse items for better search and filtering
    sample_items = {
        'Electric': [
            {'Item Code': 'ELE001', 'Description': 'LED Light Bulbs 60W Warm White', 'Quantity on Hand': 45, 'Unit of Measure': 'pcs', 'Location': 'Main Warehouse', 'Min. Stock Level': 20, 'Max. Stock Level': 100, 'Supplier': 'ElectroMax Ltd', 'Cost/Unit': 25.50, 'Total Value (auto-calc)': 1147.50, 'Last Purchase Date': '2025-07-15', 'Warranty Expiry (if applicable)': '2026-07-15'},
            {'Item Code': 'ELE002', 'Description': 'Extension Cords Heavy Duty 5m', 'Quantity on Hand': 8, 'Unit of Measure': 'pcs', 'Location': 'Workshop', 'Min. Stock Level': 25, 'Max. Stock Level': 75, 'Supplier': 'PowerPlus Co', 'Cost/Unit': 185.00, 'Total Value (auto-calc)': 1480.00, 'Last Purchase Date': '2025-06-20', 'Warranty Expiry (if applicable)': '2027-06-20'},
            {'Item Code': 'ELE003', 'Description': 'Circuit Breakers MCB 20A', 'Quantity on Hand': 12, 'Unit of Measure': 'pcs', 'Location': 'Electrical Room', 'Min. Stock Level': 15, 'Max. Stock Level': 50, 'Supplier': 'SafeElectric Inc', 'Cost/Unit': 125.00, 'Total Value (auto-calc)': 1500.00, 'Last Purchase Date': '2025-08-01', 'Warranty Expiry (if applicable)': '2030-08-01'},
            {'Item Code': 'ELE004', 'Description': 'Electrical Wire Single Core 2.5mm', 'Quantity on Hand': 150, 'Unit of Measure': 'm', 'Location': 'Cable Store', 'Min. Stock Level': 50, 'Max. Stock Level': 300, 'Supplier': 'WireTech SA', 'Cost/Unit': 15.75, 'Total Value (auto-calc)': 2362.50, 'Last Purchase Date': '2025-08-10', 'Warranty Expiry (if applicable)': 'N/A'},
            {'Item Code': 'ELE005', 'Description': 'Power Outlets Double 16A White', 'Quantity on Hand': 28, 'Unit of Measure': 'pcs', 'Location': 'Main Warehouse', 'Min. Stock Level': 15, 'Max. Stock Level': 60, 'Supplier': 'ElectroMax Ltd', 'Cost/Unit': 45.00, 'Total Value (auto-calc)': 1260.00, 'Last Purchase Date': '2025-07-25', 'Warranty Expiry (if applicable)': '2028-07-25'},
            {'Item Code': 'ELE006', 'Description': 'Fluorescent Tubes T8 36W', 'Quantity on Hand': 5, 'Unit of Measure': 'pcs', 'Location': 'Storage Room B', 'Min. Stock Level': 20, 'Max. Stock Level': 80, 'Supplier': 'LightPro SA', 'Cost/Unit': 35.50, 'Total Value (auto-calc)': 177.50, 'Last Purchase Date': '2025-05-15', 'Warranty Expiry (if applicable)': '2026-05-15'},
            {'Item Code': 'ELE007', 'Description': 'Emergency Exit Light Battery Backup', 'Quantity on Hand': 3, 'Unit of Measure': 'pcs', 'Location': 'Safety Equipment Store', 'Min. Stock Level': 8, 'Max. Stock Level': 25, 'Supplier': 'SafeElectric Inc', 'Cost/Unit': 485.00, 'Total Value (auto-calc)': 1455.00, 'Last Purchase Date': '2025-04-20', 'Warranty Expiry (if applicable)': '2028-04-20'},
        ],
        'Plumbing': [
            {'Item Code': 'PLM001', 'Description': 'PVC Pipes uPVC 110mm Class 12', 'Quantity on Hand': 85, 'Unit of Measure': 'm', 'Location': 'Pipe Yard', 'Min. Stock Level': 50, 'Max. Stock Level': 200, 'Supplier': 'AquaFlow Systems', 'Cost/Unit': 52.00, 'Total Value (auto-calc)': 4420.00, 'Last Purchase Date': '2025-08-05', 'Warranty Expiry (if applicable)': 'N/A'},
            {'Item Code': 'PLM002', 'Description': 'Toilet Seats Soft Close White', 'Quantity on Hand': 12, 'Unit of Measure': 'pcs', 'Location': 'Bathroom Fixtures', 'Min. Stock Level': 8, 'Max. Stock Level': 30, 'Supplier': 'BathCare Ltd', 'Cost/Unit': 225.50, 'Total Value (auto-calc)': 2706.00, 'Last Purchase Date': '2025-07-20', 'Warranty Expiry (if applicable)': '2027-07-20'},
            {'Item Code': 'PLM003', 'Description': 'Basin Mixer Tap Chrome Lever Handle', 'Quantity on Hand': 4, 'Unit of Measure': 'pcs', 'Location': 'Bathroom Fixtures', 'Min. Stock Level': 10, 'Max. Stock Level': 25, 'Supplier': 'TapMaster Pro', 'Cost/Unit': 420.00, 'Total Value (auto-calc)': 1680.00, 'Last Purchase Date': '2025-06-15', 'Warranty Expiry (if applicable)': '2030-06-15'},
            {'Item Code': 'PLM004', 'Description': 'PVC Pipe Fittings 110mm Bend 90°', 'Quantity on Hand': 45, 'Unit of Measure': 'pcs', 'Location': 'Pipe Yard', 'Min. Stock Level': 25, 'Max. Stock Level': 100, 'Supplier': 'AquaFlow Systems', 'Cost/Unit': 38.50, 'Total Value (auto-calc)': 1732.50, 'Last Purchase Date': '2025-08-05', 'Warranty Expiry (if applicable)': 'N/A'},
            {'Item Code': 'PLM005', 'Description': 'Water Meter 15mm Residential', 'Quantity on Hand': 6, 'Unit of Measure': 'pcs', 'Location': 'Meters Store', 'Min. Stock Level': 12, 'Max. Stock Level': 30, 'Supplier': 'FlowMeter SA', 'Cost/Unit': 385.00, 'Total Value (auto-calc)': 2310.00, 'Last Purchase Date': '2025-07-10', 'Warranty Expiry (if applicable)': '2035-07-10'},
            {'Item Code': 'PLM006', 'Description': 'Geyser Element 3kW Universal', 'Quantity on Hand': 8, 'Unit of Measure': 'pcs', 'Location': 'Electrical Parts', 'Min. Stock Level': 15, 'Max. Stock Level': 40, 'Supplier': 'HeatTech Pro', 'Cost/Unit': 165.00, 'Total Value (auto-calc)': 1320.00, 'Last Purchase Date': '2025-08-15', 'Warranty Expiry (if applicable)': '2027-08-15'},
        ],
        'Carpentry': [
            {'Item Code': 'CAR001', 'Description': 'Wood Screws Self-Tapping 50mm Zinc', 'Quantity on Hand': 280, 'Unit of Measure': 'pcs', 'Location': 'Hardware Store', 'Min. Stock Level': 200, 'Max. Stock Level': 500, 'Supplier': 'FastenMax SA', 'Cost/Unit': 3.25, 'Total Value (auto-calc)': 910.00, 'Last Purchase Date': '2025-08-12', 'Warranty Expiry (if applicable)': 'N/A'},
            {'Item Code': 'CAR002', 'Description': 'Pine Timber PAR 38x114mm 3.6m', 'Quantity on Hand': 12, 'Unit of Measure': 'lengths', 'Location': 'Timber Yard', 'Min. Stock Level': 20, 'Max. Stock Level': 60, 'Supplier': 'TimberMax Ltd', 'Cost/Unit': 145.00, 'Total Value (auto-calc)': 1740.00, 'Last Purchase Date': '2025-07-28', 'Warranty Expiry (if applicable)': 'N/A'},
            {'Item Code': 'CAR003', 'Description': 'PVA Wood Glue Weatherproof 500ml', 'Quantity on Hand': 15, 'Unit of Measure': 'bottles', 'Location': 'Adhesives Store', 'Min. Stock Level': 12, 'Max. Stock Level': 35, 'Supplier': 'BondTech Pro', 'Cost/Unit': 85.00, 'Total Value (auto-calc)': 1275.00, 'Last Purchase Date': '2025-08-20', 'Warranty Expiry (if applicable)': '2027-08-20'},
            {'Item Code': 'CAR004', 'Description': 'Door Hinges Heavy Duty 100mm Brass', 'Quantity on Hand': 18, 'Unit of Measure': 'pairs', 'Location': 'Hardware Store', 'Min. Stock Level': 25, 'Max. Stock Level': 60, 'Supplier': 'HardwarePro SA', 'Cost/Unit': 125.00, 'Total Value (auto-calc)': 2250.00, 'Last Purchase Date': '2025-06-30', 'Warranty Expiry (if applicable)': '2030-06-30'},
            {'Item Code': 'CAR005', 'Description': 'Wood Stain Mahogany 1L', 'Quantity on Hand': 6, 'Unit of Measure': 'cans', 'Location': 'Paint Store', 'Min. Stock Level': 12, 'Max. Stock Level': 30, 'Supplier': 'WoodFinish Ltd', 'Cost/Unit': 165.00, 'Total Value (auto-calc)': 990.00, 'Last Purchase Date': '2025-05-22', 'Warranty Expiry (if applicable)': '2028-05-22'},
        ],
        'Painting': [
            {'Item Code': 'PNT001', 'Description': 'Acrylic Interior Paint Brilliant White 5L', 'Quantity on Hand': 25, 'Unit of Measure': 'cans', 'Location': 'Paint Store', 'Min. Stock Level': 15, 'Max. Stock Level': 50, 'Supplier': 'ColorMax Paints', 'Cost/Unit': 335.00, 'Total Value (auto-calc)': 8375.00, 'Last Purchase Date': '2025-08-18', 'Warranty Expiry (if applicable)': '2027-08-18'},
            {'Item Code': 'PNT002', 'Description': 'Paint Brushes Professional 75mm Synthetic', 'Quantity on Hand': 18, 'Unit of Measure': 'pcs', 'Location': 'Tool Store', 'Min. Stock Level': 15, 'Max. Stock Level': 45, 'Supplier': 'BrushPro SA', 'Cost/Unit': 65.50, 'Total Value (auto-calc)': 1179.00, 'Last Purchase Date': '2025-07-12', 'Warranty Expiry (if applicable)': 'N/A'},
            {'Item Code': 'PNT003', 'Description': 'Paint Roller Kit 230mm with Tray', 'Quantity on Hand': 14, 'Unit of Measure': 'sets', 'Location': 'Tool Store', 'Min. Stock Level': 10, 'Max. Stock Level': 30, 'Supplier': 'RollTech Ltd', 'Cost/Unit': 145.00, 'Total Value (auto-calc)': 2030.00, 'Last Purchase Date': '2025-07-25', 'Warranty Expiry (if applicable)': 'N/A'},
            {'Item Code': 'PNT004', 'Description': 'Exterior Paint Weatherguard Grey 5L', 'Quantity on Hand': 4, 'Unit of Measure': 'cans', 'Location': 'Paint Store', 'Min. Stock Level': 12, 'Max. Stock Level': 35, 'Supplier': 'WeatherShield SA', 'Cost/Unit': 485.00, 'Total Value (auto-calc)': 1940.00, 'Last Purchase Date': '2025-06-08', 'Warranty Expiry (if applicable)': '2030-06-08'},
            {'Item Code': 'PNT005', 'Description': 'Paint Primer Sealer Universal 5L', 'Quantity on Hand': 8, 'Unit of Measure': 'cans', 'Location': 'Paint Store', 'Min. Stock Level': 10, 'Max. Stock Level': 25, 'Supplier': 'ColorMax Paints', 'Cost/Unit': 265.00, 'Total Value (auto-calc)': 2120.00, 'Last Purchase Date': '2025-08-02', 'Warranty Expiry (if applicable)': '2028-08-02'},
        ],
        'Aircon': [
            {'Item Code': 'AIR001', 'Description': 'HVAC Air Filter Pleated 595x595x48mm', 'Quantity on Hand': 32, 'Unit of Measure': 'pcs', 'Location': 'HVAC Store', 'Min. Stock Level': 25, 'Max. Stock Level': 80, 'Supplier': 'CoolAir Systems', 'Cost/Unit': 125.00, 'Total Value (auto-calc)': 4000.00, 'Last Purchase Date': '2025-08-10', 'Warranty Expiry (if applicable)': 'N/A'},
            {'Item Code': 'AIR002', 'Description': 'Refrigerant Gas R410A Environmental 1kg', 'Quantity on Hand': 6, 'Unit of Measure': 'bottles', 'Location': 'Refrigerant Store', 'Min. Stock Level': 8, 'Max. Stock Level': 25, 'Supplier': 'ChillMax Pro', 'Cost/Unit': 520.00, 'Total Value (auto-calc)': 3120.00, 'Last Purchase Date': '2025-07-05', 'Warranty Expiry (if applicable)': '2030-07-05'},
            {'Item Code': 'AIR003', 'Description': 'Digital Thermostat Programmable 7-Day', 'Quantity on Hand': 9, 'Unit of Measure': 'pcs', 'Location': 'Controls Store', 'Min. Stock Level': 12, 'Max. Stock Level': 30, 'Supplier': 'TempControl SA', 'Cost/Unit': 385.50, 'Total Value (auto-calc)': 3469.50, 'Last Purchase Date': '2025-06-25', 'Warranty Expiry (if applicable)': '2030-06-25'},
            {'Item Code': 'AIR004', 'Description': 'Condensate Drain Pump 230V', 'Quantity on Hand': 3, 'Unit of Measure': 'pcs', 'Location': 'HVAC Store', 'Min. Stock Level': 8, 'Max. Stock Level': 20, 'Supplier': 'PumpTech SA', 'Cost/Unit': 645.00, 'Total Value (auto-calc)': 1935.00, 'Last Purchase Date': '2025-05-18', 'Warranty Expiry (if applicable)': '2028-05-18'},
        ],
        'Safety': [
            {'Item Code': 'SAF001', 'Description': 'Safety Helmets Hard Hat ANSI Compliant', 'Quantity on Hand': 42, 'Unit of Measure': 'pcs', 'Location': 'PPE Store', 'Min. Stock Level': 30, 'Max. Stock Level': 80, 'Supplier': 'SafeGuard Ltd', 'Cost/Unit': 185.00, 'Total Value (auto-calc)': 7770.00, 'Last Purchase Date': '2025-08-08', 'Warranty Expiry (if applicable)': '2030-08-08'},
            {'Item Code': 'SAF002', 'Description': 'Hi-Vis Safety Vests Class 2 Reflective', 'Quantity on Hand': 28, 'Unit of Measure': 'pcs', 'Location': 'PPE Store', 'Min. Stock Level': 25, 'Max. Stock Level': 75, 'Supplier': 'VisProtect SA', 'Cost/Unit': 125.00, 'Total Value (auto-calc)': 3500.00, 'Last Purchase Date': '2025-07-30', 'Warranty Expiry (if applicable)': 'N/A'},
            {'Item Code': 'SAF003', 'Description': 'Fire Extinguisher DCP 2kg SABS', 'Quantity on Hand': 12, 'Unit of Measure': 'pcs', 'Location': 'Fire Safety Store', 'Min. Stock Level': 15, 'Max. Stock Level': 40, 'Supplier': 'FireSafe Pro', 'Cost/Unit': 385.00, 'Total Value (auto-calc)': 4620.00, 'Last Purchase Date': '2025-06-12', 'Warranty Expiry (if applicable)': '2030-06-12'},
            {'Item Code': 'SAF004', 'Description': 'Safety Goggles Clear Anti-Fog', 'Quantity on Hand': 18, 'Unit of Measure': 'pcs', 'Location': 'PPE Store', 'Min. Stock Level': 20, 'Max. Stock Level': 50, 'Supplier': 'EyeProtect SA', 'Cost/Unit': 65.00, 'Total Value (auto-calc)': 1170.00, 'Last Purchase Date': '2025-08-15', 'Warranty Expiry (if applicable)': '2027-08-15'},
            {'Item Code': 'SAF005', 'Description': 'First Aid Kit Workplace 20-Person', 'Quantity on Hand': 5, 'Unit of Measure': 'kits', 'Location': 'Medical Store', 'Min. Stock Level': 8, 'Max. Stock Level': 20, 'Supplier': 'MedCare Supplies', 'Cost/Unit': 245.00, 'Total Value (auto-calc)': 1225.00, 'Last Purchase Date': '2025-07-18', 'Warranty Expiry (if applicable)': '2027-07-18'},
        ],
        'Ceiling Tiles': [
            {'Item Code': 'CTL001', 'Description': 'Acoustic Ceiling Tiles 600x600mm', 'Quantity on Hand': 48, 'Unit of Measure': 'pcs', 'Location': 'Ceiling Materials', 'Min. Stock Level': 60, 'Max. Stock Level': 150, 'Supplier': 'CeilingPro SA', 'Cost/Unit': 45.00, 'Total Value (auto-calc)': 2160.00, 'Last Purchase Date': '2025-07-08', 'Warranty Expiry (if applicable)': 'N/A'},
            {'Item Code': 'CTL002', 'Description': 'Suspended Ceiling Grid T-Bar 3.6m', 'Quantity on Hand': 25, 'Unit of Measure': 'lengths', 'Location': 'Ceiling Materials', 'Min. Stock Level': 30, 'Max. Stock Level': 80, 'Supplier': 'GridMax Ltd', 'Cost/Unit': 125.00, 'Total Value (auto-calc)': 3125.00, 'Last Purchase Date': '2025-06-20', 'Warranty Expiry (if applicable)': '2035-06-20'},
        ],
        'Decoration': [
            {'Item Code': 'DEC001', 'Description': 'Vinyl Floor Tiles Self-Adhesive', 'Quantity on Hand': 85, 'Unit of Measure': 'pcs', 'Location': 'Flooring Store', 'Min. Stock Level': 100, 'Max. Stock Level': 300, 'Supplier': 'FloorStyle SA', 'Cost/Unit': 28.50, 'Total Value (auto-calc)': 2422.50, 'Last Purchase Date': '2025-08-12', 'Warranty Expiry (if applicable)': '2030-08-12'},
            {'Item Code': 'DEC002', 'Description': 'Window Blinds Venetian 1200mm', 'Quantity on Hand': 8, 'Unit of Measure': 'pcs', 'Location': 'Window Treatments', 'Min. Stock Level': 12, 'Max. Stock Level': 30, 'Supplier': 'BlindCraft Ltd', 'Cost/Unit': 285.00, 'Total Value (auto-calc)': 2280.00, 'Last Purchase Date': '2025-05-25', 'Warranty Expiry (if applicable)': '2030-05-25'},
        ],
        'Parking & Signage': [
            {'Item Code': 'PKG001', 'Description': 'Parking Bay Markers Reflective Yellow', 'Quantity on Hand': 12, 'Unit of Measure': 'pcs', 'Location': 'Signage Store', 'Min. Stock Level': 20, 'Max. Stock Level': 50, 'Supplier': 'SignMax Pro', 'Cost/Unit': 145.00, 'Total Value (auto-calc)': 1740.00, 'Last Purchase Date': '2025-07-15', 'Warranty Expiry (if applicable)': '2035-07-15'},
            {'Item Code': 'PKG002', 'Description': 'No Smoking Signs Aluminium 300x200mm', 'Quantity on Hand': 6, 'Unit of Measure': 'pcs', 'Location': 'Signage Store', 'Min. Stock Level': 15, 'Max. Stock Level': 40, 'Supplier': 'SafeSign SA', 'Cost/Unit': 65.00, 'Total Value (auto-calc)': 390.00, 'Last Purchase Date': '2025-06-28', 'Warranty Expiry (if applicable)': '2040-06-28'},
        ],
        'Access Control': [
            {'Item Code': 'ACC001', 'Description': 'Proximity Card Reader RFID', 'Quantity on Hand': 4, 'Unit of Measure': 'pcs', 'Location': 'Security Store', 'Min. Stock Level': 8, 'Max. Stock Level': 20, 'Supplier': 'SecureTech SA', 'Cost/Unit': 1250.00, 'Total Value (auto-calc)': 5000.00, 'Last Purchase Date': '2025-05-10', 'Warranty Expiry (if applicable)': '2030-05-10'},
            {'Item Code': 'ACC002', 'Description': 'Access Control Cards Proximity', 'Quantity on Hand': 85, 'Unit of Measure': 'pcs', 'Location': 'Security Store', 'Min. Stock Level': 100, 'Max. Stock Level': 500, 'Supplier': 'CardTech Ltd', 'Cost/Unit': 25.00, 'Total Value (auto-calc)': 2125.00, 'Last Purchase Date': '2025-08-20', 'Warranty Expiry (if applicable)': '2035-08-20'},
        ]
    }
    
    # Enhanced Maintenance Log with more comprehensive data
    maintenance_data = [
        {
            'Date': '2025-08-15',
            'Task Completed': 'Emergency lighting system upgrade - replaced LED bulbs and exit signs',
            'Category': 'Electric',
            'Technicians Involved': 'John Smith (Electrical), Mike Wilson (Assistant)',
            'Time Taken': '4.5h',
            'Special Notes / Challenges': 'Had to coordinate with building occupants for power shutdowns. Some ceiling fixtures required scaffolding. Discovered two faulty ballasts that needed replacement.',
            'Before & After Photos Link': 'drive://facilities/maintenance/2025-08-15-emergency-lighting',
            'Impact': 'Enhanced safety compliance, improved energy efficiency by 35%, better illumination levels'
        },
        {
            'Date': '2025-08-20',
            'Task Completed': 'Critical plumbing repair - main water line leak in basement',
            'Category': 'Plumbing',
            'Technicians Involved': 'Sarah Connor (Senior Plumber), Tom Brown (Pipe Specialist)',
            'Time Taken': '6h',
            'Special Notes / Challenges': 'Emergency repair required full building water shutdown for 3 hours. Had to excavate concrete floor to access main line. Coordinated with water authority for pressure testing.',
            'Before & After Photos Link': 'drive://facilities/maintenance/2025-08-20-water-line-repair',
            'Impact': 'Eliminated risk of flooding, restored full water pressure, prevented potential structural damage'
        },
        {
            'Date': '2025-08-25',
            'Task Completed': 'Office renovation - complete repainting of reception and meeting areas',
            'Category': 'Painting',
            'Technicians Involved': 'Lisa Davis (Lead Painter), Carlos Martinez (Assistant)',
            'Time Taken': '8h',
            'Special Notes / Challenges': 'Required extensive prep work due to wall damage. Used low-VOC paints for indoor air quality. Had to work around office furniture and equipment.',
            'Before & After Photos Link': 'drive://facilities/maintenance/2025-08-25-office-renovation',
            'Impact': 'Professional appearance restored, improved workplace morale, better first impression for visitors'
        },
        {
            'Date': '2025-09-01',
            'Task Completed': 'HVAC preventive maintenance - filter replacement and system cleaning',
            'Category': 'Aircon',
            'Technicians Involved': 'Mark Johnson (HVAC Tech), Pete Williams (Assistant)',
            'Time Taken': '7h',
            'Special Notes / Challenges': 'Several units had severely clogged filters affecting airflow. Cleaned evaporator coils and checked refrigerant levels. Replaced 3 thermostats with digital programmable units.',
            'Before & After Photos Link': 'drive://facilities/maintenance/2025-09-01-hvac-service',
            'Impact': 'Improved air quality by 40%, reduced energy consumption, extended equipment lifespan'
        },
        {
            'Date': '2025-09-03',
            'Task Completed': 'Safety equipment audit and fire extinguisher servicing',
            'Category': 'Safety',
            'Technicians Involved': 'Janet Wilson (Safety Officer), Robert Lee (Fire Safety Tech)',
            'Time Taken': '3h',
            'Special Notes / Challenges': 'Found 2 expired extinguishers that needed immediate replacement. Updated safety signage in multiple languages. Conducted emergency exit lighting tests.',
            'Before & After Photos Link': 'drive://facilities/maintenance/2025-09-03-safety-audit',
            'Impact': 'Full safety compliance achieved, emergency preparedness improved, staff confidence increased'
        },
        {
            'Date': '2025-09-05',
            'Task Completed': 'Carpentry repairs - damaged door frames and window sills replacement',
            'Category': 'Carpentry',
            'Technicians Involved': 'David Thompson (Master Carpenter)',
            'Time Taken': '5.5h',
            'Special Notes / Challenges': 'Wood rot damage more extensive than initially assessed. Had to source matching timber stain. Some areas required structural reinforcement.',
            'Before & After Photos Link': 'drive://facilities/maintenance/2025-09-05-carpentry-repairs',
            'Impact': 'Structural integrity restored, improved weather sealing, enhanced building aesthetics'
        }
    ]
    
    # Enhanced Suppliers data with comprehensive vendor information
    suppliers_data = [
        {
            'Supplier Name': 'ElectroMax Ltd',
            'Category Supplied': 'Electric, Emergency Lighting',
            'Contact Person': 'David Johnson (Sales Manager)',
            'Phone/Email': 'david@electromax.co.za / 011-555-0001 / 082-123-4567',
            'Contract Expiry Date': '2025-12-31',
            'Preferred / Approved Vendor Indicator': 'Preferred'
        },
        {
            'Supplier Name': 'PowerPlus Co',
            'Category Supplied': 'Electric, Heavy Duty Equipment',
            'Contact Person': 'Michelle Thompson (Account Manager)',
            'Phone/Email': 'michelle@powerplus.co.za / 011-555-0012 / 083-987-6543',
            'Contract Expiry Date': '2026-08-15',
            'Preferred / Approved Vendor Indicator': 'Approved'
        },
        {
            'Supplier Name': 'AquaFlow Systems',
            'Category Supplied': 'Plumbing, Water Management',
            'Contact Person': 'Maria Rodriguez (Technical Sales)',
            'Phone/Email': 'maria@aquaflow.co.za / 021-555-0002 / 072-456-7890',
            'Contract Expiry Date': '2026-06-30',
            'Preferred / Approved Vendor Indicator': 'Preferred'
        },
        {
            'Supplier Name': 'FlowMeter SA',
            'Category Supplied': 'Plumbing, Metering Equipment',
            'Contact Person': 'James Wilson (Regional Manager)',
            'Phone/Email': 'james@flowmeter.co.za / 031-555-0015 / 084-321-0987',
            'Contract Expiry Date': '2027-02-28',
            'Preferred / Approved Vendor Indicator': 'Approved'
        },
        {
            'Supplier Name': 'TimberMax Ltd',
            'Category Supplied': 'Carpentry, Structural Timber',
            'Contact Person': 'Peter van der Merwe (Operations Manager)',
            'Phone/Email': 'peter@timbermax.co.za / 031-555-0003 / 073-654-3210',
            'Contract Expiry Date': '2025-10-15',
            'Preferred / Approved Vendor Indicator': 'Preferred'
        },
        {
            'Supplier Name': 'FastenMax SA',
            'Category Supplied': 'Carpentry, Hardware, Fasteners',
            'Contact Person': 'Ryan Mitchell (Sales Representative)',
            'Phone/Email': 'ryan@fastenmax.co.za / 011-555-0018 / 076-890-1234',
            'Contract Expiry Date': '2026-11-20',
            'Preferred / Approved Vendor Indicator': 'Approved'
        },
        {
            'Supplier Name': 'ColorMax Paints',
            'Category Supplied': 'Painting, Interior/Exterior Coatings',
            'Contact Person': 'Jennifer Smith (Key Account Manager)',
            'Phone/Email': 'jen@colormax.co.za / 011-555-0004 / 082-567-8901',
            'Contract Expiry Date': '2026-03-20',
            'Preferred / Approved Vendor Indicator': 'Preferred'
        },
        {
            'Supplier Name': 'WeatherShield SA',
            'Category Supplied': 'Painting, Protective Coatings',
            'Contact Person': 'Michael Brown (Technical Specialist)',
            'Phone/Email': 'michael@weathershield.co.za / 021-555-0022 / 079-234-5678',
            'Contract Expiry Date': '2025-09-30',
            'Preferred / Approved Vendor Indicator': 'Approved'
        },
        {
            'Supplier Name': 'CoolAir Systems',
            'Category Supplied': 'HVAC, Air Conditioning',
            'Contact Person': 'Ahmed Hassan (Technical Director)',
            'Phone/Email': 'ahmed@coolair.co.za / 021-555-0005 / 071-345-6789',
            'Contract Expiry Date': '2025-11-30',
            'Preferred / Approved Vendor Indicator': 'Preferred'
        },
        {
            'Supplier Name': 'ChillMax Pro',
            'Category Supplied': 'HVAC, Refrigerants & Components',
            'Contact Person': 'Lisa Chen (Business Development)',
            'Phone/Email': 'lisa@chillmax.co.za / 011-555-0025 / 083-678-9012',
            'Contract Expiry Date': '2026-07-15',
            'Preferred / Approved Vendor Indicator': 'Approved'
        },
        {
            'Supplier Name': 'SafeGuard Ltd',
            'Category Supplied': 'Safety, Personal Protective Equipment',
            'Contact Person': 'Susan Williams (Safety Consultant)',
            'Phone/Email': 'susan@safeguard.co.za / 031-555-0006 / 074-789-0123',
            'Contract Expiry Date': '2026-01-31',
            'Preferred / Approved Vendor Indicator': 'Preferred'
        },
        {
            'Supplier Name': 'MedCare Supplies',
            'Category Supplied': 'Safety, Medical & First Aid',
            'Contact Person': 'Dr. Patricia Adams (Medical Advisor)',
            'Phone/Email': 'patricia@medcare.co.za / 021-555-0028 / 072-890-1234',
            'Contract Expiry Date': '2026-12-31',
            'Preferred / Approved Vendor Indicator': 'Approved'
        },
        {
            'Supplier Name': 'CeilingPro SA',
            'Category Supplied': 'Ceiling Tiles, Suspended Systems',
            'Contact Person': 'Robert Taylor (Project Manager)',
            'Phone/Email': 'robert@ceilingpro.co.za / 011-555-0030 / 075-123-4567',
            'Contract Expiry Date': '2026-04-30',
            'Preferred / Approved Vendor Indicator': 'Approved'
        },
        {
            'Supplier Name': 'SecureTech SA',
            'Category Supplied': 'Access Control, Security Systems',
            'Contact Person': 'Mark Stevens (Security Solutions Manager)',
            'Phone/Email': 'mark@securetech.co.za / 031-555-0033 / 078-345-6789',
            'Contract Expiry Date': '2027-01-15',
            'Preferred / Approved Vendor Indicator': 'Preferred'
        }
    ]
    
    return sample_items, maintenance_data, suppliers_data

def populate_excel_file():
    """Populate the Excel file with sample data"""
    
    print("Creating sample inventory data...")
    sample_items, maintenance_data, suppliers_data = create_sample_data()
    
    # Load existing Excel file
    excel_file = 'STORES_INFRASTRUCTURE_ADMINISTRATION.xlsx'
    
    with pd.ExcelWriter(excel_file, mode='w', engine='openpyxl') as writer:
        
        # Update Dashboard KPIs
        dashboard_data = {
            'KPI': ['Total stock value', 'Items below reorder level', 'Top used items (last 30 days)', 'Average replenishment time'],
            'Value': [25000, 8, 'LED Bulbs, Paint Brushes, Safety Vests', '5.2 days']
        }
        dashboard_df = pd.DataFrame(dashboard_data)
        dashboard_df.to_excel(writer, sheet_name='Dashboard', index=False)
        print("Updated Dashboard")
        
        # Populate inventory categories
        for category, items in sample_items.items():
            df = pd.DataFrame(items)
            # Add missing columns to match expected structure
            expected_columns = [
                'Item Code', 'Description', 'Quantity on Hand', 'Unit of Measure',
                'Location', 'Min. Stock Level', 'Max. Stock Level', 'Supplier',
                'Last Purchase Date', 'Warranty Expiry (if applicable)', 'Cost/Unit', 'Total Value (auto-calc)'
            ]
            
            # Add missing columns with default values
            for col in expected_columns:
                if col not in df.columns:
                    if col == 'Last Purchase Date':
                        df[col] = '2025-07-15'  # Default date
                    elif col == 'Warranty Expiry (if applicable)':
                        df[col] = 'N/A'
                    else:
                        df[col] = ''
            
            # Reorder columns to match expected structure
            df = df[expected_columns]
            df.to_excel(writer, sheet_name=category, index=False)
            print(f"Populated {category} with {len(items)} items")
        
        # Add empty sheets for remaining categories
        remaining_categories = ['Ceiling Tiles', 'Decoration', 'Parking & Signage', 'Access Control']
        for category in remaining_categories:
            empty_df = pd.DataFrame(columns=[
                'Item Code', 'Description', 'Quantity on Hand', 'Unit of Measure',
                'Location', 'Min. Stock Level', 'Max. Stock Level', 'Supplier',
                'Last Purchase Date', 'Warranty Expiry (if applicable)', 'Cost/Unit', 'Total Value (auto-calc)'
            ])
            empty_df.to_excel(writer, sheet_name=category, index=False)
            print(f"Created empty {category} sheet")
        
        # Populate Maintenance Log
        maintenance_df = pd.DataFrame(maintenance_data)
        maintenance_df.to_excel(writer, sheet_name='Maintenance Log', index=False)
        print(f"Populated Maintenance Log with {len(maintenance_data)} entries")
        
        # Populate Suppliers & Contractors
        suppliers_df = pd.DataFrame(suppliers_data)
        suppliers_df.to_excel(writer, sheet_name='Suppliers & Contractors', index=False)
        print(f"Populated Suppliers with {len(suppliers_data)} entries")
    
    print(f"\nSuccessfully populated {excel_file} with sample data!")
    print("\nSample data includes:")
    print("- Electric: 7 items (some low stock)")
    print("- Plumbing: 6 items (some low stock)")
    print("- Carpentry: 5 items (some low stock)")
    print("- Painting: 5 items (some low stock)")
    print("- Aircon: 4 items (some low stock)")
    print("- Safety: 5 items (some low stock)")
    print("- Ceiling Tiles: 2 items")
    print("- Decoration: 2 items")
    print("- Parking & Signage: 2 items")
    print("- Access Control: 2 items")
    print("- Maintenance Log: 6 detailed maintenance activities")
    print("- Suppliers: 14 supplier contacts with full details")
    print("\nNow reload the web application to see the data!")

if __name__ == "__main__":
    populate_excel_file()