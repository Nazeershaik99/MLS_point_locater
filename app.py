from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from psycopg2.extras import RealDictCursor
import json
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import matplotlib.pyplot as plt
import matplotlib
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.lib.units import inch, cm

matplotlib.use('Agg')
import base64
from datetime import datetime
import os
import logging
import pytz

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_CONFIG = {
    'host': 'localhost',
    'database': 'database',
    'user': 'user_name',
    'password': 'password',
    'port': '5432'
}

# Create SQLAlchemy engine
DATABASE_URL = f"postgresql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"
engine = create_engine(DATABASE_URL)

# Global variables
CURRENT_USER = 'Nazeershaik99'
CURRENT_UTC_TIME = '2025-07-12 16:18:47'


def get_current_utc_time():
    """Get current UTC time in YYYY-MM-DD HH:MM:SS format"""
    return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')


def load_data():
    """Load all MLS data from PostgreSQL database"""
    try:
        query = "SELECT * FROM mslpoint"
        df = pd.read_sql_query(query, engine)
        logger.info(f"Successfully loaded {len(df)} records from database")

        # Convert column names to lowercase and replace spaces with underscores
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        return df
    except SQLAlchemyError as e:
        logger.error(f"Database query error: {e}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Unexpected error loading data: {e}")
        return pd.DataFrame()


# Initialize data
df = load_data()


@app.route('/')
def index():
    return render_template('index.html',
                           current_user=CURRENT_USER,
                           current_time=CURRENT_UTC_TIME)


@app.route('/api/districts')
def get_districts():
    """Get all distinct districts from database"""
    try:
        if df.empty:
            return jsonify([])

        districts = df[['district_code', 'district_name']].drop_duplicates().sort_values('district_name')
        districts_list = [
            {
                'District Code': row['district_code'],
                'District Name': row['district_name']
            }
            for _, row in districts.iterrows()
        ]
        return jsonify(districts_list)
    except Exception as e:
        logger.error(f"Error fetching districts: {e}")
        return jsonify({'error': 'Failed to fetch districts'}), 500


@app.route('/api/mandals/<district_code>')
def get_mandals(district_code):
    """Get all mandals for a specific district"""
    try:
        if df.empty:
            logger.error(f"No data available in dataframe for district {district_code}")
            return jsonify([])

        logger.info(f"Fetching mandals for district code: {district_code}")
        district_code = str(district_code)
        filtered_df = df[df['district_code'].astype(str) == district_code]
        logger.info(f"Found {len(filtered_df)} records for district {district_code}")

        if filtered_df.empty:
            logger.warning(f"No mandals found for district code {district_code}")
            return jsonify([])

        mandals = filtered_df[['mandal_code', 'mandal_name']].drop_duplicates().sort_values('mandal_name')
        mandals_list = []
        for _, row in mandals.iterrows():
            mandal_dict = {
                'Mandal Code': str(row['mandal_code']),
                'Mandal Name': str(row['mandal_name'])
            }
            mandals_list.append(mandal_dict)

        logger.info(f"Successfully retrieved {len(mandals_list)} mandals for district {district_code}")
        return jsonify(mandals_list)

    except Exception as e:
        logger.error(f"Error fetching mandals for district {district_code}: {str(e)}")
        return jsonify({
            'error': 'Failed to fetch mandals',
            'district_code': district_code,
            'timestamp': get_current_utc_time(),
            'user': CURRENT_USER
        }), 500


