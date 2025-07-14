MLS Point Locator
A comprehensive web application for managing and visualizing MLS (Market Level Storage) points across different districts and mandals in Andhra Pradesh, India.
Features

Interactive Map Interface: View MLS points on an interactive map using Leaflet
Location-based Search: Filter MLS points by district and mandal
Detailed Information: Access comprehensive details for each MLS point
PDF Report Generation: Generate detailed PDF reports for individual MLS points
Responsive Design: Works seamlessly on desktop and mobile devices
Real-time Data: Fetches data from PostgreSQL database

Technology Stack
Frontend

HTML5/CSS3: Modern responsive design
JavaScript: Interactive functionality
Leaflet.js: Interactive mapping library
OpenStreetMap: Map tiles

Backend

Python 3.x: Core backend language
Flask: Web framework
PostgreSQL: Database system
SQLAlchemy: Database ORM

Libraries & Dependencies

pandas: Data manipulation and analysis
psycopg2: PostgreSQL adapter
reportlab: PDF generation
matplotlib: Chart generation

Prerequisites
Before running the application, ensure you have the following installed:

Python 3.7 or higher
PostgreSQL database
pip (Python package manager)

Installation

Clone the repository (or save the files to your project directory):
bashgit clone <repository-url>
cd mls-point-locator

Create a virtual environment:
bashpython -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install required packages:
bashpip install flask pandas sqlalchemy psycopg2-binary reportlab matplotlib


Database Setup

Create PostgreSQL database:
sqlCREATE DATABASE postgres;

Create the MLS points table:
sqlCREATE TABLE mslpoint (
    district_code VARCHAR(10),
    district_name VARCHAR(100),
    mandal_code VARCHAR(10),
    mandal_name VARCHAR(100),
    mls_point_code VARCHAR(20) PRIMARY KEY,
    mls_point_name VARCHAR(200),
    mls_point_address TEXT,
    mls_point_latitude DECIMAL(10, 8),
    mls_point_logitude DECIMAL(11, 8),
    mls_point_incharge_cfms VARCHAR(50),
    corporation_emp_id VARCHAR(50),
    mls_point_incharge_name VARCHAR(100),
    designation VARCHAR(100),
    aadhaar_number VARCHAR(20),
    phone_number VARCHAR(20),
    -- Add other columns as needed
);

Update database configuration in app.py:
pythonDATABASE_CONFIG = {
    'host': 'localhost',
    'database': 'postgres',
    'user': 'your_username',
    'password': 'your_password',
    'port': '5432'
}


Project Structure
mls-point-locator/
├── app.py                 # Main Flask application
├── templates/
│   └── index.html        # Frontend template (or standalone HTML)
├── static/               # Static files (if using Flask templates)
├── assets/               # Icons and images
├── requirements.txt      # Python dependencies
└── README.md            # This file
Configuration
Environment Variables
You can set the following environment variables or update the configuration in app.py:

DATABASE_HOST: PostgreSQL host (default: localhost)
DATABASE_NAME: Database name (default: postgres)
DATABASE_USER: Database username (default: postgres)
DATABASE_PASSWORD: Database password (default: 1234)
DATABASE_PORT: Database port (default: 5432)

User Configuration
Update the global variables in app.py:
pythonCURRENT_USER = 'YourUsername'
CURRENT_UTC_TIME = '2025-07-12 16:18:47'
Usage

Start the application:
bashpython app.py

Access the application:
Open your web browser and navigate to http://localhost:5000
Using the application:

Select a district from the dropdown
Select a mandal from the second dropdown
Click "Load MLS Points" to view points on the map
Click on map markers to view basic information
Click "View Details" in the popup to see comprehensive information
Generate PDF reports using the "Download PDF Report" button



API Endpoints
Core Endpoints

GET / - Main application interface
GET /api/districts - Get all districts
GET /api/mandals/<district_code> - Get mandals for a district
GET /api/mls_points/<district_code>/<mandal_code> - Get MLS points
GET /api/mls_details/<mls_code> - Get detailed information for an MLS point
GET /api/download_pdf/<mls_code> - Generate and download PDF report

Utility Endpoints

GET /api/health - Health check and database connectivity
GET /api/refresh_data - Refresh data from database
GET /api/user - Get current user information

Features in Detail
Interactive Map

Powered by Leaflet.js with OpenStreetMap tiles
Responsive markers for each MLS point
Popup information with quick details
Auto-fit bounds to show all markers

PDF Report Generation

Comprehensive reports with all MLS point details
Organized sections: Basic Info, Personnel, Infrastructure, Technology, Operations, Maintenance
Utilization charts and graphs
Professional formatting with ReportLab

Data Management

Real-time data fetching from PostgreSQL
Error handling and validation
Efficient data filtering and processing

Database Schema
The application expects a table named mslpoint with the following key columns:

district_code, district_name
mandal_code, mandal_name
mls_point_code, mls_point_name
mls_point_address
mls_point_latitude, mls_point_logitude
mls_point_incharge_name, phone_number
storage_capacity_in_mts.
godown_area_in_sq._ft.
And many other operational fields
