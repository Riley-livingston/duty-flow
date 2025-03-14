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
import atexit
import shutil

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Create uploads directory if it doesn't exist
UPLOAD_FOLDER = 'uploads'
# Create a temporary directory for results that will be cleaned up when the app exits
RESULTS_FOLDER = tempfile.mkdtemp(prefix='dutyflow_results_')
GENERATED_FORMS_FOLDER = tempfile.mkdtemp(prefix='dutyflow_forms_')

# Register cleanup function to remove temp directories on application exit
@atexit.register
def cleanup_temp_files():
    """Clean up temporary files when the application exits"""
    try:
        app.logger.info(f"Cleaning up temporary directories: {RESULTS_FOLDER}, {GENERATED_FORMS_FOLDER}")
        
        # Remove all files from the uploads directory
        for filename in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                
        # Remove the temporary directories
        shutil.rmtree(RESULTS_FOLDER, ignore_errors=True)
        shutil.rmtree(GENERATED_FORMS_FOLDER, ignore_errors=True)
        
        app.logger.info("Temporary files cleaned up successfully")
    except Exception as e:
        app.logger.error(f"Error cleaning up temporary files: {str(e)}")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)
os.makedirs(GENERATED_FORMS_FOLDER, exist_ok=True)

# Log the temporary directories
print(f"Using temporary directories for storage:")
print(f"Results: {RESULTS_FOLDER}")
print(f"Forms: {GENERATED_FORMS_FOLDER}")

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

