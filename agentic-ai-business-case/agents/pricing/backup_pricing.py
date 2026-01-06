"""
AWS Backup Cost Calculator
Calculates backup costs for EC2, RDS, and EKS with intelligent storage tiering
"""
import boto3
import json
import logging
from functools import lru_cache
from typing import Dict, List, Tuple
from agents.config.config import BACKUP_CONFIG

logger = logging.getLogger(__name__)


def calculate_backup_costs(vms: List[Dict], region: str = 'us-east-1') -> Dict:
    """
    Calculate AWS Backup costs with prod/pre-prod differentiation and intelligent tiering
    
    Args:
        vms: List of VM dictionaries with:
            - storage_gb: Storage size
            - environment: 'production' or 'pre_production' (optional)
            - vm_name or name: VM name (for environment detection)
            - folder: VMware folder (optional, for RVTools)
            - cluster: VMware cluster (optional, for RVTools)
        region: AWS region
    
    Returns:
        {
            'total_monthly': 1250.00,
            'total_annual': 15000.00,
            'production': {...},
            'pre_production': {...},
            'breakdown': {...},
            'savings_vs_all_warm': 10000.00,
            'savings_percentage': 80
        }
    """
    if not BACKUP_CONFIG.get('enabled', True):
        return {
            'total_monthly': 0,
            'total_annual': 0,
            'production': _empty_environment_costs(),
            'pre_production': _empty_environment_costs()
        }
    
    # Detect environment for each VM
    prod_vms = []
    preprod_vms = []
    
    for vm in vms:
        env = detect_vm_environment(vm)
        if env == 'production':
            prod_vms.append(vm)
        else:
            preprod_vms.append(vm)
    
    logger.info(f"Backup cost calculation: {len(prod_vms)} production VMs, {len(preprod_vms)} pre-production VMs")
    
    # Calculate costs for each environment
    prod_costs = calculate_environment_backup_costs(prod_vms, 'production', region)
    preprod_costs = calculate_environment_backup_costs(preprod_vms, 'pre_production', region)
    
    # Calculate total savings
    total_storage_gb = sum(vm.get('storage_gb', 0) for vm in vms)
    warm_rate = get_backup_rate('backup_storage_per_gb_month', region)
    all_warm_cost = total_storage_gb * warm_rate
    total_cost = prod_costs['monthly_cost'] + preprod_costs['monthly_cost']
    total_savings = all_warm_cost - total_cost
    savings_pct = (total_savings / all_warm_cost * 100) if all_warm_cost > 0 else 0
    
    return {
        'total_monthly': prod_costs['monthly_cost'] + preprod_costs['monthly_cost'],
        'total_annual': prod_costs['annual_cost'] + preprod_costs['annual_cost'],
        'production': prod_costs,
        'pre_production': preprod_costs,
        'breakdown': {
            'daily_backups_gb': prod_costs.get('daily_gb', 0) + preprod_costs.get('daily_gb', 0),
            'weekly_backups_gb': prod_costs.get('weekly_gb', 0) + preprod_costs.get('weekly_gb', 0),
            'monthly_backups_gb': prod_costs.get('monthly_gb', 0) + preprod_costs.get('monthly_gb', 0)
        },
        'savings_vs_all_warm': total_savings,
        'savings_percentage': savings_pct
    }


