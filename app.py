from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import tempfile
import pandas as pd
from duty_scanner import scan_transactions, scan_transactions_with_exports, generate_summary_report, generate_summary_report_with_exports, save_results
from pdf_generator import generate_form_from_eligible_transactions, generate_document_guide
import json
from flask_sqlalchemy import SQLAlchemy
from models.db import db
from models.transactions import ImportTransaction, ExportTransaction
from document_routes import document_bp
from models.document import Document

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Create uploads directory if it doesn't exist
UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# Add this after creating the Flask app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dutyflow.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Add this to register the blueprint
app.register_blueprint(document_bp)

@app.route('/api/scan', methods=['POST'])
def scan_files():
    """API endpoint to scan import files for analysis"""
    try:
        # Check if import file was uploaded
        if 'import_file' not in request.files:
            return jsonify({'error': 'Import file is required'}), 400
        
        import_file = request.files['import_file']
        if import_file.filename == '':
            return jsonify({'error': 'Import file is required'}), 400
        
        # Save import file
        import_path = os.path.join(UPLOAD_FOLDER, import_file.filename)
        import_file.save(import_path)
        
        # Process file
        transactions = scan_transactions(import_path)
        
        # Save results
        timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
        results_path = os.path.join(RESULTS_FOLDER, f'import_analysis_{timestamp}.csv')
        save_results(transactions, results_path)
        
        # Generate summary
        summary = generate_summary_report(transactions)
        
        # Convert DataFrame to JSON-friendly format
        transactions_json = transactions.to_dict(orient='records')
        total_duty = transactions['duty_paid'].sum()
        total_refund = transactions['potential_refund'].sum()
        count = len(transactions)
        eligible_count = transactions['is_eligible'].sum()
        
        return jsonify({
            'success': True,
            'summary': summary,
            'count': count,
            'eligibleCount': int(eligible_count),
            'totalDuty': float(total_duty),
            'totalRefund': float(total_refund),
            'transactions': transactions_json,
            'resultsFile': results_path
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-form', methods=['POST'])
def generate_form():
    """API endpoint to generate CBP Form 7551"""
    try:
        # Get company info from request
        company_info = request.json.get('company_info', {})
        
        # Get results file path
        results_file = request.json.get('results_file')
        if not results_file:
            return jsonify({'error': 'Results file is required'}), 400
        
        # Generate form
        pdf_path = generate_form_from_eligible_transactions(results_file, company_info)
        
        # Return path to generated PDF
        return jsonify({
            'success': True,
            'pdf_path': pdf_path
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<path:filename>', methods=['GET'])
def download_file(filename):
    """API endpoint to download generated files"""
    try:
        # Ensure the file exists
        if not os.path.exists(filename):
            return jsonify({'error': 'File not found'}), 404
        
        # Determine file type
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext == '.pdf':
            mimetype = 'application/pdf'
        elif file_ext == '.csv':
            mimetype = 'text/csv'
        else:
            mimetype = 'application/octet-stream'
        
        return send_file(filename, mimetype=mimetype, as_attachment=True)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test', methods=['GET'])
def test_api():
    """Simple endpoint to test if the API is running"""
    return jsonify({
        'status': 'success',
        'message': 'DutyFlow API is running'
    })

@app.route('/api/scan-with-exports', methods=['POST'])
def scan_with_exports():
    """API endpoint to scan import and export files for analysis"""
    try:
        # Check if import file was uploaded
        if 'import_file' not in request.files:
            return jsonify({'error': 'Import file is required'}), 400
        
        import_file = request.files['import_file']
        if import_file.filename == '':
            return jsonify({'error': 'Import file is required'}), 400
        
        # Check if export file was uploaded
        if 'export_file' not in request.files:
            return jsonify({'error': 'Export file is required for import-export analysis'}), 400
        
        export_file = request.files['export_file']
        if export_file.filename == '':
            return jsonify({'error': 'Export file is required for import-export analysis'}), 400
        
        # Save import file
        import_path = os.path.join(UPLOAD_FOLDER, import_file.filename)
        import_file.save(import_path)
        
        # Save export file
        export_path = os.path.join(UPLOAD_FOLDER, export_file.filename)
        export_file.save(export_path)
        
        # Process files
        transactions, export_transactions = scan_transactions_with_exports(import_path, export_path)
        
        # Save results
        timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
        results_path = os.path.join(RESULTS_FOLDER, f'import_export_analysis_{timestamp}.csv')
        save_results(transactions, results_path)
        
        # Generate summary
        summary = generate_summary_report_with_exports(transactions, export_transactions)
        
        # Convert DataFrames to JSON-friendly format
        transactions_json = transactions.to_dict(orient='records')
        export_transactions_json = export_transactions.to_dict(orient='records')
        
        total_duty = transactions['duty_paid'].sum()
        total_refund = transactions['potential_refund'].sum()
        count = len(transactions)
        eligible_count = transactions['is_eligible'].sum()
        matched_count = transactions['has_export_match'].sum() if 'has_export_match' in transactions.columns else 0
        
        return jsonify({
            'success': True,
            'summary': summary,
            'count': count,
            'eligibleCount': int(eligible_count),
            'matchedCount': int(matched_count),
            'totalDuty': float(total_duty),
            'totalRefund': float(total_refund),
            'transactions': transactions_json,
            'exportTransactions': export_transactions_json,
            'resultsFile': results_path
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-pdf-report', methods=['GET'])
def generate_pdf_report():
    """API endpoint to generate a PDF report from the most recent analysis"""
    try:
        # Find the most recent results file
        results_files = [f for f in os.listdir(RESULTS_FOLDER) if f.endswith('.csv')]
        if not results_files:
            return jsonify({'error': 'No analysis results found'}), 404
        
        # Sort by modification time (most recent first)
        results_files.sort(key=lambda f: os.path.getmtime(os.path.join(RESULTS_FOLDER, f)), reverse=True)
        most_recent_file = os.path.join(RESULTS_FOLDER, results_files[0])
        
        # Sample company info - in a real app, this would come from user settings
        company_info = {
            'name': 'Your Company Name',
            'address': '123 Business St, Suite 100',
            'city_state_zip': 'Anytown, ST 12345',
            'contact_name': 'Contact Person',
            'phone': '(555) 555-5555',
            'email': 'contact@yourcompany.com',
            'importer_number': 'IMPxxxxxxxx'
        }
        
        # Generate PDF
        pdf_path = generate_form_from_eligible_transactions(most_recent_file, company_info)
        
        # Return the PDF file for download
        return send_file(pdf_path, mimetype='application/pdf', as_attachment=True)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/documentation-guide', methods=['GET'])
def get_documentation_guide():
    """API endpoint to generate and serve a documentation guide PDF"""
    try:
        # Generate the guide
        guide_path = generate_document_guide()
        
        # Return the PDF file for download
        return send_file(guide_path, mimetype='application/pdf', as_attachment=True, download_name='DutyFlow_Documentation_Guide.pdf')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Add this before running the app to create all tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5000) 