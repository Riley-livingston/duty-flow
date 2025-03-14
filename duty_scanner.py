import pandas as pd
import datetime
import os

def scan_transactions(import_file, export_file=None):
    """
    Scan import transactions to identify potential refund opportunities.
    For the initial version, we'll just analyze the import data.
    
    Parameters:
    - import_file: CSV file containing import transactions
    - export_file: Not used in this simplified version
    
    Returns:
    - DataFrame with import transactions
    """
    # Load import data
    imports_df = pd.read_csv(import_file)
    
    # Basic validation
    required_columns = ['entry_number', 'product_id', 'import_date', 'quantity', 'duty_paid']
    for col in required_columns:
        if col not in imports_df.columns:
            raise ValueError(f"Missing required column: {col}")
    
    # More robust date parsing for import_date - try different formats
    try:
        # Try the standard format first
        imports_df['import_date'] = pd.to_datetime(imports_df['import_date'])
    except:
        # If that fails, try common alternative formats
        try:
            # Try MM/DD/YYYY format
            imports_df['import_date'] = pd.to_datetime(imports_df['import_date'], format='%m/%d/%Y')
        except:
            try:
                # Try DD/MM/YYYY format
                imports_df['import_date'] = pd.to_datetime(imports_df['import_date'], format='%d/%m/%Y')
            except Exception as e:
                # If all parsing attempts fail, raise a helpful error
                raise ValueError(f"Failed to parse import_date. Please ensure dates are in YYYY-MM-DD, MM/DD/YYYY, or DD/MM/YYYY format. Error: {str(e)}")
    
    # Calculate eligibility based on import date
    # For duty drawback, imports are typically eligible if they occurred within the last 5 years
    today = pd.Timestamp.now()
    five_years_ago = today - pd.DateOffset(years=5)
    imports_df['is_eligible'] = imports_df['import_date'] >= five_years_ago
    
    # Calculate potential refund (99% of duty paid if eligible, 0 if not)
    imports_df['potential_refund'] = imports_df.apply(
        lambda row: round(row['duty_paid'] * 0.99, 2) if row['is_eligible'] else 0, 
        axis=1
    )
    
    return imports_df

def scan_transactions_with_exports(import_file, export_file):
    """
    Scan import and export transactions to identify potential refund opportunities.
    
    Parameters:
    - import_file: CSV file containing import transactions
    - export_file: CSV file containing export transactions
    
    Returns:
    - Tuple of (imports_df, exports_df) with analysis results
    """
    # Load import data
    imports_df = scan_transactions(import_file)
    
    # Load export data
    exports_df = pd.read_csv(export_file)
    
    # Basic validation for export data
    required_columns = ['export_reference', 'product_id', 'export_date', 'quantity', 'destination']
    for col in required_columns:
        if col not in exports_df.columns:
            raise ValueError(f"Missing required column in export file: {col}")
    
    # More robust date parsing - try different formats
    try:
        # Try the standard format first
        exports_df['export_date'] = pd.to_datetime(exports_df['export_date'])
    except:
        # If that fails, try common alternative formats
        try:
            # Try MM/DD/YYYY format
            exports_df['export_date'] = pd.to_datetime(exports_df['export_date'], format='%m/%d/%Y')
        except:
            try:
                # Try DD/MM/YYYY format
                exports_df['export_date'] = pd.to_datetime(exports_df['export_date'], format='%d/%m/%Y')
            except Exception as e:
                # If all parsing attempts fail, raise a helpful error
                raise ValueError(f"Failed to parse export_date. Please ensure dates are in YYYY-MM-DD, MM/DD/YYYY, or DD/MM/YYYY format. Error: {str(e)}")
    
    # Also ensure import dates are in datetime format
    if not pd.api.types.is_datetime64_dtype(imports_df['import_date']):
        try:
            # Try to convert if not already in datetime format
            imports_df['import_date'] = pd.to_datetime(imports_df['import_date'])
        except Exception as e:
            # If parsing fails, raise a helpful error
            raise ValueError(f"Failed to parse import_date. Please ensure dates are in a standard format. Error: {str(e)}")
    
    # Print some debug info
    print(f"Import date range: {imports_df['import_date'].min()} to {imports_df['import_date'].max()}")
    print(f"Export date range: {exports_df['export_date'].min()} to {exports_df['export_date'].max()}")
    print(f"Import products: {len(imports_df['product_id'].unique())} unique")
    print(f"Export products: {len(exports_df['product_id'].unique())} unique")
    print(f"Product overlap: {len(set(imports_df['product_id']).intersection(set(exports_df['product_id'])))} products")
    
    # Initialize match columns
    imports_df['has_export_match'] = False
    exports_df['matched_to_import'] = False
    
    # Match exports to imports based on product_id
    # For each eligible import, find matching exports where export_date > import_date
    for i, import_row in imports_df.iterrows():
        if import_row['is_eligible']:
            # Find matching exports by product_id where export date is after import date
            matching_exports = exports_df[
                (exports_df['product_id'] == import_row['product_id']) & 
                (exports_df['export_date'] > import_row['import_date'])
            ]
            
            if len(matching_exports) > 0:
                # Mark this import as having a match
                imports_df.at[i, 'has_export_match'] = True
                
                # Mark the matching exports
                for j in matching_exports.index:
                    exports_df.at[j, 'matched_to_import'] = True
    
    # For SMBs, we'll only allow refunds for imports that have matching exports
    # This is a simplified version of the actual rules
    imports_df['potential_refund'] = imports_df.apply(
        lambda row: round(row['duty_paid'] * 0.99, 2) if row['is_eligible'] and row['has_export_match'] else 0, 
        axis=1
    )
    
    return imports_df, exports_df

