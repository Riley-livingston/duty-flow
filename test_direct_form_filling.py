import os
import sys
import webbrowser
from enhanced_test_documents import run_comprehensive_test

def test_direct_form_filling():
    """
    Generate realistic test documents, auto-fill CBP Form 7551,
    and capture screenshots of the results
    """
    print("=== Testing Direct Form Filling with Generated Documents ===")
    
    # Create screenshots directory if it doesn't exist
    os.makedirs('screenshots', exist_ok=True)
    
    # Run the comprehensive test function with screenshot capability
    results = run_comprehensive_test(num_entries=3, fill_form=True, take_screenshot=True)
    
    if results:
        print("\nTest completed successfully!")
        
        # Display generated files
        print("\nGenerated files:")
        for key, path in results.items():
            if isinstance(path, str) and os.path.exists(path):
                print(f"  - {key}: {path}")
        
        # Create an HTML report with screenshots
        html_report = create_html_report(results)
        
        # Open the HTML report in the default browser
        if html_report:
            print(f"\nOpening HTML report: {html_report}")
            webbrowser.open(f'file://{os.path.abspath(html_report)}')
        
        return True
    else:
        print("\nTest did not complete successfully.")
        return False

def create_html_report(results):
    """
    Create an HTML report with screenshots and analysis
    
    Args:
        results: Dictionary with paths to generated files
        
    Returns:
        str: Path to the HTML report
    """
    try:
        report_path = "screenshots/form_filling_report.html"
        
        # Add current date to results if not present
        if 'date' not in results:
            import datetime
            results['date'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(report_path, "w") as f:
            f.write("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>CBP Form 7551 Auto-Fill Test Report</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    h1, h2, h3 { color: #333; }
                    .screenshot { margin: 20px 0; border: 1px solid #ddd; max-width: 100%; }
                    .analysis { background-color: #f9f9f9; padding: 15px; border-radius: 5px; }
                    .section { margin-bottom: 40px; }
                    table { border-collapse: collapse; width: 100%; }
                    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                    th { background-color: #f2f2f2; }
                    tr:nth-child(even) { background-color: #f9f9f9; }
                </style>
            </head>
            <body>
                <h1>CBP Form 7551 Auto-Fill Test Report</h1>
                <p><em>Generated on: """ + results.get('date', 'Unknown date') + """</em></p>
                
                <div class="section">
                    <h2>PDF Form Filling Results</h2>
            """)
            
            # Add form filling results
            if 'filled_form' in results and os.path.exists(results['filled_form']):
                f.write(f"""
                <p><strong>Form path:</strong> {results['filled_form']}</p>
                <p>The form has been filled with data from test documents and can be viewed in a PDF reader.</p>
                """)
                
                # Add screenshot if available
                if 'screenshot' in results and os.path.exists(results['screenshot']):
                    f.write(f"""
                    <h3>Form Screenshot:</h3>
                    <img class="screenshot" src="../{results['screenshot']}" alt="Filled Form">
                    """)
                
                # Add analysis if available
                if 'analysis' in results and os.path.exists(results['analysis']):
                    f.write(f"""
                    <h3>Field Analysis:</h3>
                    <img class="screenshot" src="../{results['analysis']}" alt="Form Analysis">
                    """)
                    
                    # Add text analysis if available
                    analysis_txt = results['analysis'].replace('.png', '.txt')
                    if os.path.exists(analysis_txt):
                        with open(analysis_txt, 'r') as txt_file:
                            f.write(f"""
                            <div class="analysis">
                                <pre>{txt_file.read()}</pre>
                            </div>
                            """)
            else:
                f.write("<p>No filled form was generated or the file could not be found.</p>")
            
            # Add input data information
            f.write("""
                </div>
                
                <div class="section">
                    <h2>Test Input Data</h2>
            """)
            
            if 'package' in results:
                package = results['package']
                
                # Import entries information
                if 'import_entries' in package and package['import_entries']:
                    f.write("""
                    <h3>Import Entries</h3>
                    <table>
                        <tr>
                            <th>Entry Number</th>
                            <th>Date</th>
                            <th>Value</th>
                            <th>Duty</th>
                        </tr>
                    """)
                    
                    for entry in package['import_entries']:
                        entry_num = entry.get('entry_number', 'N/A')
                        date = entry.get('import_date', 'N/A')
                        
                        # Calculate value and duty from line items if not provided directly
                        value = entry.get('total_value', 0)
                        duty = entry.get('total_duty', 0)
                        
                        if not value and 'line_items' in entry:
                            value = sum(item.get('value', 0) for item in entry['line_items'])
                        
                        if not duty and 'line_items' in entry:
                            duty = sum(item.get('duty_amount', 0) for item in entry['line_items'])
                        
                        f.write(f"""
                        <tr>
                            <td>{entry_num}</td>
                            <td>{date}</td>
                            <td>${value:,.2f}</td>
                            <td>${duty:,.2f}</td>
                        </tr>
                        """)
                    
                    f.write("</table>")
                
                # Export documents information
                if 'export_docs' in package and package['export_docs']:
                    f.write("""
                    <h3>Export Documents</h3>
                    <table>
                        <tr>
                            <th>Reference</th>
                            <th>Date</th>
                            <th>Destination</th>
                            <th>Value</th>
                        </tr>
                    """)
                    
                    for doc in package['export_docs']:
                        ref = doc.get('export_ref', 'N/A')
                        date = doc.get('export_date', 'N/A')
                        dest = doc.get('destination', 'N/A')
                        
                        # Calculate value from items if not provided directly
                        value = doc.get('total_value', 0)
                        if not value and 'items' in doc:
                            value = sum(item.get('value', 0) for item in doc['items'])
                        
                        f.write(f"""
                        <tr>
                            <td>{ref}</td>
                            <td>{date}</td>
                            <td>{dest}</td>
                            <td>${value:,.2f}</td>
                        </tr>
                        """)
                    
                    f.write("</table>")
            
            f.write("""
                </div>
                
                <div class="section">
                    <h2>Next Steps</h2>
                    <ol>
                        <li>Review the screenshots and field analysis to identify missing or incorrect fields</li>
                        <li>Update the form filling functions in pdf_generator.py to address any issues</li>
                        <li>Run this test again to verify improvements</li>
                    </ol>
                </div>
            </body>
            </html>
            """)
        
        print(f"HTML report created: {report_path}")
        return report_path
    
    except Exception as e:
        print(f"Error creating HTML report: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    success = test_direct_form_filling()
    sys.exit(0 if success else 1) 