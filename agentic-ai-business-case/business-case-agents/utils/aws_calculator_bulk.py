#!/usr/bin/env python3
"""AWS Calculator Bulk Import Excel Generator"""

import pandas as pd
import json
from pathlib import Path

def generate_bulk_import_excel(infrastructure_data, template_path="/Users/arptsha/Downloads/Amazon_EC2_Instances_BulkUpload_Template_Commercial.xlsx", output_file="aws_calculator_bulk_import.xlsx"):
    """Generate AWS Calculator bulk import Excel using official template format"""
    
    try:
        # Read the official template's Inputs sheet
        template_df = pd.read_excel(template_path, sheet_name='Inputs', header=1)  # Header at row 1
        print(f"✅ Loaded AWS template Inputs sheet")
        
        # Clear existing data but keep headers (keep first 2 rows - headers)
        header_rows = template_df.iloc[:1].copy()
        
        bulk_import_rows = []
        
        # Process RVTools data if available
        if 'rvtool_csv' in infrastructure_data:
            df = infrastructure_data['rvtool_csv']
            
            # Group servers by CPU/Memory to determine instance types
            server_groups = df.groupby(['CPU Cores', 'Memory (MB)']).size().reset_index(name='count')
            
            group_id = 1
            for _, group in server_groups.iterrows():
                cpu_cores = group['CPU Cores']
                memory_mb = group['Memory (MB)']
                count = group['count']
                
                # Map to appropriate EC2 instance type
                instance_type = map_to_ec2_instance(cpu_cores, memory_mb)
                
                # Create row matching AWS template format with correct values
                row_data = [None] * len(template_df.columns)
                row_data[0] = group_id  # Group
                row_data[1] = f'{cpu_cores} vCPU, {memory_mb/1024:.0f}GB RAM servers'  # Description
                row_data[2] = 'US East (N. Virginia)'  # AWS Region (correct format)
                row_data[3] = 'Linux/UNIX'  # Operating System (correct format)
                row_data[4] = instance_type  # Instance Type
                row_data[5] = 'Shared'  # Tenancy (correct option)
                row_data[6] = count  # Number of Instances
                row_data[7] = 100  # Assumed Usage (percentage)
                row_data[8] = 'Always On'  # Usage Type
                row_data[9] = 'On Demand'  # Purchasing Option (correct format)
                
                bulk_import_rows.append(row_data)
                group_id += 1
        
        # Create DataFrame with proper structure
        if bulk_import_rows:
            # Convert to DataFrame with same columns as template
            df_new_data = pd.DataFrame(bulk_import_rows, columns=template_df.columns)
            
            # Combine header + new data
            final_df = pd.concat([header_rows, df_new_data], ignore_index=True)
            
            # Write to Excel with same sheet structure as template
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                final_df.to_excel(writer, sheet_name='Inputs', index=False, header=False)
            
            print(f"✅ Generated AWS Calculator Excel: {output_file}")
            return output_file, df_new_data
        else:
            print("❌ No infrastructure data found to process")
            return None, None
            
    except Exception as e:
        print(f"❌ Error processing template: {e}")
        return None, None

def generate_basic_excel(infrastructure_data, output_file):
    """Fallback method to create basic Excel without template"""
    
    bulk_import_rows = []
    
    # Add sample data based on infrastructure
    if 'rvtool_csv' in infrastructure_data:
        df = infrastructure_data['rvtool_csv']
        total_servers = len(df)
        
        # Add sample data based on infrastructure with correct AWS Calculator values
        bulk_import_rows.append({
            'Service': 'Amazon EC2',
            'Region': 'US East (N. Virginia)',
            'Operating System': 'Linux/UNIX',
            'Instance Type': 'm5.xlarge',
            'Tenancy': 'Shared',
            'Quantity': total_servers,
            'Usage Hours': 8760,
            'Purchasing Option': 'On Demand',
            'Description': f'{total_servers} servers from RVTools'
        })
        
        # Add storage with correct values
        if 'Provisioned Storage (GB)' in df.columns:
            total_storage = df['Provisioned Storage (GB)'].sum()
            bulk_import_rows.append({
                'Service': 'Amazon EBS',
                'Region': 'US East (N. Virginia)',
                'Storage Type': 'General Purpose SSD (gp2)',  # Use gp2 instead of gp3
                'Size (GB)': total_storage,
                'Description': 'Migrated storage'
            })
    
    # Create DataFrame and save
    df_bulk = pd.DataFrame(bulk_import_rows)
    df_bulk.to_excel(output_file, index=False)
    
    return output_file, df_bulk

def map_to_ec2_instance(cpu_cores, memory_mb):
    """Map CPU/Memory to appropriate EC2 instance type"""
    memory_gb = memory_mb / 1024
    
    # Simple mapping logic
    if cpu_cores <= 2 and memory_gb <= 8:
        return 'm5.large'
    elif cpu_cores <= 4 and memory_gb <= 16:
        return 'm5.xlarge'
    elif cpu_cores <= 8 and memory_gb <= 32:
        return 'm5.2xlarge'
    elif cpu_cores <= 16 and memory_gb <= 64:
        return 'm5.4xlarge'
    elif cpu_cores <= 32 and memory_gb <= 128:
        return 'm5.8xlarge'
    else:
        return 'm5.12xlarge'

def get_bulk_import_instructions():
    """Get instructions for using the bulk import Excel"""
    return """
AWS Calculator Bulk Import Instructions:

1. The Excel file has been generated with your infrastructure data
2. Go to AWS Calculator Bulk Import: https://calculator.aws/#/bulk-import
3. Upload the generated Excel file
4. Review and adjust the imported services as needed
5. Generate your estimate and create a shareable link
6. Share the estimate link (format: https://calculator.aws/#/estimate?id=xxxxx)

The bulk import feature allows you to quickly populate the calculator with all your infrastructure requirements and generate accurate ARR estimates with shareable links.
"""

if __name__ == "__main__":
    # Test with sample data
    sample_data = {
        'rvtool_csv': pd.DataFrame({
            'CPU Cores': [4, 8, 2, 4],
            'Memory (MB)': [16384, 32768, 8192, 16384],
            'Provisioned Storage (GB)': [100, 200, 50, 150]
        })
    }
    
    excel_file, df = generate_bulk_import_excel(sample_data)
    if excel_file:
        print(f"✅ Generated: {excel_file}")
        print(df)
        print(get_bulk_import_instructions())
    else:
        print("❌ Failed to generate Excel file")
