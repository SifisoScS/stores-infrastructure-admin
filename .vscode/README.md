# Derivco Stores Administration - VS Code Guide

## 🗂️ Project Structure
```
stores-in-web/
├── app.py                          # Main Flask application
├── data_loader.py                  # Excel data processing
├── analyze_excel.py               # Excel analysis utility
├── add_sample_data.py             # Sample data helper
├── requirements.txt               # Python dependencies
├── STORES_INFRASTRUCTURE_ADMINISTRATION.xlsx  # Data source
├── templates/                     # HTML templates
│   ├── base.html                 # Base template
│   ├── index.html                # Dashboard
│   ├── category_detail.html      # Category view
│   ├── low_stock.html            # Low stock page
│   ├── maintenance.html          # Maintenance log
│   └── suppliers.html            # Suppliers directory
├── static/                       # Static assets
│   ├── css/style.css            # Styles
│   └── js/main.js               # JavaScript
└── .vscode/                     # VS Code configuration
```

## 🚀 Running in VS Code

### Method 1: Debug Mode (Recommended)
1. Press `F5` or `Ctrl+F5`
2. Select "Flask App" configuration
3. Application runs with debugging enabled

### Method 2: Terminal
1. `Ctrl+`` (backtick) to open terminal
2. `python app.py`

### Method 3: Run Python File
1. Open `app.py`
2. `Ctrl+F5` to run without debugging

## 🔧 Key Features

### Debugging
- Set breakpoints by clicking line numbers
- Use F5 to start debugging
- Variable inspection in Debug panel

### Code Intelligence
- Auto-completion for Python and Flask
- HTML/CSS support for templates
- Jinja2 template syntax highlighting

### Integrated Terminal
- Run scripts directly in VS Code
- Multiple terminals for different tasks
- Git integration

## 📊 Working with Data

### Analyze Excel Structure
- Run "Analyze Excel" configuration
- Or: `python analyze_excel.py` in terminal

### Add Sample Data
- Run "Add Sample Data" configuration  
- Or: `python add_sample_data.py` in terminal

### Reload Application Data
- Use "Reload Data" button in web interface
- Or make API call: `POST /api/reload-data`

## 🌐 Access Points
- **Web App**: http://127.0.0.1:5000
- **API**: http://127.0.0.1:5000/api/
- **Debug**: VS Code Debug Console