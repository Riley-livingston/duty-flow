# DutyFlow

DutyFlow is an import duty analysis tool designed to help small and medium-sized international trade businesses analyze their import transactions and identify potential duty drawback opportunities.

## Features

- CSV upload for import and export transactions
- Import-only or Import-Export matching analysis
- Eligibility determination based on import date
- Export matching for more accurate refund estimates
- Estimated refund calculation (99% of eligible duty paid)
- Summary reports with key metrics
- Detailed transaction tables
- CSV export of analysis results
- PDF report generation
- Clean, responsive user interface

## Getting Started

### Prerequisites

- Python 3.7+
- Node.js 14+
- npm or yarn

### Installation

1. Clone the repository
2. Set up the backend:
   ```
   cd duty-flow
   python -m venv dutyflow-env
   source dutyflow-env/bin/activate  # On Windows: dutyflow-env\Scripts\activate
   pip install -r requirements.txt
   ```
3. Set up the frontend:
   ```
   cd frontend
   npm install
   ```

### Running the Application

1. Start the backend server:
   ```
   python app.py
   ```
2. Start the frontend development server:
   ```
   cd frontend
   npm start
   ```
3. Open your browser and navigate to `http://localhost:3000`

## CSV File Format

### Import CSV

Your import CSV file should include the following columns:
- `entry_number`: The customs entry number
- `product_id`: Product identifier
- `import_date`: Date of import (YYYY-MM-DD)
- `quantity`: Quantity imported
- `duty_paid`: Amount of duty paid

### Export CSV

Your export CSV file should include the following columns:
- `export_reference`: Export reference number
- `product_id`: Product identifier (should match import product_id for matching)
- `export_date`: Date of export (YYYY-MM-DD)
- `quantity`: Quantity exported
- `destination`: Export destination country/region

## For Small and Medium-Sized Businesses

DutyFlow is specifically designed with small and medium-sized businesses in mind:

- Simplified interface for non-specialists
- Clear eligibility indicators
- Estimated refund calculations
- PDF reports suitable for sharing with customs brokers
- Guidance on next steps for claiming duty drawbacks 