@app.route('/api/analyze', methods=['GET'])
def analyze_data():
    """API endpoint to analyze import and export data based on IDs"""
    try:
        import_id = request.args.get('import_id')
        export_id = request.args.get('export_id')
        
        if not import_id:
            return jsonify({'error': 'Import ID is required'}), 400
        
        # Retrieve import data
        import_doc = Document.query.filter_by(id=import_id).first()
        if not import_doc:
            return jsonify({'error': f'Import document with ID {import_id} not found'}), 404
            
        import_file_path = import_doc.file_path
        app.logger.info(f"Using import file: {import_file_path}")
        
        # Check if file exists
        if not os.path.exists(import_file_path):
            app.logger.error(f"Import file not found: {import_file_path}")
            # Try to find the file in the uploads directory if using a relative path
            base_filename = os.path.basename(import_file_path)
            alt_path = os.path.join('uploads', base_filename)
            if os.path.exists(alt_path):
                app.logger.info(f"Found import file at alternative path: {alt_path}")
                import_file_path = alt_path
            else:
                return jsonify({'error': f'Import file not found: {import_file_path}'}), 404
        
        # If export ID is provided, retrieve export data
        export_file_path = None
        if export_id:
            export_doc = Document.query.filter_by(id=export_id).first()
            if not export_doc:
                return jsonify({'error': f'Export document with ID {export_id} not found'}), 404
            export_file_path = export_doc.file_path
            app.logger.info(f"Using export file: {export_file_path}")
            
            # Check if file exists
            if not os.path.exists(export_file_path):
                app.logger.error(f"Export file not found: {export_file_path}")
                # Try to find the file in the uploads directory if using a relative path
                base_filename = os.path.basename(export_file_path)
                alt_path = os.path.join('uploads', base_filename)
                if os.path.exists(alt_path):
                    app.logger.info(f"Found export file at alternative path: {alt_path}")
                    export_file_path = alt_path
                else:
                    return jsonify({'error': f'Export file not found: {export_file_path}'}), 404
        
        # Perform analysis based on the data
        if export_file_path:
            # Analyze with both import and export data
            imports_df, exports_df = scan_transactions_with_exports(import_file_path, export_file_path)
            
            # Convert DataFrames to dictionaries for easier processing
            transactions = imports_df.to_dict('records')
            export_transactions = exports_df.to_dict('records')
            
            # Save results to a file
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            results_file = os.path.join(RESULTS_FOLDER, f'analysis_results_{timestamp}.csv')
            save_results(imports_df, results_file)
            
            summary_report = generate_summary_report_with_exports(imports_df, exports_df)
            
            # Count eligible transactions
            eligible_count = int(imports_df['is_eligible'].sum())
            matched_count = int(imports_df['has_export_match'].sum()) if 'has_export_match' in imports_df.columns else 0
            
            # Calculate total duty paid and potential refund
            total_duty = float(imports_df['duty_paid'].sum())
            total_refund = float(imports_df[imports_df['is_eligible']]['potential_refund'].sum() if 'is_eligible' in imports_df.columns else 0)
            
            # Format data for matches
            matches = []
            for i, imp in imports_df.iterrows():
                if imp.get('has_export_match', False):
                    # Find matching export transactions
                    matching_exports = exports_df[exports_df['product_id'] == imp['product_id']]
                    
                    for j, exp in matching_exports.iterrows():
                        if exp.get('matched_to_import', False):
                            matches.append({
                                'product_id': imp['product_id'],
                                'import_date': imp['import_date'].strftime('%Y-%m-%d') if isinstance(imp['import_date'], pd.Timestamp) else imp['import_date'],
                                'import_qty': int(imp['quantity']),
                                'duty_paid': float(imp['duty_paid']),
                                'export_date': exp['export_date'].strftime('%Y-%m-%d') if isinstance(exp['export_date'], pd.Timestamp) else exp['export_date'],
                                'export_qty': int(exp['quantity']),
                                'refund_amount': float(imp['potential_refund'])
                            })
            
            # Format data for unmatched imports
            unmatched_imports = []
            for i, imp in imports_df.iterrows():
                if not imp.get('has_export_match', False):
                    unmatched_imports.append({
                        'product_id': imp['product_id'],
                        'import_date': imp['import_date'].strftime('%Y-%m-%d') if isinstance(imp['import_date'], pd.Timestamp) else imp['import_date'],
                        'quantity': int(imp['quantity']),
                        'duty_paid': float(imp['duty_paid']),
                        'eligible_for_future': bool(imp.get('is_eligible', False))
                    })
            
            return jsonify({
                'import_count': len(transactions),
                'export_count': len(export_transactions),
                'eligible_transactions': eligible_count,
                'matched_exports': matched_count,
                'total_duty_paid': total_duty,
                'potential_refund': total_refund,
                'matches': matches,
                'unmatched_imports': unmatched_imports,
                'results_file': results_file
            })
        else:
            # Analyze with only import data
            imports_df = scan_transactions(import_file_path)
            
            # Convert DataFrame to dictionary for easier processing
            transactions = imports_df.to_dict('records')
            
            # Save results to a file
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            results_file = os.path.join(RESULTS_FOLDER, f'analysis_results_{timestamp}.csv')
            save_results(imports_df, results_file)
            
            summary_report = generate_summary_report(imports_df)
            
            # Count eligible transactions
            eligible_count = int(imports_df['is_eligible'].sum())
            
            # Calculate total duty paid and potential refund
            total_duty = float(imports_df['duty_paid'].sum())
            total_refund = float(imports_df[imports_df['is_eligible']]['potential_refund'].sum() if 'is_eligible' in imports_df.columns else 0)
            
            # Format data for unmatched imports (all imports in this case)
            unmatched_imports = []
            for i, imp in imports_df.iterrows():
                unmatched_imports.append({
                    'product_id': imp['product_id'],
                    'import_date': imp['import_date'].strftime('%Y-%m-%d') if isinstance(imp['import_date'], pd.Timestamp) else imp['import_date'],
                    'quantity': int(imp['quantity']),
                    'duty_paid': float(imp['duty_paid']),
                    'eligible_for_future': bool(imp.get('is_eligible', False))
                })
            
            return jsonify({
                'import_count': len(transactions),
                'export_count': 0,
                'eligible_transactions': eligible_count,
                'matched_exports': 0,
                'total_duty_paid': total_duty,
                'potential_refund': total_refund,
                'matches': [],
                'unmatched_imports': unmatched_imports,
                'results_file': results_file
            })
    
    except Exception as e:
        app.logger.error(f"Error in analyze_data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-form-wizard', methods=['POST'])
def generate_form_wizard():
    """API endpoint to generate CBP Form 7551 from data in the wizard flow"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['company_name', 'company_address', 'company_city', 
                          'company_state', 'company_zip', 'company_ein',
                          'contact_name', 'contact_phone', 'contact_email',
                          'results_file']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Generate form
        results_file = data.get('results_file')
        results_path = os.path.join(RESULTS_FOLDER, results_file)
        
        if not os.path.exists(results_path):
            return jsonify({'error': 'Results file not found'}), 404
        
        # Read results data
        results_df = pd.read_csv(results_path)
        eligible_df = results_df[results_df['is_eligible'] == True]
        
        if eligible_df.empty:
            return jsonify({'error': 'No eligible transactions found'}), 400
        
        # Generate form
        company_info = {
            'company_name': data.get('company_name'),
            'company_address': data.get('company_address'),
            'company_city': data.get('company_city'),
            'company_state': data.get('company_state'),
            'company_zip': data.get('company_zip'),
            'company_ein': data.get('company_ein'),
            'contact_name': data.get('contact_name'),
            'contact_phone': data.get('contact_phone'),
            'contact_email': data.get('contact_email')
        }
        
        # Use timestamp in filename for uniqueness
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        output_filename = f"cbp_form_7551_{timestamp}.pdf"
        output_path = os.path.join(GENERATED_FORMS_FOLDER, output_filename)
        
        generator = CBPFormGenerator()
        generator.generate_form(eligible_df, company_info, output_path)
        
        return jsonify({
            'success': True,
            'form_path': output_filename,
            'form_url': f'/api/download/{output_filename}'
        })
        
    except Exception as e:
        app.logger.error(f"Error in generate_form_wizard: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/preview/<path:filename>', methods=['GET'])
def preview_file(filename):
    """Preview a file (especially for PDF)"""
    try:
        # Determine which directory to look in based on filename
        if filename.startswith('generated_forms/'):
            # Strip the directory part from the filename
            filename = filename.replace('generated_forms/', '')
            return send_from_directory(GENERATED_FORMS_FOLDER, filename)
        elif filename.startswith('uploads/'):
            filename = filename.replace('uploads/', '')
            return send_from_directory(UPLOAD_FOLDER, filename)
        elif filename.startswith('results/'):
            filename = filename.replace('results/', '')
            return send_from_directory(RESULTS_FOLDER, filename)
        else:
            # Try to find the file in the generated forms folder first
            if os.path.exists(os.path.join(GENERATED_FORMS_FOLDER, filename)):
                return send_from_directory(GENERATED_FORMS_FOLDER, filename)
            else:
                return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        app.logger.error(f"Error in preview_file: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/test-with-samples', methods=['GET'])
def test_with_samples():
    """API endpoint to test with sample import and export data"""
    try:
        # Use the sample files in the uploads directory
        import_file_path = 'uploads/sample_imports.csv'
        export_file_path = 'uploads/sample_exports.csv'
        
        # Check if files exist
        if not os.path.exists(import_file_path):
            return jsonify({'error': f'Sample import file not found: {import_file_path}'}), 404
        
        if not os.path.exists(export_file_path):
            return jsonify({'error': f'Sample export file not found: {export_file_path}'}), 404
        
        # Process files
        imports_df, exports_df = scan_transactions_with_exports(import_file_path, export_file_path)
        
        # Save results
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = os.path.join(RESULTS_FOLDER, f'sample_analysis_{timestamp}.csv')
        save_results(imports_df, results_file)
        
        # Generate summary
        summary_report = generate_summary_report_with_exports(imports_df, exports_df)
        
        # Count eligible transactions
        eligible_count = int(imports_df['is_eligible'].sum())
        matched_count = int(imports_df['has_export_match'].sum()) if 'has_export_match' in imports_df.columns else 0
        
        # Calculate total duty paid and potential refund
        total_duty = float(imports_df['duty_paid'].sum())
        total_refund = float(imports_df[imports_df['is_eligible']]['potential_refund'].sum() if 'is_eligible' in imports_df.columns else 0)
        
        # Format data for matches
        matches = []
        for i, imp in imports_df.iterrows():
            if imp.get('has_export_match', False):
                # Find matching export transactions
                matching_exports = exports_df[exports_df['product_id'] == imp['product_id']]
                
                for j, exp in matching_exports.iterrows():
                    if exp.get('matched_to_import', False):
                        matches.append({
                            'product_id': imp['product_id'],
                            'import_date': imp['import_date'].strftime('%Y-%m-%d') if isinstance(imp['import_date'], pd.Timestamp) else imp['import_date'],
                            'import_qty': int(imp['quantity']),
                            'duty_paid': float(imp['duty_paid']),
                            'export_date': exp['export_date'].strftime('%Y-%m-%d') if isinstance(exp['export_date'], pd.Timestamp) else exp['export_date'],
                            'export_qty': int(exp['quantity']),
                            'refund_amount': float(imp['potential_refund'])
                        })
        
        # Format data for unmatched imports
        unmatched_imports = []
        for i, imp in imports_df.iterrows():
            if not imp.get('has_export_match', False):
                unmatched_imports.append({
                    'product_id': imp['product_id'],
                    'import_date': imp['import_date'].strftime('%Y-%m-%d') if isinstance(imp['import_date'], pd.Timestamp) else imp['import_date'],
                    'quantity': int(imp['quantity']),
                    'duty_paid': float(imp['duty_paid']),
                    'eligible_for_future': bool(imp.get('is_eligible', False))
                })
        
        return jsonify({
            'import_count': len(imports_df),
            'export_count': len(exports_df),
            'eligible_transactions': eligible_count,
            'matched_exports': matched_count,
            'total_duty_paid': total_duty,
            'potential_refund': total_refund,
            'matches': matches,
            'unmatched_imports': unmatched_imports,
            'results_file': results_file,
            'summary': summary_report
        })
    
    except Exception as e:
        app.logger.error(f"Error in test_with_samples: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Add this before running the app to create all tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5000) 