def calculate_eks_backup_costs(eks_vms: List[Dict], region: str = 'us-east-1') -> Dict:
    """
    Calculate backup costs for EKS persistent volumes
    
    Args:
        eks_vms: List of VMs migrating to EKS
        region: AWS region
    
    Returns:
        {
            'total_workloads': 100,
            'stateful_workloads': 30,
            'total_storage_gb': 3000,
            'backup_storage_gb': 1050,
            'monthly_cost': 52.50,
            'annual_cost': 630.00,
            'tier_breakdown': {...}
        }
    """
    if not BACKUP_CONFIG.get('enabled', True) or not BACKUP_CONFIG.get('backup_eks', True):
        return {
            'total_workloads': len(eks_vms),
            'stateful_workloads': 0,
            'total_storage_gb': 0,
            'backup_storage_gb': 0,
            'monthly_cost': 0,
            'annual_cost': 0
        }
    
    # Calculate stateful workloads
    stateful_pct = BACKUP_CONFIG.get('eks_stateful_percentage', 0.30)
    stateful_count = int(len(eks_vms) * stateful_pct)
    
    # Calculate storage
    avg_storage = BACKUP_CONFIG.get('eks_avg_storage_per_workload_gb', 100)
    total_storage_gb = stateful_count * avg_storage
    
    logger.info(f"EKS backup: {stateful_count} stateful workloads out of {len(eks_vms)} total, {total_storage_gb} GB storage")
    
    # Create synthetic VMs for backup calculation
    eks_backup_vms = []
    for i in range(stateful_count):
        eks_backup_vms.append({
            'vm_name': f'EKS-PV-{i+1}',
            'storage_gb': avg_storage,
            'environment': 'production'  # EKS typically production
        })
    
    # Calculate costs (EKS uses production retention)
    costs = calculate_environment_backup_costs(eks_backup_vms, 'production', region)
    
    return {
        'total_workloads': len(eks_vms),
        'stateful_workloads': stateful_count,
        'total_storage_gb': total_storage_gb,
        'backup_storage_gb': costs.get('backup_storage_gb', 0),
        'monthly_cost': costs['monthly_cost'],
        'annual_cost': costs['annual_cost'],
        'tier_breakdown': costs.get('tier_breakdown', {})
    }


def detect_vm_environment(vm: Dict) -> str:
    """
    Detect if VM is production or pre-production
    
    Checks:
    1. Explicit 'environment' field
    2. VM name patterns
    3. Folder/cluster (if available)
    4. Default to production (safer for cost estimation)
    
    Returns:
        'production' or 'pre_production'
    """
    if not BACKUP_CONFIG.get('environment_detection', {}).get('enabled', True):
        # If detection disabled, use default percentages
        return 'production'
    
    # Check explicit environment field
    if 'environment' in vm and vm['environment']:
        env = str(vm['environment']).lower()
        preprod_patterns = BACKUP_CONFIG['environment_detection']['preprod_patterns']
        for pattern in preprod_patterns:
            if pattern in env:
                return 'pre_production'
        prod_patterns = BACKUP_CONFIG['environment_detection']['prod_patterns']
        for pattern in prod_patterns:
            if pattern in env:
                return 'production'
    
    # Check VM name
    name = ''
    if 'vm_name' in vm:
        name = str(vm['vm_name']).lower()
    elif 'name' in vm:
        name = str(vm['name']).lower()
    
    if name:
        # Check pre-prod patterns first (more specific)
        preprod_patterns = BACKUP_CONFIG['environment_detection']['preprod_patterns']
        for pattern in preprod_patterns:
            if pattern in name:
                return 'pre_production'
        
        # Check prod patterns
        prod_patterns = BACKUP_CONFIG['environment_detection']['prod_patterns']
        for pattern in prod_patterns:
            if pattern in name:
                return 'production'
    
    # Check folder/cluster (RVTools)
    if 'folder' in vm and vm['folder']:
        folder = str(vm['folder']).lower()
        preprod_patterns = BACKUP_CONFIG['environment_detection']['preprod_patterns']
        for pattern in preprod_patterns:
            if pattern in folder:
                return 'pre_production'
    
    if 'cluster' in vm and vm['cluster']:
        cluster = str(vm['cluster']).lower()
        preprod_patterns = BACKUP_CONFIG['environment_detection']['preprod_patterns']
        for pattern in preprod_patterns:
            if pattern in cluster:
                return 'pre_production'
    
    # Default to production (safer for cost estimation)
    return 'production'