@app.route('/api/mls_points/<district_code>/<mandal_code>')
def get_mls_points(district_code, mandal_code):
    """Get all MLS points for a specific district and mandal"""
    try:
        if df.empty:
            logger.error("DataFrame is empty")
            return jsonify({
                'points': [],
                'message': 'No data available'
            })

        district_code = str(district_code)
        mandal_code = str(mandal_code)

        filtered_df = df[
            (df['district_code'].astype(str) == district_code) &
            (df['mandal_code'].astype(str) == mandal_code)
            ]

        logger.info(f"Found {len(filtered_df)} MLS points for district {district_code} and mandal {mandal_code}")

        if filtered_df.empty:
            return jsonify({
                'points': [],
                'message': 'No MLS points found for selected district and mandal'
            })

        mls_points = []
        for _, row in filtered_df.iterrows():
            try:
                longitude = row.get('mls_point_logitude', row.get('mls_point_longitude', 0.0))

                mls_point = {
                    'mls_code': str(row['mls_point_code']),
                    'mls_name': str(row['mls_point_name']),
                    'latitude': float(row['mls_point_latitude']) if pd.notna(row['mls_point_latitude']) else 0.0,
                    'longitude': float(longitude) if pd.notna(longitude) else 0.0,
                    'address': str(row['mls_point_address']),
                    'incharge_name': str(row['mls_point_incharge_name']),
                    'phone': str(row['phone_number']),
                    'storage_capacity': str(row.get('storage_capacity_in_mts.', '')),
                    'godown_area': str(row.get('godown_area_in_sq._ft.', ''))
                }

                if mls_point['latitude'] == 0.0 or mls_point['longitude'] == 0.0:
                    logger.warning(f"Invalid coordinates for MLS point {mls_point['mls_code']}")
                    continue

                mls_points.append(mls_point)
                logger.info(f"Successfully processed MLS point: {mls_point['mls_code']}")

            except Exception as e:
                logger.error(f"Error processing MLS point row: {e}")
                continue

        response_data = {
            'points': mls_points,
            'message': f"Found {len(mls_points)} MLS points" if mls_points else "No valid MLS points found",
            'timestamp': get_current_utc_time()
        }

        return jsonify(response_data)

    except Exception as e:
        logger.error(f"Error fetching MLS points: {e}")
        return jsonify({
            'points': [],
            'error': str(e),
            'message': 'Error loading MLS points',
            'timestamp': get_current_utc_time()
        }), 500


@app.route('/api/mls_details/<mls_code>')
def get_mls_details(mls_code):
    """Get detailed information for a specific MLS point"""
    try:
        if df.empty:
            logger.error("No data available")
            return jsonify({'error': 'No data available'}), 404

        mls_code = str(mls_code)
        logger.info(f"Fetching details for MLS code: {mls_code}")

        mls_record = df[df['mls_point_code'].astype(str) == mls_code]

        if mls_record.empty:
            logger.warning(f"MLS point not found: {mls_code}")
            return jsonify({'error': 'MLS point not found'}), 404

        mls_data = mls_record.iloc[0].to_dict()

        # Helper function to safely get values
        def safe_get(key, default='N/A'):
            value = mls_data.get(key, default)
            return str(value) if pd.notna(value) and value != '' else default

        # Format the complete response data with all available fields
        formatted_data = {
            'MLS Point Code': safe_get('mls_point_code'),
            'MLS Point Name': safe_get('mls_point_name'),
            'MLS Point Address': safe_get('mls_point_address'),
            'District Name': safe_get('district_name'),
            'Mandal Name': safe_get('mandal_name'),
            'MLS Point Latitude': safe_get('mls_point_latitude'),
            'MLS Point Longitude': safe_get('mls_point_logitude'),
            'MLS Point Incharge CFMS': safe_get('mls_point_incharge_cfms'),
            'Corporation EMP ID': safe_get('corporation_emp_id'),
            'MLS Point Incharge Name': safe_get('mls_point_incharge_name'),
            'Designation': safe_get('designation'),
            'Aadhaar Number': safe_get('aadhaar_number'),
            'Phone Number': safe_get('phone_number'),
            'DEO CFMS ID-Corporation Emp ID': safe_get('deo_cfms_id-corporation_emp_id'),
            'DEO Name': safe_get('deo_name'),
            'DEO Aadhaar Number': safe_get('deo_aadhaar_number'),
            'DEO Phone Number': safe_get('deo_phone_number'),
            'Godown Area in Sq. Ft.': safe_get('godown_area_in_sq._ft.'),
            'Storage Capacity in MTs.': safe_get('storage_capacity_in_mts.'),
            'MLS Point Owned (or) Hired ?': safe_get('mls_point_owned_(or)_hired_?'),
            'If Rented, (Private / Amc / Other)': safe_get('if_rented,_(private_/_amc_/_other)'),
            'Weighbridge Available? (Yes / No)': safe_get('weighbridge_available?_(yes_/_no)'),
            'No. of CC Camers installed': safe_get('no._of_cc_camers_installed'),
            'Whether all Cameras are in working condition? (Yes/No)': safe_get('whether_all_cameras_are_in_working_condition?_(yes/no)'),
            'CC Cameras are maintained by Vendor': safe_get('cc_cameras_are_maintained_by_vendor'),
            'Number of Hamalies Working': safe_get('number_of_hamalies_working'),
            'Number of Stage - II Vehicles Registered': safe_get('number_of_stage_-_ii_vehicles_registered'),
            'All Vehicles Having GPS Devices? (Yes/No)': safe_get('all_vehicles_having_gps_devices?_(yes/no)'),
            'Compound Wall Available? (Yes/No)': safe_get('compound_wall_available?_(yes/no)'),
            'Distance From Main Road To Reach MLS? (In Kms)': safe_get('distance_from_main_road_to_reach_mls?_(in_kms)'),
            'Internal Roads Available? (Yes/No)': safe_get('internal_roads_available?_(yes/no)'),
            'Solar System Available? (Yes/No)': safe_get('solar_system_available?_(yes/no)'),
            'Whether MLS Can Be Converted to Green Godown With Solar? (Yes/No)': safe_get('whether_mls_can_be_converted_to_green_godown_with_solar?_(yes/no)'),
            'When Was Last Time Minor Repairs Done?': safe_get('when_was_last_time_minor_repairs_done?'),
            'When Was Last Time Paintings Done?': safe_get('when_was_last_time_paintings_done?')
        }

        logger.info(f"Successfully retrieved details for MLS code: {mls_code}")
        return jsonify(formatted_data)

    except Exception as e:
        logger.error(f"Error fetching MLS details for code {mls_code}: {str(e)}")
        return jsonify({
            'error': 'Failed to fetch MLS details',
            'message': str(e)
        }), 500


