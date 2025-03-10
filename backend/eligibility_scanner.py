import pandas as pd
from datetime import datetime, timedelta

class EligibilityScanner:
    def __init__(self):
        self.eligible_items = []
        self.ineligible_items = []
        self.total_potential_refund = 0
    
    def scan_imports_exports(self, import_data, export_data):
        """
        Scan import and export data to determine drawback eligibility.
        Returns eligible items and potential refund amount.
        """
        # Parse data
        imports_df = pd.read_csv(import_data) if isinstance(import_data, str) else import_data
        exports_df = pd.read_csv(export_data) if isinstance(export_data, str) else export_data
        
        # Reset results
        self.eligible_items = []
        self.ineligible_items = []
        self.total_potential_refund = 0
        
        # Process each export item
        for _, export_row in exports_df.iterrows():
            # Find matching imports (simplified - in real app, would match by product codes)
            matching_imports = self._find_matching_imports(export_row, imports_df)
            
            if matching_imports.empty:
                self.ineligible_items.append({
                    'export_item': export_row.to_dict(),
                    'reason': 'No matching import found'
                })
                continue
            
            # Check time constraints (3-year window)
            for _, import_row in matching_imports.iterrows():
                import_date = pd.to_datetime(import_row['import_date'])
                export_date = pd.to_datetime(export_row['export_date'])
                
                # Check if export is within 3 years of import
                if export_date <= import_date + timedelta(days=3*365):
                    # Calculate potential refund (99% of duty paid)
                    duty_paid = float(import_row.get('duty_amount', 0))
                    refund_amount = duty_paid * 0.99
                    
                    self.eligible_items.append({
                        'import_item': import_row.to_dict(),
                        'export_item': export_row.to_dict(),
                        'refund_amount': refund_amount
                    })
                    
                    self.total_potential_refund += refund_amount
                else:
                    self.ineligible_items.append({
                        'export_item': export_row.to_dict(),
                        'import_item': import_row.to_dict(),
                        'reason': 'Export occurred more than 3 years after import'
                    })
        
        return {
            'eligible_items': self.eligible_items,
            'ineligible_items': self.ineligible_items,
            'total_potential_refund': self.total_potential_refund
        }
    
    def _find_matching_imports(self, export_row, imports_df):
        """Find imports that match this export (simplified matching logic)"""
        # In a real application, you would have more sophisticated matching
        # based on product codes, descriptions, etc.
        return imports_df[imports_df['product_code'] == export_row['product_code']]
    
    def generate_summary_report(self):
        """Generate a summary report of eligibility findings"""
        return {
            'eligible_count': len(self.eligible_items),
            'ineligible_count': len(self.ineligible_items),
            'total_potential_refund': self.total_potential_refund,
            'eligible_items': self.eligible_items[:5],  # Preview of first 5
            'common_ineligibility_reasons': self._analyze_ineligibility_reasons()
        }
    
    def _analyze_ineligibility_reasons(self):
        """Analyze common reasons for ineligibility"""
        reasons = {}
        for item in self.ineligible_items:
            reason = item['reason']
            reasons[reason] = reasons.get(reason, 0) + 1
        
        return reasons 