def calculate_environment_backup_costs(vms: List[Dict], environment: str, region: str) -> Dict:
    """
    Calculate backup costs for specific environment with intelligent tiering
    
    Args:
        vms: List of VMs
        environment: 'production' or 'pre_production'
        region: AWS region
    
    Returns:
        {
            'vm_count': 70,
            'storage_gb': 35000,
            'backup_storage_gb': 12250,
            'monthly_cost': 875.00,
            'annual_cost': 10500.00,
            'tier_breakdown': {...},
            'retention_summary': {...}
        }
    """
    if not vms:
        return _empty_environment_costs()
    
    # Get retention policy for environment
    retention = BACKUP_CONFIG.get(environment, BACKUP_CONFIG['production'])
    
    # Calculate total storage
    total_storage_gb = sum(vm.get('storage_gb', 0) for vm in vms)
    
    # Apply compression and deduplication
    compression = BACKUP_CONFIG.get('compression_ratio', 0.7)
    dedup = BACKUP_CONFIG.get('deduplication_ratio', 0.5)
    
    # Calculate costs with tiering if enabled
    if BACKUP_CONFIG.get('enable_storage_tiering', True):
        costs = calculate_tiered_storage_costs(total_storage_gb, compression, dedup, retention, region)
    else:
        # Simple calculation without tiering (all warm storage)
        backup_storage_gb = total_storage_gb * compression * dedup
        rate = get_backup_rate('backup_storage_per_gb_month', region)
        monthly_cost = backup_storage_gb * rate
        costs = {
            'backup_storage_gb': backup_storage_gb,
            'monthly_cost': monthly_cost,
            'tier_breakdown': {
                'warm': {'gb': backup_storage_gb, 'cost': monthly_cost}
            }
        }
    
    return {
        'vm_count': len(vms),
        'storage_gb': total_storage_gb,
        'backup_storage_gb': costs['backup_storage_gb'],
        'monthly_cost': costs['monthly_cost'],
        'annual_cost': costs['monthly_cost'] * 12,
        'tier_breakdown': costs.get('tier_breakdown', {}),
        'daily_gb': costs.get('daily_gb', 0),
        'weekly_gb': costs.get('weekly_gb', 0),
        'monthly_gb': costs.get('monthly_gb', 0),
        'retention_summary': {
            'daily': f"{retention.get('daily_retention_days', 0)} days",
            'weekly': f"{retention.get('weekly_retention_weeks', 0)} weeks" if retention.get('weekly_retention_weeks', 0) > 0 else "None",
            'monthly': f"{retention.get('monthly_retention_months', 0)} months" if retention.get('monthly_retention_months', 0) > 0 else "None"
        }
    }


