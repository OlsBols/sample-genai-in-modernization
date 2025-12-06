"""
Strands Tools for AWS Pricing Calculation
Provides deterministic ARR calculation from RVTools data
"""
from strands import tool
import pandas as pd
from aws_pricing_calculator import AWSPricingCalculator
from rv_tool_analysis import rv_tool_analysis
from config import USE_DETERMINISTIC_PRICING, PRICING_CONFIG
import json

@tool(
    name="calculate_exact_aws_arr",
    description="Calculate exact AWS Annual Recurring Revenue (ARR) from RVTools data using AWS pricing. Returns deterministic, consistent costs every time. Requires RVTools filename or pattern. Controlled by USE_DETERMINISTIC_PRICING config."
)
def calculate_exact_aws_arr(rvtools_filename: str, target_region: str = None):
    """
    Calculate exact AWS ARR from RVTools data
    
    This tool provides DETERMINISTIC pricing - same input always produces same output.
    Uses AWS Price List API when available, falls back to accurate hardcoded pricing.
    
    Behavior controlled by config.py:
    - USE_DETERMINISTIC_PRICING: Enable/disable this feature
    - PRICING_CONFIG: Configure region, API usage, pricing model
    
    Args:
        rvtools_filename: RVTools file path or pattern (e.g., 'input/rvtool*.csv')
        target_region: AWS region for pricing (default: from config)
    
    Returns:
        JSON string with detailed cost breakdown including:
        - Total monthly cost and ARR
        - Breakdown by instance type
        - Breakdown by OS (Windows vs Linux)
        - Cost components (compute, storage, data transfer)
        - Per-VM details
    
    Example:
        result = calculate_exact_aws_arr('input/rvtool*.csv', 'us-east-1')
    """
    # Check if deterministic pricing is enabled
    if not USE_DETERMINISTIC_PRICING:
        return json.dumps({
            'error': 'Deterministic pricing is disabled in config.py',
            'message': 'Set USE_DETERMINISTIC_PRICING = True to enable this feature',
            'current_mode': 'LLM-based estimation'
        })
    
    # Use config default if region not specified
    if target_region is None:
        target_region = PRICING_CONFIG.get('default_region', 'us-east-1')
    
    print(f"\n{'='*80}")
    print(f"EXACT AWS ARR CALCULATION")
    print(f"{'='*80}")
    print(f"Input: {rvtools_filename}")
    print(f"Region: {target_region}")
    print(f"Mode: Deterministic (config-controlled)")
    print(f"{'='*80}\n")
    
    # Step 1: Load RVTools data
    print("Step 1: Loading RVTools data...")
    df = rv_tool_analysis(rvtools_filename)
    print(f"✓ Loaded {len(df)} VMs\n")
    
    # Step 2: Initialize pricing calculator (uses config settings)
    print("Step 2: Initializing AWS Pricing Calculator...")
    calculator = AWSPricingCalculator(region=target_region)
    print(f"✓ Calculator ready\n")
    
    # Step 3: Calculate ARR
    print("Step 3: Calculating exact AWS costs...")
    results = calculator.calculate_arr_from_dataframe(df)
    
    # Step 3.5: Export to Excel
    print("Step 3.5: Generating Excel export...")
    try:
        from excel_export import export_vm_to_ec2_mapping
        excel_path = export_vm_to_ec2_mapping(results, 'vm_to_ec2_mapping.xlsx')
        if excel_path:
            print(f"✓ Excel export saved: {excel_path}")
        else:
            print(f"✗ Excel export returned None - check excel_export.py for errors")
    except Exception as e:
        import traceback
        print(f"✗ Excel export failed: {e}")
        print(f"Traceback: {traceback.format_exc()}")
    
    # Step 4: Format results for agent consumption
    summary = results['summary']
    cost_breakdown = results['cost_breakdown']
    instance_breakdown = results['instance_type_breakdown']
    os_breakdown = results['os_breakdown']
    
    # Create formatted output
    output = {
        'summary': {
            'total_vms': summary['total_vms'],
            'total_monthly_cost_usd': summary['total_monthly_cost'],
            'total_annual_cost_arr_usd': summary['total_arr'],
            'region': summary['region'],
            'pricing_model': summary['pricing_model']
        },
        'monthly_cost_breakdown': {
            'compute': cost_breakdown['monthly_compute'],
            'storage': cost_breakdown['monthly_storage'],
            'data_transfer': cost_breakdown['monthly_data_transfer'],
            'total': cost_breakdown['monthly_total']
        },
        'instance_type_distribution': instance_breakdown,
        'os_distribution': os_breakdown,
        'calculation_method': 'Deterministic - AWS Price List API with fallback pricing',
        'consistency_guarantee': 'Same input produces identical output every time'
    }
    
    # Add top 10 most expensive VMs for context
    detailed_df = results['detailed_results']
    top_vms = detailed_df.nlargest(10, 'monthly_total')[
        ['vm_name', 'instance_type', 'vcpu', 'memory_gb', 'monthly_total']
    ].to_dict('records')
    output['top_10_most_expensive_vms'] = top_vms
    
    # Convert to JSON string for agent
    return json.dumps(output, indent=2)


