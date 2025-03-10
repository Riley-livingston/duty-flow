from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import tempfile
import pandas as pd
from duty_scanner import scan_transactions, scan_transactions_with_exports, generate_summary_report, generate_summary_report_with_exports, save_results
from pdf_generator import generate_form_from_eligible_transactions, generate_document_guide, CBPFormGenerator, process_and_generate_form
import json
from flask_sqlalchemy import SQLAlchemy
from models.db import db
from models.transactions import ImportTransaction, ExportTransaction
from document_routes import document_bp
from models.document import Document
from werkzeug.utils import secure_filename
from enhanced_test_documents import TestDocumentGenerator, run_enhanced_test
import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Create uploads directory if it doesn't exist
UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results'
GENERATED_FORMS_FOLDER = 'generated_forms'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)
os.makedirs(GENERATED_FORMS_FOLDER, exist_ok=True)

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

@app.route('/api/generate-cbp-form', methods=['POST'])
def generate_cbp_form():
    try:
        # Check if the post request has the file parts
        if 'import_file' not in request.files or 'export_file' not in request.files:
            return jsonify({'message': 'Missing required files'}), 400
        
        import_file = request.files['import_file']
        export_file = request.files['export_file']
        company_info = json.loads(request.form.get('company_info', '{}'))
        
        # Validate files
        if import_file.filename == '' or export_file.filename == '':
            return jsonify({'message': 'No selected files'}), 400
        
        # Save files temporarily
        import_filename = secure_filename(import_file.filename)
        export_filename = secure_filename(export_file.filename)
        
        import_path = os.path.join(UPLOAD_FOLDER, import_filename)
        export_path = os.path.join(UPLOAD_FOLDER, export_filename)
        
        import_file.save(import_path)
        export_file.save(export_path)
        
        # Process files and generate PDF
        result = process_and_generate_form(import_path, export_path, company_info)
        
        # Return the URLs to the generated files
        form_url = f'/api/generated-forms/{os.path.basename(result["form"])}'
        attachment_url = f'/api/generated-forms/{os.path.basename(result["attachment"])}'
        
        return jsonify({
            'message': 'Form generated successfully',
            'pdf_url': form_url,
            'attachment_url': attachment_url
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500

@app.route('/api/generated-forms/<filename>')
def get_generated_form(filename):
    return send_from_directory(GENERATED_FORMS_FOLDER, filename)

@app.route('/api/generate-test-documents', methods=['POST'])
def generate_test_documents():
    """Generate realistic test documents for demonstration purposes"""
    try:
        data = request.json
        company_name = data.get('companyName', 'Test Company Inc.')
        num_entries = int(data.get('numEntries', 3))
        
        # Initialize the document generator
        generator = TestDocumentGenerator(company_name)
        
        # Generate the complete drawback package
        package = generator.generate_complete_drawback_package(num_entries)
        
        # Create company info for form filling
        company_info = {
            "name": company_name,
            "address": "123 Trade Street, Business City, CA 90001",
            "city_state_zip": "Business City, CA 90001",
            "contact_name": "Jane Smith",
            "phone": "(555) 555-5555",
            "email": "jane@testcompany.com",
            "importer_number": generator.company_ein
        }
        
        # Generate the filled drawback form
        filled_form_path = fill_drawback_form(
            package['import_entries'],
            package['export_docs'],
            company_info
        )
        
        # Prepare response with file paths and structured data
        document_files = []
        
        # Add import entries
        for entry in package['import_entries']:
            entry_path = f"test_documents/import_entry_{entry['entry_number'].replace('-', '_')}.pdf"
            if os.path.exists(entry_path):
                document_files.append({
                    'path': entry_path,
                    'name': os.path.basename(entry_path),
                    'type': 'Import Entry',
                    'size': os.path.getsize(entry_path)
                })
        
        # Add export docs
        for doc in package['export_docs']:
            export_date_formatted = doc['export_date'].replace('/', '_')
            doc_path = f"test_documents/export_doc_{export_date_formatted}.pdf"
            if os.path.exists(doc_path):
                document_files.append({
                    'path': doc_path,
                    'name': os.path.basename(doc_path),
                    'type': 'Export Document',
                    'size': os.path.getsize(doc_path)
                })
        
        # Add summary
        summary_path = f"test_documents/drawback_summary_{datetime.datetime.now().strftime('%Y%m%d')}.xlsx"
        if os.path.exists(summary_path):
            document_files.append({
                'path': summary_path,
                'name': os.path.basename(summary_path),
                'type': 'Summary Spreadsheet',
                'size': os.path.getsize(summary_path)
            })
        
        # Add the filled form
        if os.path.exists(filled_form_path):
            document_files.append({
                'path': filled_form_path,
                'name': os.path.basename(filled_form_path),
                'type': 'Filled Drawback Form',
                'size': os.path.getsize(filled_form_path)
            })
        
        # Also run the enhanced test to generate additional documents
        run_enhanced_test()
        
        # Add any other generated documents
        for root, dirs, files in os.walk('test_documents'):
            for file in files:
                file_path = os.path.join(root, file)
                if not any(doc['path'] == file_path for doc in document_files):
                    file_type = 'Commercial Invoice' if 'invoice' in file.lower() else \
                                'Bill of Lading' if 'bill_of_lading' in file.lower() else \
                                'Export Proof' if 'export_proof' in file.lower() else 'Other'
                    document_files.append({
                        'path': file_path,
                        'name': file,
                        'type': file_type,
                        'size': os.path.getsize(file_path)
                    })
        
        return jsonify({
            'success': True,
            'message': f'Generated {num_entries} import entries and matching export documents',
            'documentFiles': document_files,
            'documentData': {
                'importEntries': package['import_entries'],
                'exportDocs': package['export_docs'],
                'companyInfo': company_info
            }
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Add this before running the app to create all tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5000) 