def calculate_tiered_storage_costs(total_storage_gb: float, compression: float, dedup: float, 
                                   retention: Dict, region: str) -> Dict:
    """
    Calculate backup costs with intelligent storage tiering
    
    Strategy:
    - Daily backups: warm (7 days) → archive
    - Weekly backups: warm (7 days) → archive
    - Monthly backups: warm (30 days) → archive (60 days) → deep archive
    
    Returns:
        {
            'backup_storage_gb': 12250,
            'monthly_cost': 875.00,
            'tier_breakdown': {...},
            'daily_gb': 5000,
            'weekly_gb': 4000,
            'monthly_gb': 3250
        }
    """
    tier_strategy = BACKUP_CONFIG.get('tier_strategy', {})
    incremental_ratio = BACKUP_CONFIG.get('incremental_ratio', 0.2)
    
    # Get pricing rates
    warm_rate = get_backup_rate('backup_storage_per_gb_month', region)
    archive_rate = get_backup_rate('s3_glacier_flexible_per_gb_month', region)
    deep_rate = get_backup_rate('s3_glacier_deep_per_gb_month', region)
    
    total_cost = 0
    tier_breakdown = {'warm': {'gb': 0, 'cost': 0}, 'archive': {'gb': 0, 'cost': 0}, 'deep_archive': {'gb': 0, 'cost': 0}}
    
    # Base backup size (full backup after compression/dedup)
    base_backup_gb = total_storage_gb * compression * dedup
    
    # === DAILY BACKUPS ===
    daily_retention = retention.get('daily_retention_days', 0)
    if daily_retention > 0:
        daily_strategy = tier_strategy.get('daily', {'warm_days': 7, 'archive_days': 7})
        
        # Full backup + incrementals
        daily_full_gb = base_backup_gb
        daily_incremental_gb = base_backup_gb * incremental_ratio * (daily_retention - 1)
        daily_total_gb = daily_full_gb + daily_incremental_gb
        
        # Warm storage
        warm_days = min(daily_strategy.get('warm_days', 7), daily_retention)
        daily_warm_gb = daily_total_gb * (warm_days / daily_retention)
        daily_warm_cost = daily_warm_gb * warm_rate
        
        # Archive storage
        archive_days = daily_retention - warm_days
        daily_archive_gb = daily_total_gb * (archive_days / daily_retention) if archive_days > 0 else 0
        daily_archive_cost = daily_archive_gb * archive_rate
        
        total_cost += daily_warm_cost + daily_archive_cost
        tier_breakdown['warm']['gb'] += daily_warm_gb
        tier_breakdown['warm']['cost'] += daily_warm_cost
        tier_breakdown['archive']['gb'] += daily_archive_gb
        tier_breakdown['archive']['cost'] += daily_archive_cost
    
    # === WEEKLY BACKUPS ===
    weekly_retention_weeks = retention.get('weekly_retention_weeks', 0)
    weekly_retention_days = weekly_retention_weeks * 7
    if weekly_retention_days > 0:
        weekly_strategy = tier_strategy.get('weekly', {'warm_days': 7, 'archive_days': 7})
        weekly_total_gb = base_backup_gb * weekly_retention_weeks
        
        # Warm storage
        warm_days = min(weekly_strategy.get('warm_days', 7), weekly_retention_days)
        weekly_warm_gb = weekly_total_gb * (warm_days / weekly_retention_days)
        weekly_warm_cost = weekly_warm_gb * warm_rate
        
        # Archive storage
        archive_days = weekly_retention_days - warm_days
        weekly_archive_gb = weekly_total_gb * (archive_days / weekly_retention_days) if archive_days > 0 else 0
        weekly_archive_cost = weekly_archive_gb * archive_rate
        
        total_cost += weekly_warm_cost + weekly_archive_cost
        tier_breakdown['warm']['gb'] += weekly_warm_gb
        tier_breakdown['warm']['cost'] += weekly_warm_cost
        tier_breakdown['archive']['gb'] += weekly_archive_gb
        tier_breakdown['archive']['cost'] += weekly_archive_cost
    
    # === MONTHLY BACKUPS ===
    monthly_retention_months = retention.get('monthly_retention_months', 0)
    monthly_retention_days = monthly_retention_months * 30
    if monthly_retention_days > 0:
        monthly_strategy = tier_strategy.get('monthly', {'warm_days': 30, 'archive_days': 60, 'deep_archive_days': 180})
        monthly_total_gb = base_backup_gb * monthly_retention_months
        
        # Warm storage
        warm_days = min(monthly_strategy.get('warm_days', 30), monthly_retention_days)
        monthly_warm_gb = monthly_total_gb * (warm_days / monthly_retention_days)
        monthly_warm_cost = monthly_warm_gb * warm_rate
        
        # Archive storage
        archive_start = warm_days
        archive_end = min(monthly_strategy.get('deep_archive_days', monthly_retention_days), monthly_retention_days)
        archive_days = archive_end - archive_start
        monthly_archive_gb = monthly_total_gb * (archive_days / monthly_retention_days) if archive_days > 0 else 0
        monthly_archive_cost = monthly_archive_gb * archive_rate
        
        # Deep archive storage (if enabled)
        monthly_deep_gb = 0
        monthly_deep_cost = 0
        if BACKUP_CONFIG.get('deep_archive_enabled', False) and 'deep_archive_days' in monthly_strategy:
            deep_days = monthly_retention_days - archive_end
            monthly_deep_gb = monthly_total_gb * (deep_days / monthly_retention_days) if deep_days > 0 else 0
            monthly_deep_cost = monthly_deep_gb * deep_rate
        
        total_cost += monthly_warm_cost + monthly_archive_cost + monthly_deep_cost
        tier_breakdown['warm']['gb'] += monthly_warm_gb
        tier_breakdown['warm']['cost'] += monthly_warm_cost
        tier_breakdown['archive']['gb'] += monthly_archive_gb
        tier_breakdown['archive']['cost'] += monthly_archive_cost
        tier_breakdown['deep_archive']['gb'] += monthly_deep_gb
        tier_breakdown['deep_archive']['cost'] += monthly_deep_cost
    
    total_backup_gb = tier_breakdown['warm']['gb'] + tier_breakdown['archive']['gb'] + tier_breakdown['deep_archive']['gb']
    
    return {
        'backup_storage_gb': total_backup_gb,
        'monthly_cost': total_cost,
        'tier_breakdown': tier_breakdown,
        'daily_gb': daily_total_gb if daily_retention > 0 else 0,
        'weekly_gb': weekly_total_gb if weekly_retention_days > 0 else 0,
        'monthly_gb': monthly_total_gb if monthly_retention_days > 0 else 0
    }