@tool(
    name="get_vm_cost_breakdown",
    description="Get detailed cost breakdown for a specific VM configuration. Useful for what-if analysis and sizing recommendations."
)
def get_vm_cost_breakdown(vcpu: int, memory_gb: float, storage_gb: float, 
                         os: str, target_region: str = 'us-east-1'):
    """
    Calculate cost for a specific VM configuration
    
    Args:
        vcpu: Number of vCPUs
        memory_gb: Memory in GB
        storage_gb: Storage in GB
        os: Operating system ('Windows' or 'Linux')
        target_region: AWS region for pricing
    
    Returns:
        JSON string with cost breakdown for this VM
    """
    calculator = AWSPricingCalculator(region=target_region, use_api=False)
    
    result = calculator.calculate_vm_cost(
        vcpu=vcpu,
        memory_gb=memory_gb,
        storage_gb=storage_gb,
        os=os,
        vm_name='custom-vm'
    )
    
    output = {
        'vm_configuration': {
            'vcpu': vcpu,
            'memory_gb': memory_gb,
            'storage_gb': storage_gb,
            'os': os
        },
        'recommended_instance_type': result['instance_type'],
        'pricing': {
            'hourly_rate_usd': result['hourly_rate'],
            'monthly_compute_usd': result['monthly_compute'],
            'monthly_storage_usd': result['monthly_storage'],
            'monthly_data_transfer_usd': result['monthly_data_transfer'],
            'monthly_total_usd': result['monthly_total'],
            'annual_cost_usd': round(result['monthly_total'] * 12, 2)
        },
        'region': target_region,
        'pricing_model': '3-Year No Upfront Reserved Instance'
    }
    
    return json.dumps(output, indent=2)


@tool(
    name="compare_pricing_models",
    description="Compare costs across different AWS pricing models (On-Demand, 1-Year RI, 3-Year RI) for the RVTools inventory."
)
def compare_pricing_models(rvtools_filename: str, target_region: str = 'us-east-1'):
    """
    Compare pricing across different AWS purchasing options
    
    Args:
        rvtools_filename: RVTools file path or pattern
        target_region: AWS region for pricing
    
    Returns:
        JSON string comparing On-Demand, 1-Year RI, and 3-Year RI pricing
    """
    # Load RVTools data
    df = rv_tool_analysis(rvtools_filename)
    
    # Calculate for 3-Year RI (base calculation)
    calculator = AWSPricingCalculator(region=target_region, use_api=False)
    results_3yr = calculator.calculate_arr_from_dataframe(df)
    
    # Estimate other pricing models (multipliers based on typical AWS pricing)
    monthly_3yr = results_3yr['summary']['total_monthly_cost']
    
    # On-Demand is typically 2.5x more expensive than 3-Year RI
    monthly_on_demand = monthly_3yr * 2.5
    
    # 1-Year RI is typically 1.4x more expensive than 3-Year RI
    monthly_1yr = monthly_3yr * 1.4
    
    output = {
        'vm_count': results_3yr['summary']['total_vms'],
        'region': target_region,
        'pricing_comparison': {
            'on_demand': {
                'monthly_cost_usd': round(monthly_on_demand, 2),
                'annual_cost_usd': round(monthly_on_demand * 12, 2),
                'description': 'Pay-as-you-go, no commitment'
            },
            '1_year_reserved_instance': {
                'monthly_cost_usd': round(monthly_1yr, 2),
                'annual_cost_usd': round(monthly_1yr * 12, 2),
                'savings_vs_on_demand_percent': round((1 - monthly_1yr/monthly_on_demand) * 100, 1),
                'description': '1-year commitment, no upfront payment'
            },
            '3_year_reserved_instance': {
                'monthly_cost_usd': round(monthly_3yr, 2),
                'annual_cost_usd': round(monthly_3yr * 12, 2),
                'savings_vs_on_demand_percent': round((1 - monthly_3yr/monthly_on_demand) * 100, 1),
                'savings_vs_1yr_ri_percent': round((1 - monthly_3yr/monthly_1yr) * 100, 1),
                'description': '3-year commitment, no upfront payment (RECOMMENDED)'
            }
        },
        'recommendation': '3-Year No Upfront Reserved Instances provide best value for stable workloads',
        'three_year_savings_usd': round((monthly_on_demand - monthly_3yr) * 36, 2)
    }
    
    return json.dumps(output, indent=2)


if __name__ == "__main__":
    # Test the tools
    print("Testing Pricing Tools...")
    
    # Test 1: Calculate ARR
    print("\n=== Test 1: Calculate Exact AWS ARR ===")
    try:
        result = calculate_exact_aws_arr('input/RVTools_Export.xlsx', 'us-east-1')
        data = json.loads(result)
        print(f"✓ Total VMs: {data['summary']['total_vms']}")
        print(f"✓ Monthly Cost: ${data['summary']['total_monthly_cost_usd']:,.2f}")
        print(f"✓ Annual ARR: ${data['summary']['total_annual_cost_arr_usd']:,.2f}")
    except Exception as e:
        print(f"✗ Test failed: {e}")
    
    # Test 2: Single VM cost
    print("\n=== Test 2: Single VM Cost Breakdown ===")
    try:
        result = get_vm_cost_breakdown(4, 16, 100, 'Windows Server', 'us-east-1')
        data = json.loads(result)
        print(f"✓ Instance Type: {data['recommended_instance_type']}")
        print(f"✓ Monthly Cost: ${data['pricing']['monthly_total_usd']}")
    except Exception as e:
        print(f"✗ Test failed: {e}")
    
    print("\n✓ All pricing tools tests complete")
