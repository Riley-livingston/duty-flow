import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

# Create directories if they don't exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("templates", exist_ok=True)

def generate_sample_imports(num_records=50, small_business=True, output_file="uploads/sample_imports.csv"):
    """
    Generate sample import data tailored for small and medium-sized businesses.
    
    Parameters:
    - num_records: Number of import records to generate
    - small_business: If True, generates data typical for small businesses
    - output_file: Path to save the CSV file
    
    Returns:
    - Path to the generated CSV file
    """
    np.random.seed(42)  # For reproducibility
    
    # Generate random data
    if small_business:
        # Smaller number of unique entries for SMBs
        num_entries = min(15, num_records // 3)
        entry_numbers = [f"E{i:05d}" for i in range(1, num_entries + 1)]
        # Repeat entry numbers to simulate multiple items per entry
        entry_numbers = [entry_numbers[i % num_entries] for i in range(num_records)]
        
        # Fewer product categories for SMBs
        product_categories = ['Electronics', 'Textiles', 'Home Goods', 'Office Supplies']
        product_ids = []
        for i in range(num_records):
            category = np.random.choice(product_categories)
            product_ids.append(f"{category[:3]}-{np.random.randint(1000, 9999)}")
        
        # More recent dates for SMBs (mostly within eligibility period)
        today = datetime.now()
        dates = []
        for _ in range(num_records):
            # 80% within last 5 years, 20% older
            if np.random.random() < 0.8:
                days_ago = np.random.randint(1, 365 * 5)
            else:
                days_ago = np.random.randint(365 * 5, 365 * 7)
            dates.append((today - timedelta(days=days_ago)).strftime("%Y-%m-%d"))
        
        # Smaller quantities and duty amounts for SMBs
        quantities = np.random.randint(1, 50, size=num_records)
        duty_paid = np.round(np.random.uniform(50, 2000, size=num_records), 2)
    else:
        # Larger enterprise data
        num_entries = min(30, num_records // 2)
        entry_numbers = [f"E{i:05d}" for i in range(1, num_entries + 1)]
        entry_numbers = [entry_numbers[i % num_entries] for i in range(num_records)]
        
        product_categories = ['Electronics', 'Textiles', 'Home Goods', 'Office Supplies', 
                             'Industrial Equipment', 'Chemicals', 'Automotive', 'Food Products']
        product_ids = []
        for i in range(num_records):
            category = np.random.choice(product_categories)
            product_ids.append(f"{category[:3]}-{np.random.randint(1000, 9999)}")
        
        today = datetime.now()
        dates = []
        for _ in range(num_records):
            # 60% within last 5 years, 40% older
            if np.random.random() < 0.6:
                days_ago = np.random.randint(1, 365 * 5)
            else:
                days_ago = np.random.randint(365 * 5, 365 * 10)
            dates.append((today - timedelta(days=days_ago)).strftime("%Y-%m-%d"))
        
        quantities = np.random.randint(10, 500, size=num_records)
        duty_paid = np.round(np.random.uniform(500, 10000, size=num_records), 2)
    
    # Create DataFrame
    imports_df = pd.DataFrame({
        "entry_number": entry_numbers,
        "product_id": product_ids,
        "import_date": dates,
        "quantity": quantities,
        "duty_paid": duty_paid
    })
    
    # Save to CSV
    imports_df.to_csv(output_file, index=False)
    print(f"Generated sample import data: {output_file}")
    return output_file

def generate_sample_export_data(import_file, export_ratio=0.7, output_file="uploads/sample_exports.csv"):
    """
    Generate sample export data based on import data
    
    Parameters:
    - import_file: Path to the import CSV file
    - export_ratio: Ratio of imports that should have matching exports
    - output_file: Path to save the CSV file
    
    Returns:
    - Path to the generated CSV file
    """
    imports_df = pd.read_csv(import_file)
    
    # Select a subset of imports to create matching exports
    sample_size = int(len(imports_df) * export_ratio)
    selected_imports = imports_df.sample(n=sample_size)
    
    exports = []
    
    for _, import_row in selected_imports.iterrows():
        # Export date is after import date (between 1 day and 4 years later)
        import_date = pd.to_datetime(import_row['import_date'])
        max_days = min(4*365, (datetime.now() - import_date).days)
        
        if max_days > 0:
            days_later = np.random.randint(1, max_days)
            export_date = import_date + timedelta(days=days_later)
            
            # Sometimes export full quantity, sometimes partial
            export_quantity = import_row['quantity']
            if np.random.random() > 0.5:
                export_quantity = np.random.randint(1, export_quantity)
            
            exports.append({
                'product_id': import_row['product_id'],
                'export_date': export_date.strftime('%Y-%m-%d'),
                'quantity': export_quantity,
                'destination': np.random.choice(['Canada', 'Mexico', 'EU', 'Asia', 'South America']),
                'export_reference': f"EX-{np.random.randint(10000, 99999)}"
            })
    
    # Add some random exports that don't match imports
    for _ in range(int(sample_size * 0.2)):
        exports.append({
            'product_id': f"PROD-{np.random.randint(1000, 9999)}",
            'export_date': (datetime.now() - timedelta(days=np.random.randint(1, 365*3))).strftime('%Y-%m-%d'),
            'quantity': np.random.randint(1, 100),
            'destination': np.random.choice(['Canada', 'Mexico', 'EU', 'Asia', 'South America']),
            'export_reference': f"EX-{np.random.randint(10000, 99999)}"
        })
    
    exports_df = pd.DataFrame(exports)
    exports_df.to_csv(output_file, index=False)
    print(f"Generated sample export data: {output_file}")
    return output_file

def generate_templates():
    """Generate simple template files with a few rows of example data"""
    
    # Create sample import template
    import_columns = ["entry_number", "product_id", "import_date", "quantity", "duty_paid"]
    import_sample = pd.DataFrame([
        ["E00001", "ELEC-1234", "2023-01-15", 10, 500.00],
        ["E00001", "TEXT-5678", "2023-01-15", 20, 300.00],
        ["E00002", "HOME-9012", "2022-11-20", 5, 150.00],
    ], columns=import_columns)
    
    import_template_path = "templates/import_template.csv"
    import_sample.to_csv(import_template_path, index=False)
    print(f"Created import template: {import_template_path}")
    
    # Create sample export template
    export_columns = ["export_reference", "product_id", "export_date", "quantity", "destination"]
    export_sample = pd.DataFrame([
        ["EX-12345", "ELEC-1234", "2023-03-20", 8, "Canada"],
        ["EX-67890", "TEXT-5678", "2023-02-10", 15, "Mexico"],
        ["EX-24680", "HOME-9012", "2023-01-05", 3, "EU"],
    ], columns=export_columns)
    
    export_template_path = "templates/export_template.csv"
    export_sample.to_csv(export_template_path, index=False)
    print(f"Created export template: {export_template_path}")
    
    return import_template_path, export_template_path

def main():
    """Main function to generate all sample data files"""
    print("DutyFlow Sample Data Generator")
    print("=============================\n")
    
    print("1. Generating sample data for analysis...")
    import_file = generate_sample_imports(small_business=True)
    export_file = generate_sample_export_data(import_file)
    
    print("\n2. Generating template files...")
    import_template, export_template = generate_templates()
    
    print("\nSample data generation complete!")
    print("\nFiles for upload:")
    print(f"- Import data: {import_file}")
    print(f"- Export data: {export_file}")
    
    print("\nTemplate files:")
    print(f"- Import template: {import_template}")
    print(f"- Export template: {export_template}")
    
    print("\nYou can now upload these files in the DutyFlow application.")

if __name__ == "__main__":
    main() 