def generate_summary_report(transactions):
    """
    Generate a summary report of the import analysis.
    
    Parameters:
    - transactions: DataFrame with import transactions
    
    Returns:
    - String with summary report
    """
    total_transactions = len(transactions)
    eligible_count = transactions['is_eligible'].sum()
    total_duty = transactions['duty_paid'].sum()
    potential_refund = transactions['potential_refund'].sum()
    
    summary = f"Import Analysis Summary\n"
    summary += f"======================\n\n"
    summary += f"Total Transactions: {total_transactions}\n"
    summary += f"Eligible Transactions: {eligible_count} ({eligible_count/total_transactions*100:.1f}%)\n"
    summary += f"Total Duty Paid: ${total_duty:,.2f}\n"
    summary += f"Potential Refund: ${potential_refund:,.2f} ({potential_refund/total_duty*100:.1f}% of total duty)\n\n"
    
    # Add entry-level summary
    entry_summary = transactions.groupby('entry_number').agg({
        'duty_paid': 'sum',
        'potential_refund': 'sum',
        'is_eligible': 'any'
    }).reset_index()
    
    summary += "Duty and Potential Refund by Entry Number:\n"
    for _, row in entry_summary.iterrows():
        eligibility = "Eligible" if row['is_eligible'] else "Not Eligible"
        summary += f"Entry #{row['entry_number']}: Duty ${row['duty_paid']:,.2f}, "
        summary += f"Potential Refund ${row['potential_refund']:,.2f} ({eligibility})\n"
    
    return summary

def generate_summary_report_with_exports(transactions, export_transactions):
    """
    Generate a summary report of the import-export analysis.
    
    Parameters:
    - transactions: DataFrame with import transactions
    - export_transactions: DataFrame with export transactions
    
    Returns:
    - String with summary report
    """
    total_transactions = len(transactions)
    eligible_count = transactions['is_eligible'].sum()
    matched_count = transactions['has_export_match'].sum()
    total_duty = transactions['duty_paid'].sum()
    potential_refund = transactions['potential_refund'].sum()
    
    total_exports = len(export_transactions)
    matched_exports = export_transactions['matched_to_import'].sum()
    
    summary = f"Import-Export Analysis Summary\n"
    summary += f"=============================\n\n"
    summary += f"Total Import Transactions: {total_transactions}\n"
    summary += f"Eligible Import Transactions: {eligible_count} ({eligible_count/total_transactions*100:.1f}%)\n"
    summary += f"Imports with Export Matches: {matched_count} ({matched_count/total_transactions*100:.1f}%)\n"
    summary += f"Total Duty Paid: ${total_duty:,.2f}\n"
    summary += f"Potential Refund: ${potential_refund:,.2f} ({potential_refund/total_duty*100:.1f}% of total duty)\n\n"
    
    summary += f"Total Export Transactions: {total_exports}\n"
    summary += f"Exports Matched to Imports: {matched_exports} ({matched_exports/total_exports*100:.1f}%)\n\n"
    
    # Add entry-level summary
    entry_summary = transactions.groupby('entry_number').agg({
        'duty_paid': 'sum',
        'potential_refund': 'sum',
        'is_eligible': 'any',
        'has_export_match': 'any'
    }).reset_index()
    
    summary += "Duty and Potential Refund by Entry Number:\n"
    for _, row in entry_summary.iterrows():
        eligibility = "Eligible" if row['is_eligible'] else "Not Eligible"
        export_match = "With Export Match" if row['has_export_match'] else "No Export Match"
        summary += f"Entry #{row['entry_number']}: Duty ${row['duty_paid']:,.2f}, "
        summary += f"Potential Refund ${row['potential_refund']:,.2f} ({eligibility}, {export_match})\n"
    
    return summary

def save_results(transactions, output_file):
    """
    Save analysis results to a CSV file.
    
    Parameters:
    - transactions: DataFrame with import transactions
    - output_file: Path to save the CSV file
    
    Returns:
    - Path to the saved file
    """
    # Convert datetime columns to string for CSV export
    transactions_copy = transactions.copy()
    if 'import_date' in transactions_copy.columns:
        transactions_copy['import_date'] = transactions_copy['import_date'].dt.strftime('%Y-%m-%d')
    
    # Save to CSV
    transactions_copy.to_csv(output_file, index=False)
    return output_file

if __name__ == "__main__":
    # Example usage
    import_file = "sample_imports.csv"
    
    if os.path.exists(import_file):
        try:
            transactions = scan_transactions(import_file)
            print(generate_summary_report(transactions))
            output_file = save_results(transactions)
            print(f"Results saved to {output_file}")
        except Exception as e:
            print(f"Error processing files: {e}")
    else:
        print(f"Import file {import_file} not found.") 