def create_utilization_chart():
    """Create a sample utilization chart"""
    years = ['2020-21', '2021-22', '2022-23', '2023-24', '2024-25']
    utilization = [65, 78, 85, 82, 88]

    plt.figure(figsize=(8, 4))
    bars = plt.bar(years, utilization, color=['#4472C4', '#70AD47', '#FFC000', '#E15759', '#A5A5A5'])
    plt.title('% Utilization Over the Years', fontsize=14, fontweight='bold')
    plt.ylabel('Utilization %')
    plt.ylim(0, 100)

    for bar, value in zip(bars, utilization):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                 f'{value}%', ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()

    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
    img_buffer.seek(0)
    plt.close()

    return img_buffer


@app.route('/api/download_pdf/<mls_code>')
def download_pdf(mls_code):
    """Generate and download comprehensive PDF report for specific MLS point"""
    try:
        if df.empty:
            return jsonify({'error': 'No data available'}), 404

        mls_code = str(mls_code)
        mls_record = df[df['mls_point_code'].astype(str) == mls_code]

        if mls_record.empty:
            return jsonify({'error': 'MLS point not found'}), 404

        mls_data = mls_record.iloc[0]

        # Helper function to safely get values
        def safe_get(key, default='N/A'):
            value = mls_data.get(key, default)
            return str(value) if pd.notna(value) and value != '' else default

        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5 * inch, bottomMargin=0.5 * inch)

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=12,
            spaceAfter=6,
            spaceBefore=12,
            textColor=colors.white,
            backColor=colors.darkblue,
            alignment=TA_CENTER
        )

        # Story (content)
        story = []

        # Title
        title = Paragraph("Comprehensive MLS Point Details Report", title_style)
        story.append(title)
        story.append(Spacer(1, 12))

        # Basic Information Section
        story.append(Paragraph("Basic Information", heading_style))
        basic_info_data = [
            ["MLS Point Code:", safe_get('mls_point_code')],
            ["MLS Point Name:", safe_get('mls_point_name')],
            ["Address:", safe_get('mls_point_address')],
            ["District:", safe_get('district_name')],
            ["Mandal:", safe_get('mandal_name')],
            ["Latitude:", safe_get('mls_point_latitude')],
            ["Longitude:", safe_get('mls_point_logitude')]
        ]
        story.append(create_table(basic_info_data))
        story.append(Spacer(1, 12))

        # Personnel Information Section
        story.append(Paragraph("Personnel Information", heading_style))
        personnel_data = [
            ["MLS Point Incharge CFMS:", safe_get('mls_point_incharge_cfms')],
            ["Corporation EMP ID:", safe_get('corporation_emp_id')],
            ["Incharge Name:", safe_get('mls_point_incharge_name')],
            ["Designation:", safe_get('designation')],
            ["Aadhaar Number:", safe_get('aadhaar_number')],
            ["Phone Number:", safe_get('phone_number')],
            ["DEO CFMS ID-Corporation Emp ID:", safe_get('deo_cfms_id-corporation_emp_id')],
            ["DEO Name:", safe_get('deo_name')],
            ["DEO Aadhaar Number:", safe_get('deo_aadhaar_number')],
            ["DEO Phone Number:", safe_get('deo_phone_number')]
        ]
        story.append(create_table(personnel_data))
        story.append(Spacer(1, 12))

        # Infrastructure Section
        story.append(Paragraph("Infrastructure Details", heading_style))
        infrastructure_data = [
            ["Godown Area (Sq. Ft.):", safe_get('godown_area_in_sq._ft.')],
            ["Storage Capacity (MTs):", safe_get('storage_capacity_in_mts.')],
            ["Owned or Hired:", safe_get('mls_point_owned_(or)_hired_?')],
            ["If Rented (Private/AMC/Other):", safe_get('if_rented,_(private_/_amc_/_other)')],
            ["Weighbridge Available:", safe_get('weighbridge_available?_(yes_/_no)')],
            ["Compound Wall Available:", safe_get('compound_wall_available?_(yes/no)')],
            ["Distance from Main Road (Kms):", safe_get('distance_from_main_road_to_reach_mls?_(in_kms)')],
            ["Internal Roads Available:", safe_get('internal_roads_available?_(yes/no)')]
        ]
        story.append(create_table(infrastructure_data))
        story.append(Spacer(1, 12))

        # Technology & Equipment Section
        story.append(Paragraph("Technology & Equipment", heading_style))
        technology_data = [
            ["CC Cameras Installed:", safe_get('no._of_cc_camers_installed')],
            ["All Cameras Working:", safe_get('whether_all_cameras_are_in_working_condition?_(yes/no)')],
            ["Cameras Maintained by Vendor:", safe_get('cc_cameras_are_maintained_by_vendor')],
            ["Solar System Available:", safe_get('solar_system_available?_(yes/no)')],
            ["Can Convert to Green Godown:", safe_get('whether_mls_can_be_converted_to_green_godown_with_solar?_(yes/no)')],
            ["All Vehicles Have GPS:", safe_get('all_vehicles_having_gps_devices?_(yes/no)')]
        ]
        story.append(create_table(technology_data))
        story.append(Spacer(1, 12))

        # Operations Section
        story.append(Paragraph("Operations", heading_style))
        operations_data = [
            ["Number of Hamalies Working:", safe_get('number_of_hamalies_working')],
            ["Stage-II Vehicles Registered:", safe_get('number_of_stage_-_ii_vehicles_registered')]
        ]
        story.append(create_table(operations_data))
        story.append(Spacer(1, 12))

        # Maintenance Section
        story.append(Paragraph("Maintenance History", heading_style))
        maintenance_data = [
            ["Last Minor Repairs Done:", safe_get('when_was_last_time_minor_repairs_done?')],
            ["Last Painting Done:", safe_get('when_was_last_time_paintings_done?')]
        ]
        story.append(create_table(maintenance_data))
        story.append(Spacer(1, 12))

        # Utilization Chart
        story.append(Paragraph("Utilization Analysis", heading_style))
        chart_buffer = create_utilization_chart()
        chart_img = Image(chart_buffer, width=6 * inch, height=3 * inch)
        story.append(chart_img)

        # Footer
        story.append(Spacer(1, 20))
        footer_text = f"Report generated on {get_current_utc_time()} by {CURRENT_USER}"
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.grey
        )
        story.append(Paragraph(footer_text, footer_style))

        # Build PDF
        doc.build(story)
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'Comprehensive_MLS_Report_{mls_code}.pdf',
            mimetype='application/pdf'
        )

    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        return jsonify({'error': 'Failed to generate PDF', 'message': str(e)}), 500


