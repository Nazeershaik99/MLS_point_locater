MLS Point Locator
A comprehensive web application for managing and visualizing Market Level Storage (MLS) Points across districts and mandals in Andhra Pradesh, India.

🚀 Features
🗺️ Interactive Map Interface – View MLS points with Leaflet and OpenStreetMap tiles

🔍 Location-based Search – Filter by district and mandal

📄 Detailed Information – View full MLS point data

🧾 PDF Report Generation – Generate detailed downloadable reports

📱 Responsive Design – Seamless across desktop and mobile

🔄 Real-time Data – Fetch data directly from PostgreSQL

🛠️ Technology Stack
Frontend
HTML5 / CSS3 – Modern responsive design

JavaScript – Dynamic interactivity

Leaflet.js – Mapping library

OpenStreetMap – Map tiles provider

Backend
Python 3.x – Core backend language

Flask – Web framework

PostgreSQL – Relational database

SQLAlchemy – ORM for database interaction

Libraries & Dependencies
pandas – Data analysis

psycopg2 – PostgreSQL adapter

reportlab – PDF generation

matplotlib – Chart and graph plotting

⚙️ Prerequisites
Make sure the following are installed:

Python 3.7+

PostgreSQL

pip (Python package manager)

🧰 Installation
bash
Copy
Edit
# Clone the repository
git clone <repository-url>
cd mls-point-locator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
🗄️ Database Setup
1. Create PostgreSQL Database:
sql
Copy
Edit
CREATE DATABASE postgres;
2. Create mslpoint Table:
sql
Copy
Edit
CREATE TABLE mslpoint (
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
    phone_number VARCHAR(20)
    -- Add more columns as required
);
3. Configure Database in app.py:
python
Copy
Edit
DATABASE_CONFIG = {
    'host': 'localhost',
    'database': 'postgres',
    'user': 'your_username',
    'password': 'your_password',
    'port': '5432'
}
📁 Project Structure
csharp
Copy
Edit
mls-point-locator/
├── app.py                  # Main Flask app
├── templates/
│   └── index.html          # Frontend template
├── static/                 # Static files (CSS/JS)
├── assets/                 # Images/icons
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
⚙️ Configuration
Environment Variables (Optional)
You can use environment variables or modify app.py:

DATABASE_HOST (default: localhost)

DATABASE_NAME (default: postgres)

DATABASE_USER (default: postgres)

DATABASE_PASSWORD (default: 1234)

DATABASE_PORT (default: 5432)

User Configuration
Update user settings in app.py:

python
Copy
Edit
CURRENT_USER = 'YourUsername'
CURRENT_UTC_TIME = '2025-07-12 16:18:47'
▶️ Usage
Start the App:
bash
Copy
Edit
python app.py
Access:
Open your browser at http://localhost:5000

How to Use:
Select a district from the dropdown

Choose a mandal

Click "Load MLS Points"

View markers on the map

Click marker → View Details

Download report using "Download PDF Report"

📡 API Endpoints
Core Endpoints
Method	Endpoint	Description
GET	/	Main UI
GET	/api/districts	List of all districts
GET	/api/mandals/<district_code>	Mandals by district
GET	/api/mls_points/<district_code>/<mandal_code>	MLS points list
GET	/api/mls_details/<mls_code>	MLS detailed view
GET	/api/download_pdf/<mls_code>	Generate PDF report

Utility Endpoints
Method	Endpoint	Description
GET	/api/health	Health check
GET	/api/refresh_data	Refresh from DB
GET	/api/user	Current user info

🧾 PDF Report Generation
Organized into Basic Info, Personnel, Infrastructure, Technology, Operations, Maintenance

Contains charts and graphs via matplotlib

Clean and professional layout using reportlab

🧠 Data Management
Real-time sync from PostgreSQL

Efficient data filtering and validation

Modular design for easy extension

🗃️ Database Schema
Key columns in mslpoint table:

district_code, district_name

mandal_code, mandal_name

mls_point_code, mls_point_name

mls_point_address

mls_point_latitude, mls_point_logitude

mls_point_incharge_name, phone_number

storage_capacity_in_mts, godown_area_in_sq._ft.

(Add other operational fields as needed)