@lru_cache(maxsize=20)
def get_backup_pricing_from_api(region: str) -> Dict:
    """
    Get real-time backup pricing from AWS Price List API
    
    Returns:
        {
            'backup_storage_per_gb_month': 0.05,
            'backup_cold_storage_per_gb_month': 0.01,
            's3_glacier_instant_per_gb_month': 0.004,
            's3_glacier_flexible_per_gb_month': 0.0036,
            's3_glacier_deep_per_gb_month': 0.00099,
            'region': 'us-east-1',
            'source': 'api' or 'fallback'
        }
    """
    if not BACKUP_CONFIG.get('use_pricing_api', True):
        logger.info("Pricing API disabled, using fallback rates")
        return {**BACKUP_CONFIG['fallback_rates'], 'region': region, 'source': 'fallback'}
    
    try:
        logger.info(f"Fetching real-time backup pricing from AWS Price List API for {region}")
        
        # Initialize pricing client (must use us-east-1 for Price List API)
        pricing_client = boto3.client('pricing', region_name='us-east-1')
        
        # Map region code to AWS location name
        region_location_map = {
            'us-east-1': 'US East (N. Virginia)',
            'us-east-2': 'US East (Ohio)',
            'us-west-1': 'US West (N. California)',
            'us-west-2': 'US West (Oregon)',
            'eu-west-1': 'EU (Ireland)',
            'eu-central-1': 'EU (Frankfurt)',
            'ap-southeast-1': 'Asia Pacific (Singapore)',
            'ap-southeast-2': 'Asia Pacific (Sydney)',
            'ap-northeast-1': 'Asia Pacific (Tokyo)',
            'ap-south-1': 'Asia Pacific (Mumbai)',
            'sa-east-1': 'South America (Sao Paulo)',
            'ca-central-1': 'Canada (Central)',
            'eu-west-2': 'EU (London)',
            'eu-west-3': 'EU (Paris)',
            'eu-north-1': 'EU (Stockholm)',
            'ap-northeast-2': 'Asia Pacific (Seoul)',
            'ap-northeast-3': 'Asia Pacific (Osaka)',
            'ap-east-1': 'Asia Pacific (Hong Kong)',
            'me-south-1': 'Middle East (Bahrain)',
            'af-south-1': 'Africa (Cape Town)',
        }
        
        location = region_location_map.get(region, 'US East (N. Virginia)')
        
        rates = {}
        
        # === 1. AWS Backup Storage Pricing ===
        # AWS Backup doesn't have clear storageClass filters, need to search by usage type
        try:
            backup_response = pricing_client.get_products(
                ServiceCode='AWSBackup',
                Filters=[
                    {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': location},
                ],
                MaxResults=50
            )
            
            # Search for warm and cold storage in the results
            for price_str in backup_response.get('PriceList', []):
                price_item = json.loads(price_str)
                product = price_item.get('product', {})
                attributes = product.get('attributes', {})
                usage_type = attributes.get('usagetype', '').lower()
                
                # Look for storage-related usage types
                if 'warmbytes' in usage_type or 'warm-bytes' in usage_type:
                    on_demand = price_item.get('terms', {}).get('OnDemand', {})
                    if on_demand:
                        first_term = list(on_demand.values())[0]
                        price_dimensions = first_term.get('priceDimensions', {})
                        if price_dimensions:
                            first_price = list(price_dimensions.values())[0]
                            price_per_unit = first_price.get('pricePerUnit', {}).get('USD', '0')
                            if float(price_per_unit) > 0:
                                rates['backup_storage_per_gb_month'] = float(price_per_unit)
                                logger.info(f"✓ AWS Backup warm storage: ${price_per_unit}/GB-month")
                                break
                
                elif 'coldbytes' in usage_type or 'cold-bytes' in usage_type:
                    on_demand = price_item.get('terms', {}).get('OnDemand', {})
                    if on_demand:
                        first_term = list(on_demand.values())[0]
                        price_dimensions = first_term.get('priceDimensions', {})
                        if price_dimensions:
                            first_price = list(price_dimensions.values())[0]
                            price_per_unit = first_price.get('pricePerUnit', {}).get('USD', '0')
                            if float(price_per_unit) > 0:
                                rates['backup_cold_storage_per_gb_month'] = float(price_per_unit)
                                logger.info(f"✓ AWS Backup cold storage: ${price_per_unit}/GB-month")
        except Exception as e:
            logger.warning(f"Failed to get AWS Backup pricing: {e}")
        
        # === 2. S3 Glacier Storage Pricing ===
        try:
            s3_response = pricing_client.get_products(
                ServiceCode='AmazonS3',
                Filters=[
                    {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': location},
                    {'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': 'Storage'},
                ],
                MaxResults=100
            )
            
            # Search for Glacier storage classes
            for price_str in s3_response.get('PriceList', []):
                price_item = json.loads(price_str)
                product = price_item.get('product', {})
                attributes = product.get('attributes', {})
                storage_class = attributes.get('storageClass', '')
                volume_type = attributes.get('volumeType', '')
                usage_type = attributes.get('usagetype', '').lower()
                
                # Skip non-storage items
                if 'timedstorage' not in usage_type:
                    continue
                
                # Skip staging storage (temporary storage during transitions)
                if 'staging' in usage_type:
                    continue
                
                # Get price
                on_demand = price_item.get('terms', {}).get('OnDemand', {})
                if not on_demand:
                    continue
                
                first_term = list(on_demand.values())[0]
                price_dimensions = first_term.get('priceDimensions', {})
                if not price_dimensions:
                    continue
                
                first_price = list(price_dimensions.values())[0]
                price_per_unit = first_price.get('pricePerUnit', {}).get('USD', '0')
                
                if float(price_per_unit) == 0:
                    continue
                
                # Match Glacier Instant Retrieval
                if 'glacier instant retrieval' in storage_class.lower() or 'gir' in usage_type:
                    if 's3_glacier_instant_per_gb_month' not in rates:
                        rates['s3_glacier_instant_per_gb_month'] = float(price_per_unit)
                        logger.info(f"✓ S3 Glacier Instant Retrieval: ${price_per_unit}/GB-month")
                
                # Match Glacier Flexible Retrieval (formerly Glacier)
                elif ('glacier flexible retrieval' in storage_class.lower() or 
                      'glacier' in volume_type.lower() and 'deep' not in volume_type.lower() and 
                      'instant' not in volume_type.lower()):
                    if 's3_glacier_flexible_per_gb_month' not in rates:
                        rates['s3_glacier_flexible_per_gb_month'] = float(price_per_unit)
                        logger.info(f"✓ S3 Glacier Flexible Retrieval: ${price_per_unit}/GB-month")
                
                # Match Glacier Deep Archive
                elif 'deep archive' in storage_class.lower() or 'deep archive' in volume_type.lower() or 'gda' in usage_type:
                    if 's3_glacier_deep_per_gb_month' not in rates:
                        rates['s3_glacier_deep_per_gb_month'] = float(price_per_unit)
                        logger.info(f"✓ S3 Glacier Deep Archive: ${price_per_unit}/GB-month")
        
        except Exception as e:
            logger.warning(f"Failed to get S3 Glacier pricing: {e}")
        
        # Fill in missing rates with fallback
        fallback_rates = BACKUP_CONFIG['fallback_rates'].copy()
        for key in fallback_rates:
            if key not in rates:
                rates[key] = fallback_rates[key]
        
        # Check if we got at least some rates from API
        api_rate_count = sum(1 for k, v in rates.items() if k in ['backup_storage_per_gb_month', 'backup_cold_storage_per_gb_month', 
                                                                     's3_glacier_instant_per_gb_month', 's3_glacier_flexible_per_gb_month', 
                                                                     's3_glacier_deep_per_gb_month'])
        
        if api_rate_count >= 3:
            logger.info(f"✓ Successfully fetched {api_rate_count}/5 backup pricing rates from AWS API")
            return {**rates, 'region': region, 'source': 'api'}
        elif api_rate_count > 0:
            logger.info(f"✓ Fetched {api_rate_count}/5 rates from API, using fallback for remaining")
            return {**rates, 'region': region, 'source': 'api_partial'}
        else:
            logger.info(f"No rates from API, using fallback rates with regional multiplier")
            multiplier = BACKUP_CONFIG.get('regional_multipliers', {}).get(region, 1.0)
            for key in rates:
                if isinstance(rates[key], (int, float)):
                    rates[key] = rates[key] * multiplier
            return {**rates, 'region': region, 'source': 'fallback_regional'}
        
    except Exception as e:
        logger.warning(f"Failed to get pricing from AWS API: {e}, using fallback rates")
        
        # Apply regional multiplier to fallback rates
        fallback_rates = BACKUP_CONFIG['fallback_rates'].copy()
        multiplier = BACKUP_CONFIG.get('regional_multipliers', {}).get(region, 1.0)
        
        for key in fallback_rates:
            if isinstance(fallback_rates[key], (int, float)):
                fallback_rates[key] = fallback_rates[key] * multiplier
        
        return {**fallback_rates, 'region': region, 'source': 'fallback_error'}


def get_backup_rate(rate_type: str, region: str) -> float:
    """
    Get backup rate with API fallback
    
    Args:
        rate_type: Type of rate (e.g., 'backup_storage_per_gb_month')
        region: AWS region
    
    Returns:
        Rate in $/GB-month
    """
    rates = get_backup_pricing_from_api(region)
    return rates.get(rate_type, BACKUP_CONFIG['fallback_rates'].get(rate_type, 0.05))


def _empty_environment_costs() -> Dict:
    """Return empty cost structure"""
    return {
        'vm_count': 0,
        'storage_gb': 0,
        'backup_storage_gb': 0,
        'monthly_cost': 0,
        'annual_cost': 0,
        'tier_breakdown': {},
        'retention_summary': {}
    }


# Test function
if __name__ == "__main__":
    # Test backup calculation
    test_vms = [
        {'vm_name': 'WebServer-PROD-01', 'storage_gb': 500},
        {'vm_name': 'AppServer-PROD-02', 'storage_gb': 1000},
        {'vm_name': 'DBServer-DEV-01', 'storage_gb': 2000},
        {'vm_name': 'TestServer-UAT-01', 'storage_gb': 500},
    ]
    
    print("Testing backup cost calculation...")
    costs = calculate_backup_costs(test_vms, 'us-east-1')
    
    print(f"\nTotal Monthly: ${costs['total_monthly']:,.2f}")
    print(f"Total Annual: ${costs['total_annual']:,.2f}")
    print(f"Production VMs: {costs['production']['vm_count']}")
    print(f"Pre-Production VMs: {costs['pre_production']['vm_count']}")
    print(f"Savings vs all-warm: ${costs.get('savings_vs_all_warm', 0):,.2f} ({costs.get('savings_percentage', 0):.1f}%)")