def create_table(data):
    """Helper function to create a formatted table"""
    table = Table(data, colWidths=[2.5 * inch, 3.5 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    return table


@app.route('/api/refresh_data')
def refresh_data():
    """Refresh data from database"""
    global df
    try:
        df = load_data()
        return jsonify({
            'message': f'Data refreshed successfully. {len(df)} records loaded.',
            'timestamp': get_current_utc_time(),
            'user': CURRENT_USER
        })
    except Exception as e:
        logger.error(f"Error refreshing data: {e}")
        return jsonify({'error': 'Failed to refresh data'}), 500


@app.route('/api/health')
def health_check():
    """Health check endpoint to verify database connectivity"""
    try:
        test_query = "SELECT 1"
        result = pd.read_sql_query(test_query, engine)
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'records_count': len(df),
            'timestamp': get_current_utc_time(),
            'user': CURRENT_USER
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': get_current_utc_time(),
            'user': CURRENT_USER
        }), 500


@app.route('/api/user')
def get_current_user():
    """Get current user information"""
    return jsonify({
        'username': CURRENT_USER,
        'timestamp': CURRENT_UTC_TIME
    })


@app.before_request
def before_request():
    """Middleware to update current time before each request"""
    global CURRENT_UTC_TIME
    CURRENT_UTC_TIME = get_current_utc_time()


if __name__ == '__main__':
    CURRENT_UTC_TIME = get_current_utc_time()
    logger.info(f"Starting application at {CURRENT_UTC_TIME}")
    logger.info(f"Current user: {CURRENT_USER}")
    app.run(debug=True, host='0.0.0.0', port=5000)