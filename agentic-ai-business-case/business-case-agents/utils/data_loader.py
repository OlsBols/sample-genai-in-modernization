import os
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List

class CustomerDataLoader:
    """Loads customer-specific data with flexible file discovery"""
    
    def __init__(self, customer_data_path: str):
        self.customer_data_path = Path(customer_data_path)
        self.data_quality = {}
    
    def find_files(self, patterns: List[str], directories: List[str]) -> List[Path]:
        """Find files matching patterns in multiple possible directories"""
        found_files = []
        for dir_name in directories:
            dir_path = self.customer_data_path / dir_name
            if dir_path.exists():
                for pattern in patterns:
                    found_files.extend(dir_path.glob(f"**/{pattern}"))
        return found_files
    
    def load_infrastructure_data(self) -> Dict[str, Any]:
        """Load infrastructure data prioritizing AWS Transform assessment"""
        data = {}
        
        # PRIORITY 1: AWS Transform assessment files
        transform_patterns = ['*transform*.xlsx', '*Transform*.xlsx', '*TRANSFORM*.xlsx', 
                            '*transform*.pptx', '*Transform*.pptx', '*aws_transform*',
                            'analysis.xlsx', 'business_case.pptx', 'report.pdf']
        transform_dirs = ['AnyCustomer-Scope-and-inventory-data', 'AWS-Transform', 'transform', 'Transform']
        
        transform_files = self.find_files(transform_patterns, transform_dirs)
        for file_path in transform_files:
            try:
                if file_path.suffix.lower() == '.xlsx':
                    # Load all sheets from Transform Excel
                    excel_data = pd.read_excel(file_path, sheet_name=None)
                    data[f'aws_transform_{file_path.stem}'] = excel_data
                    print(f"✅ Loaded AWS Transform Excel: {file_path.name}")
                elif file_path.suffix.lower() == '.pptx':
                    data[f'aws_transform_{file_path.stem}'] = str(file_path)
                    print(f"✅ Found AWS Transform PPT: {file_path.name}")
                elif file_path.suffix.lower() == '.pdf':
                    data[f'aws_transform_{file_path.stem}'] = str(file_path)
                    print(f"✅ Found AWS Transform PDF: {file_path.name}")
            except Exception as e:
                print(f"❌ Error loading Transform file {file_path}: {e}")
        
        # PRIORITY 2: RVTools files (for validation/supplementary data)
        rvtools_patterns = ['*rvtool*.csv', '*RVTool*.csv', '*rvtools*.xlsx', '*RVTools*.xlsx']
        rvtools_dirs = ['AnyCustomer-Scope-and-inventory-data', 'Infra-only', 'infra-only', 'Infrastructure']
        
        rvtools_files = self.find_files(rvtools_patterns, rvtools_dirs)
        if rvtools_files:
            for file in rvtools_files:
                try:
                    if file.suffix == '.csv':
                        data['rvtool_csv'] = pd.read_csv(file)
                        self.data_quality['rvtool_csv'] = {'status': 'available', 'rows': len(data['rvtool_csv']), 'file': str(file)}
                    elif file.suffix in ['.xlsx', '.xls']:
                        data['rvtool_excel'] = pd.read_excel(file, sheet_name=None)
                        self.data_quality['rvtool_excel'] = {'status': 'available', 'sheets': len(data['rvtool_excel']), 'file': str(file)}
                except Exception as e:
                    self.data_quality[f'rvtool_{file.suffix}'] = {'status': 'error', 'error': str(e)}
        else:
            self.data_quality['rvtool'] = {'status': 'missing', 'impact': 'Cannot calculate accurate server counts and sizing'}
        
        # Find AWS Calculator files
        aws_calc_patterns = ['*aws*calc*.csv', '*AWS*Calc*.csv', '*pricing*.csv']
        aws_calc_files = self.find_files(aws_calc_patterns, rvtools_dirs)
        if aws_calc_files:
            try:
                data['aws_calculator'] = pd.read_csv(aws_calc_files[0])
                self.data_quality['aws_calculator'] = {'status': 'available', 'rows': len(data['aws_calculator']), 'file': str(aws_calc_files[0])}
            except Exception as e:
                self.data_quality['aws_calculator'] = {'status': 'error', 'error': str(e)}
        else:
            self.data_quality['aws_calculator'] = {'status': 'missing', 'impact': 'Will calculate AWS costs from public pricing'}
        
        # Find dependency files
        dep_patterns = ['*dependency*.xlsx', '*dependencies*.xlsx', '*application*.xlsx', '*database*.xlsx', '*Test-Data-Set*.xlsx']
        dep_dirs = ['AnyCustomer-Scope-and-inventory-data/infra-application-database-dependency', 'infra-application-database-dependency', 'dependencies', 'application-mapping']
        
        dep_files = self.find_files(dep_patterns, dep_dirs)
        if dep_files:
            try:
                data['dependencies'] = pd.read_excel(dep_files[0], sheet_name=None)
                self.data_quality['dependencies'] = {'status': 'available', 'sheets': len(data['dependencies']), 'file': str(dep_files[0])}
            except Exception as e:
                self.data_quality['dependencies'] = {'status': 'error', 'error': str(e)}
        else:
            self.data_quality['dependencies'] = {'status': 'missing', 'impact': 'Migration complexity may be underestimated'}
        
        # Find analytics files
        analytics_patterns = ['*analytics*.xls*', '*opensearch*.xls*', '*elasticsearch*.xls*']
        analytics_dirs = ['AnyCustomer-Scope-and-inventory-data/Analytics-data', 'Analytics-data', 'analytics', 'Analytics']
        
        analytics_files = self.find_files(analytics_patterns, analytics_dirs)
        if analytics_files:
            try:
                file_path = analytics_files[0]
                # Check if it's actually a text file
                with open(file_path, 'r') as f:
                    first_line = f.readline()
                    if 'OpenSear' in first_line or not first_line.startswith('\t'):
                        # It's a text file, read as text
                        data['analytics'] = {'text_content': file_path.read_text()}
                        self.data_quality['analytics'] = {'status': 'available', 'type': 'text', 'file': str(file_path)}
                    else:
                        # Try as Excel
                        if file_path.suffix == '.xls':
                            data['analytics'] = pd.read_excel(file_path, sheet_name=None, engine='xlrd')
                        else:
                            data['analytics'] = pd.read_excel(file_path, sheet_name=None)
                        self.data_quality['analytics'] = {'status': 'available', 'sheets': len(data['analytics']), 'file': str(file_path)}
            except Exception as e:
                self.data_quality['analytics'] = {'status': 'error', 'error': str(e)}
        else:
            self.data_quality['analytics'] = {'status': 'missing', 'impact': 'Analytics workload costs not included'}
        
        return data
    
    def load_strategy_documents(self) -> Dict[str, str]:
        """Load all strategy documents"""
        documents = {}
        strategy_dirs = ['AnyCustomer-Strategy-data', 'Strategy-data', 'strategy']
        
        for dir_name in strategy_dirs:
            strategy_path = self.customer_data_path / dir_name
            if strategy_path.exists():
                for file in strategy_path.glob("*.md"):
                    documents[file.stem] = file.read_text()
                break
        
        if documents:
            self.data_quality['strategy_docs'] = {'status': 'available', 'count': len(documents)}
        else:
            self.data_quality['strategy_docs'] = {'status': 'missing', 'impact': 'Business context limited'}
        
        return documents
    
    def load_scope_details(self) -> str:
        """Load scope document"""
        scope_patterns = ['*scope*.md', '1-scope*.md']
        scope_dirs = ['AnyCustomer-Scope-and-inventory-data', 'Scope-data']
        
        scope_files = self.find_files(scope_patterns, scope_dirs)
        if scope_files:
            content = scope_files[0].read_text()
            self.data_quality['scope'] = {'status': 'available', 'length': len(content)}
            return content
        
        self.data_quality['scope'] = {'status': 'missing', 'impact': 'Program scope unclear'}
        return ""
    
    def extract_company_profile(self) -> Dict[str, Any]:
        """Extract company profile from available data"""
        strategy_docs = self.load_strategy_documents()
        
        profile = {
            "company_name": "Customer",
            "industry": "Unknown",
            "revenue": "Unknown",
            "employees": "Unknown",
            "locations": "Unknown",
            "program_budget": "Unknown",
            "program_duration": "Unknown"
        }
        
        # Try to extract from strategy docs
        for doc_content in strategy_docs.values():
            if "$" in doc_content and "B" in doc_content:
                # Try to find revenue
                pass
        
        return profile
    
    def get_data_quality_report(self) -> Dict[str, Any]:
        """Generate data quality assessment"""
        report = {
            "overall_quality": "good" if len([v for v in self.data_quality.values() if v.get('status') == 'available']) >= 3 else "fair",
            "available_sources": [k for k, v in self.data_quality.items() if v.get('status') == 'available'],
            "missing_sources": [k for k, v in self.data_quality.items() if v.get('status') == 'missing'],
            "errors": [k for k, v in self.data_quality.items() if v.get('status') == 'error'],
            "details": self.data_quality,
            "recommendations": []
        }
        
        # Add recommendations for missing data
        for source, info in self.data_quality.items():
            if info.get('status') == 'missing' and info.get('impact'):
                report['recommendations'].append(f"Obtain {source}: {info['impact']}")
        
        return report
    
    def get_all_customer_data(self) -> Dict[str, Any]:
        """Load all customer data with quality assessment"""
        data = {
            "infrastructure": self.load_infrastructure_data(),
            "strategy": self.load_strategy_documents(),
            "scope": self.load_scope_details(),
            "profile": self.extract_company_profile(),
            "data_quality": self.get_data_quality_report()
        }
        return data
