"""
EKS Pricing and Migration Strategy Module
Handles VM categorization, cluster sizing, and cost calculations for EKS migration
"""
import re
from typing import Dict, List, Tuple, Optional
from agents.config.config import EKS_CONFIG, PRICING_CONFIG
from agents.pricing.pricing_tools import get_ec2_pricing, get_rds_pricing


def categorize_vms_for_eks(vms: List[Dict], strategy: str = None, vcpu_threshold: int = None, logger=None) -> Dict:
    """
    Categorize VMs into EKS vs EC2 based on OS, size, and suitability.
    
    OS-Aware Logic:
    - Linux VMs: Prefer EKS (cost-effective containers)
    - Windows VMs: Prefer EC2 in hybrid mode (better cost)
    - Windows VMs: Allow EKS in all-eks mode (with cost warnings)
    
    Args:
        vms: List of VM dictionaries with keys: name, vcpu, memory, os, etc.
        strategy: 'hybrid', 'all-eks', or 'disabled' (defaults to config)
        vcpu_threshold: vCPU threshold for hybrid strategy (defaults to config)
        logger: Optional logger for detailed exclusion reporting
    
    Returns:
        Dictionary with categorized VMs and summary statistics
    """
    if not EKS_CONFIG.get('enabled', True):
        return {
            'eks_linux': [],
            'eks_windows': [],
            'ec2': vms,
            'summary': {
                'total_vms': len(vms),
                'eks_total': 0,
                'eks_linux': 0,
                'eks_windows': 0,
                'ec2_total': len(vms),
                'strategy': 'disabled'
            }
        }
    
    strategy = strategy or EKS_CONFIG.get('strategy', 'hybrid')
    vcpu_threshold = vcpu_threshold or EKS_CONFIG.get('vcpu_threshold', 4)
    
    eks_linux = []
    eks_windows = []
    ec2 = []
    
    # Track exclusion reasons for logging
    exclusion_stats = {
        'total_evaluated': len(vms),
        'windows_os': 0,
        'large_vm': 0,
        'high_memory_ratio': 0,
        'exclude_pattern': {},
        'windows_desktop': 0,
        'accepted_to_eks': 0
    }
    
    for vm in vms:
        os_lower = vm.get('os', '').lower()
        vcpu = vm.get('vcpu', 0)
        memory = vm.get('memory', 0)
        name_lower = vm.get('name', '').lower()
        
        # Check if VM is suitable for containerization
        is_suitable, reason = _is_eks_suitable(vm, strategy, vcpu_threshold)
        
        if strategy == 'all-eks':
            if is_suitable:
                if 'windows' in os_lower:
                    eks_windows.append({**vm, 'migration_target': 'EKS', 'migration_reason': reason})
                    exclusion_stats['accepted_to_eks'] += 1
                else:
                    eks_linux.append({**vm, 'migration_target': 'EKS', 'migration_reason': reason})
                    exclusion_stats['accepted_to_eks'] += 1
            else:
                ec2.append({**vm, 'migration_target': 'EC2', 'migration_reason': reason})
                _track_exclusion_reason(reason, exclusion_stats)
        
        elif strategy == 'hybrid':
            # Windows VMs: Prefer EC2 (better cost)
            if 'windows' in os_lower:
                ec2.append({**vm, 'migration_target': 'EC2', 
                           'migration_reason': 'Windows - EC2 more cost-effective than containers'})
                exclusion_stats['windows_os'] += 1
            # Linux VMs: Consider EKS based on size and suitability
            elif vcpu < vcpu_threshold and is_suitable:
                eks_linux.append({**vm, 'migration_target': 'EKS', 
                                 'migration_reason': f'Small Linux VM (< {vcpu_threshold} vCPU) - containerizable'})
                exclusion_stats['accepted_to_eks'] += 1
            else:
                ec2.append({**vm, 'migration_target': 'EC2', 'migration_reason': reason})
                _track_exclusion_reason(reason, exclusion_stats)
        
        else:  # disabled
            ec2.append({**vm, 'migration_target': 'EC2', 'migration_reason': 'EKS disabled'})
    
    # Log exclusion statistics
    if logger:
        _log_exclusion_stats(exclusion_stats, vcpu_threshold, logger)
    
    # Add size-based categorization for Excel export
    def categorize_by_size(vms):
        small = [vm for vm in vms if vm.get('vcpu', 0) < 4]
        medium = [vm for vm in vms if 4 <= vm.get('vcpu', 0) < 8]
        large = [vm for vm in vms if 8 <= vm.get('vcpu', 0) < 16]
        xlarge = [vm for vm in vms if vm.get('vcpu', 0) >= 16]
        return small, medium, large, xlarge
    
    linux_small, linux_medium, linux_large, linux_xlarge = categorize_by_size(eks_linux)
    windows_small, windows_medium, windows_large, windows_xlarge = categorize_by_size(eks_windows)
    
    # Extract database VMs from EC2 list
    db_patterns = ['sql', 'db', 'database', 'oracle', 'postgres', 'mysql', 'mariadb']
    databases = [vm for vm in ec2 if any(p in vm.get('name', '').lower() for p in db_patterns)]
    
    return {
        'eks_linux': eks_linux,
        'eks_windows': eks_windows,
        'ec2': ec2,
        # Size-based categories for Excel
        'linux_small': linux_small,
        'linux_medium': linux_medium,
        'linux_large': linux_large,
        'linux_xlarge': linux_xlarge,
        'windows_small': windows_small,
        'windows_medium': windows_medium,
        'windows_large': windows_large,
        'windows_xlarge': windows_xlarge,
        'databases': databases,
        'summary': {
            'total_vms': len(vms),
            'eks_total': len(eks_linux) + len(eks_windows),
            'eks_linux': len(eks_linux),
            'eks_windows': len(eks_windows),
            'ec2_total': len(ec2),
            'strategy': strategy,
            'vcpu_threshold': vcpu_threshold if strategy == 'hybrid' else None
        },
        'exclusion_stats': exclusion_stats
    }



def _track_exclusion_reason(reason: str, stats: Dict):
    """Track exclusion reasons for statistics"""
    reason_lower = reason.lower()
    
    if 'large vm' in reason_lower or '>=' in reason_lower:
        stats['large_vm'] += 1
    elif 'high memory ratio' in reason_lower:
        stats['high_memory_ratio'] += 1
    elif 'windows desktop' in reason_lower:
        stats['windows_desktop'] += 1
    elif 'unsuitable for containers' in reason_lower:
        # Extract pattern name from reason
        pattern = reason.split(':')[-1].strip().split()[0] if ':' in reason else 'unknown'
        if pattern not in stats['exclude_pattern']:
            stats['exclude_pattern'][pattern] = 0
        stats['exclude_pattern'][pattern] += 1


def _log_exclusion_stats(stats: Dict, vcpu_threshold: int, logger):
    """Log detailed exclusion statistics"""
    logger.info("=" * 70)
    logger.info("EKS CATEGORIZATION BREAKDOWN")
    logger.info("=" * 70)
    logger.info(f"Total VMs evaluated: {stats['total_evaluated']}")
    logger.info(f"✓ Accepted to EKS: {stats['accepted_to_eks']}")
    logger.info(f"✗ Excluded from EKS: {stats['total_evaluated'] - stats['accepted_to_eks']}")
    logger.info("")
    logger.info("Exclusion Reasons:")
    
    if stats['windows_os'] > 0:
        logger.info(f"  • Windows OS (hybrid mode): {stats['windows_os']} VMs")
    
    if stats['large_vm'] > 0:
        logger.info(f"  • Large VM (>= {vcpu_threshold} vCPU): {stats['large_vm']} VMs")
    
    if stats['high_memory_ratio'] > 0:
        logger.info(f"  • High memory ratio (> 8 GB/vCPU): {stats['high_memory_ratio']} VMs")
    
    if stats['windows_desktop'] > 0:
        logger.info(f"  • Windows Desktop/GUI: {stats['windows_desktop']} VMs")
    
    if stats['exclude_pattern']:
        logger.info(f"  • Exclude patterns matched:")
        for pattern, count in sorted(stats['exclude_pattern'].items(), key=lambda x: -x[1]):
            logger.info(f"    - '{pattern}' pattern: {count} VMs")
    
    logger.info("=" * 70)


def _is_eks_suitable(vm: Dict, strategy: str, vcpu_threshold: int) -> Tuple[bool, str]:
    """Check if VM is suitable for containerization"""
    os_lower = vm.get('os', '').lower()
    vcpu = vm.get('vcpu', 0)
    memory = vm.get('memory', 0)
    name_lower = vm.get('name', '').lower()
    
    # Check for unsuitable patterns
    exclude_patterns = EKS_CONFIG.get('exclude_patterns', [])
    for pattern in exclude_patterns:
        if re.search(pattern, name_lower):
            return False, f'Unsuitable for containers: {pattern} workload'
    
    # Check Windows Desktop/GUI
    if 'windows' in os_lower:
        if any(x in os_lower for x in ['desktop', 'workstation', 'gui', 'client']):
            return False, 'Windows Desktop not containerizable'
    
    # Check memory ratio (high memory apps better on EC2)
    if vcpu > 0:
        memory_per_vcpu = memory / vcpu
        if memory_per_vcpu > 8:
            return False, 'High memory ratio - better on EC2 or RDS'
    
    # Check size for hybrid strategy
    if strategy == 'hybrid' and vcpu >= vcpu_threshold:
        return False, f'Large VM (>= {vcpu_threshold} vCPU) - direct migration to EC2'
    
    return True, 'Suitable for containerization'


def calculate_eks_cluster_size(eks_vms: List[Dict], region: str = 'us-east-1') -> Dict:
    """
    Calculate required EKS worker nodes with size-based consolidation.
    
    Separate calculations for Linux and Windows with different consolidation ratios.
    
    Args:
        eks_vms: List of VMs to containerize
        region: AWS region for pricing
    
    Returns:
        Dictionary with cluster configuration and worker node details
    """
    if not eks_vms:
        return {
            'linux_worker_nodes': [],
            'windows_worker_nodes': [],
            'all_worker_nodes': [],
            'total_vms': 0,
            'required_vcpu': 0,
            'required_memory': 0
        }
    
    # Separate Linux and Windows VMs
    linux_vms = [vm for vm in eks_vms if 'windows' not in vm.get('os', '').lower()]
    windows_vms = [vm for vm in eks_vms if 'windows' in vm.get('os', '').lower()]
    
    # Get consolidation ratios
    linux_ratios = EKS_CONFIG.get('linux_consolidation_ratios', {})
    windows_ratios = EKS_CONFIG.get('windows_consolidation_ratios', {})
    overhead_factor = EKS_CONFIG.get('overhead_factor', 1.15)
    
    # Calculate Linux requirements
    linux_vcpu, linux_memory = _calculate_consolidated_resources(linux_vms, linux_ratios)
    linux_vcpu *= overhead_factor
    linux_memory *= overhead_factor
    
    # Calculate Windows requirements
    windows_vcpu, windows_memory = _calculate_consolidated_resources(windows_vms, windows_ratios)
    windows_vcpu *= overhead_factor
    windows_memory *= overhead_factor
    
    # Select worker nodes
    linux_nodes = _select_worker_nodes(linux_vcpu, linux_memory, prefer_graviton=True, region=region) if linux_vcpu > 0 else []
    windows_nodes = _select_worker_nodes(windows_vcpu, windows_memory, prefer_graviton=False, region=region) if windows_vcpu > 0 else []
    
    # Calculate original vCPU (before consolidation)
    original_vcpu = sum(vm.get('vcpu', 0) for vm in eks_vms)
    original_memory = sum(vm.get('memory_gb', 0) for vm in eks_vms)
    
    # Calculate consolidation ratio
    required_vcpu_total = linux_vcpu + windows_vcpu
    consolidation_ratio = original_vcpu / required_vcpu_total if required_vcpu_total > 0 else 1.0
    
    # Calculate total capacity
    all_nodes = linux_nodes + windows_nodes
    total_vcpu_capacity = sum(node['vcpu'] * node.get('count', 1) for node in all_nodes)
    total_memory_capacity = sum(node['memory_gb'] * node.get('count', 1) for node in all_nodes)
    total_node_count = sum(node.get('count', 1) for node in all_nodes)
    
    return {
        'linux_worker_nodes': linux_nodes,
        'windows_worker_nodes': windows_nodes,
        'all_worker_nodes': all_nodes,
        'worker_nodes': all_nodes,  # Alias for Excel export compatibility
        'total_vms': len(eks_vms),
        'total_nodes': total_node_count,  # For Excel export - actual count of nodes
        'linux_vms': len(linux_vms),
        'windows_vms': len(windows_vms),
        'required_vcpu': required_vcpu_total,
        'required_memory': linux_memory + windows_memory,
        'total_vcpu': total_vcpu_capacity,  # For Excel export
        'total_memory_gb': total_memory_capacity,  # For Excel export
        'linux_vcpu': linux_vcpu,
        'linux_memory': linux_memory,
        'windows_vcpu': windows_vcpu,
        'windows_memory': windows_memory,
        'original_vcpu': original_vcpu,  # For Excel export
        'original_memory_gb': original_memory,  # For Excel export
        'consolidation_ratio': consolidation_ratio  # For Excel export
    }


def _calculate_consolidated_resources(vms: List[Dict], ratios: Dict) -> Tuple[float, float]:
    """Calculate consolidated vCPU and memory requirements"""
    total_vcpu = 0
    total_memory = 0
    
    for vm in vms:
        vcpu = vm.get('vcpu', 0)
        memory = vm.get('memory', 0)
        
        # Determine size category and get ratio
        if vcpu < 4:
            ratio = ratios.get('small', 3.5)
        elif vcpu < 8:
            ratio = ratios.get('medium', 2.5)
        elif vcpu < 16:
            ratio = ratios.get('large', 1.75)
        else:
            ratio = ratios.get('xlarge', 1.25)
        
        total_vcpu += vcpu / ratio
        total_memory += memory / ratio
    
    return total_vcpu, total_memory


def _select_worker_nodes(vcpu: float, memory: float, prefer_graviton: bool, region: str) -> List[Dict]:
    """Select optimal worker node types using bin-packing"""
    from agents.pricing.aws_pricing_calculator import AWSPricingCalculator
    
    # Check if Graviton is enabled in configuration
    graviton_enabled = EKS_CONFIG.get('enable_graviton', True)
    
    # Determine instance family based on memory ratio
    memory_ratio = memory / vcpu if vcpu > 0 else 4
    if memory_ratio < 3:
        family = 'c'  # Compute-optimized
    elif memory_ratio > 6:
        family = 'r'  # Memory-optimized
    else:
        family = 'm'  # General purpose
    
    # Build instance type list
    if prefer_graviton and graviton_enabled:
        # Graviton enabled: Use ARM-based instances (20% cheaper)
        generations = [f'{family}7g', f'{family}6g']
    else:
        # Graviton disabled or Windows: Use x86 instances only
        generations = [f'{family}7i', f'{family}6i', f'{family}6a', f'{family}5']
    
    # Get available instances
    available_instances = []
    calculator = AWSPricingCalculator(region=region)
    
    for gen in generations:
        for size in ['large', 'xlarge', '2xlarge', '4xlarge', '8xlarge', '12xlarge', '16xlarge']:
            instance_type = f'{gen}.{size}'
            specs = AWSPricingCalculator.INSTANCE_SPECS.get(instance_type)
            if specs:
                inst_vcpu, inst_memory = specs
                try:
                    # Use 3-Year Reserved Instance No Upfront pricing (not Compute SP)
                    # This matches the Excel display of "3-Year Reserved Instance"
                    hourly_rate = calculator.get_ec2_price_by_term(
                        instance_type=instance_type,
                        os_type='Linux',
                        region=region,
                        term='3yr',
                        purchase_option='No Upfront'
                    )
                except:
                    hourly_rate = 0.035 * inst_vcpu
                
                available_instances.append({
                    'type': instance_type,
                    'vcpu': inst_vcpu,
                    'memory': inst_memory,
                    'hourly_rate': hourly_rate,
                    'generation': gen
                })
    
    # Bin-packing: Use larger instances first
    selected_nodes = []
    remaining_vcpu = vcpu
    remaining_memory = memory
    
    available_instances.sort(key=lambda x: (generations.index(x['generation']), -x['vcpu']))
    
    for instance in available_instances:
        while (remaining_vcpu >= instance['vcpu'] * 0.7 and remaining_memory >= instance['memory'] * 0.7):
            selected_nodes.append(instance)
            remaining_vcpu -= instance['vcpu']
            remaining_memory -= instance['memory']
            if remaining_vcpu <= 0 and remaining_memory <= 0:
                break
        if remaining_vcpu <= 0 and remaining_memory <= 0:
            break
    
    # If no nodes selected but we have requirements, add minimum nodes
    if not selected_nodes and vcpu > 0 and available_instances:
        # Use smallest available instance
        smallest = min(available_instances, key=lambda x: x['vcpu'])
        num_nodes = max(2, int((vcpu / smallest['vcpu']) + 0.5))  # Round up, minimum 2 for HA
        selected_nodes = [smallest] * num_nodes
    
    # Add buffer node for HA
    if selected_nodes:
        buffer_instance = min([i for i in available_instances if i['generation'] == selected_nodes[0]['generation']], 
                             key=lambda x: x['vcpu'])
        selected_nodes.append(buffer_instance)
    
    # Aggregate nodes by instance type and convert to Excel-compatible format
    from collections import Counter
    node_counts = Counter(node['type'] for node in selected_nodes)
    
    aggregated_nodes = []
    for instance_type, count in node_counts.items():
        # Find the node details
        node_details = next(n for n in selected_nodes if n['type'] == instance_type)
        aggregated_nodes.append({
            'instance_type': instance_type,
            'count': count,
            'vcpu': node_details['vcpu'],
            'memory_gb': node_details['memory'],
            'hourly_rate': node_details['hourly_rate']
        })
    
    return aggregated_nodes


# Performance optimization: Calculate EKS costs in parallel with EC2 costs
def calculate_eks_costs_async(eks_cluster: Dict, num_clusters: int, region: str) -> Dict:
    """
    Calculate total EKS costs (optimized for parallel execution).
    This function is designed to run concurrently with EC2 cost calculations.
    Uses AWS Pricing API for region-specific costs.
    """
    if not eks_cluster.get('all_worker_nodes'):
        return {'total_3yr': 0, 'monthly_avg': 0}
    
    # Import pricing calculator
    from agents.pricing.aws_pricing_calculator import AWSPricingCalculator
    calculator = AWSPricingCalculator(region=region)
    
    # Control plane cost - GET FROM API
    try:
        control_plane_hourly = calculator.get_eks_control_plane_price(region)
    except:
        control_plane_hourly = EKS_CONFIG.get('eks_control_plane_hourly', 0.10)
    
    control_plane_3yr = control_plane_hourly * 24 * 365 * 3 * num_clusters
    
    # DEBUG: Log control plane calculation
    import logging
    logger = logging.getLogger('AgentWorkflow')
    logger.info(f"EKS Cost Calc - Control Plane Hourly: ${control_plane_hourly}")
    logger.info(f"EKS Cost Calc - Num Clusters: {num_clusters}")
    logger.info(f"EKS Cost Calc - Control Plane 3yr: ${control_plane_3yr:,.2f}")
    logger.info(f"EKS Cost Calc - Control Plane Monthly (3yr/36): ${control_plane_3yr / 36:,.2f}")
    
    # Worker node costs with Spot strategy
    worker_nodes = eks_cluster['all_worker_nodes']
    spot_pct = EKS_CONFIG.get('spot_percentage', 0.30)
    on_demand_pct = EKS_CONFIG.get('on_demand_percentage', 0.40)
    reserved_pct = EKS_CONFIG.get('reserved_percentage', 0.30)
    spot_discount = EKS_CONFIG.get('spot_discount', 0.70)
    
    # Calculate total hourly cost considering node counts
    # Note: hourly_rate is already the 3-Year Reserved Instance No Upfront rate
    total_hourly = sum(node['hourly_rate'] * node.get('count', 1) for node in worker_nodes)
    
    # Split costs by capacity type
    # Reserved: Use the RI rate directly (no additional discount needed)
    # On-Demand: Use On-Demand rate (approximately 1.67x the RI rate)
    # Spot: Use Spot rate (70% discount from On-Demand)
    reserved_hourly = total_hourly * reserved_pct  # Already at RI rate
    on_demand_hourly = total_hourly * on_demand_pct * 1.67  # On-Demand is ~1.67x RI rate
    spot_hourly = total_hourly * spot_pct * 1.67 * (1 - spot_discount)  # Spot discount from On-Demand
    
    # Calculate 3-year total
    worker_3yr = (reserved_hourly + on_demand_hourly + spot_hourly) * 24 * 365 * 3
    
    # DEBUG: Log worker node calculation
    logger.info(f"Worker Node Cost Calc - Total Hourly (RI rate): ${total_hourly:.4f}")
    logger.info(f"Worker Node Cost Calc - Reserved Hourly (30% at RI rate): ${reserved_hourly:.4f}")
    logger.info(f"Worker Node Cost Calc - On-Demand Hourly (40% at 1.67x RI): ${on_demand_hourly:.4f}")
    logger.info(f"Worker Node Cost Calc - Spot Hourly (30% at 70% discount from OD): ${spot_hourly:.4f}")
    logger.info(f"Worker Node Cost Calc - Combined Hourly: ${reserved_hourly + on_demand_hourly + spot_hourly:.4f}")
    logger.info(f"Worker Node Cost Calc - Worker 3yr: ${worker_3yr:,.2f}")
    logger.info(f"Worker Node Cost Calc - Worker Monthly (3yr/36): ${worker_3yr / 36:,.2f}")
    
    # Storage costs - GET FROM API
    try:
        ebs_rate_per_gb = calculator.get_ebs_gp3_price(region)
    except:
        ebs_rate_per_gb = 0.08
    
    num_nodes = sum(node.get('count', 1) for node in worker_nodes)  # Total actual nodes
    storage_3yr = num_nodes * 150 * ebs_rate_per_gb * 36  # 150GB per node, 36 months
    
    # Networking costs - SIMPLIFIED: 10% of compute cost
    # This provides a simpler, more predictable estimate than detailed ALB/NAT pricing
    compute_monthly = worker_3yr / 36
    networking_monthly = compute_monthly * 0.10  # 10% of compute cost
    networking_3yr = networking_monthly * 36
    
    # Monitoring costs - GET FROM API
    try:
        cloudwatch_rate = calculator.get_cloudwatch_logs_price(region)
    except:
        cloudwatch_rate = 0.50
    
    # Monitoring: 2GB/day per node, but monthly not 3-year calculation
    # 2GB/day * 30 days = 60GB/month per node
    monitoring_monthly = num_nodes * 2 * 30 * cloudwatch_rate  # 60GB/month per node
    monitoring_3yr = monitoring_monthly * 36
    
    total_3yr = control_plane_3yr + worker_3yr + storage_3yr + networking_3yr + monitoring_3yr
    monthly_avg = total_3yr / 36
    
    return {
        'control_plane_3yr': control_plane_3yr,
        'workers_3yr': worker_3yr,
        'storage_3yr': storage_3yr,
        'networking_3yr': networking_3yr,
        'monitoring_3yr': monitoring_3yr,
        'total_3yr': total_3yr,
        'monthly_avg': monthly_avg,
        'spot_savings_3yr': total_hourly * spot_pct * spot_discount * 24 * 365 * 3,
        # Add monthly breakdown for Excel export
        'total_monthly': monthly_avg,
        'control_plane_monthly': control_plane_3yr / 36,
        'compute_monthly': worker_3yr / 36,
        'storage_monthly': storage_3yr / 36,
        'networking_monthly': networking_3yr / 36,
        'data_transfer_monthly': 0,  # Included in networking
        'monitoring_monthly': monitoring_monthly,  # Use the monthly variable, not divided again
        # Add pricing sources for transparency
        'pricing_sources': {
            'control_plane_hourly': control_plane_hourly,
            'ebs_rate_per_gb_month': ebs_rate_per_gb,
            'alb_monthly': alb_monthly if 'alb_pricing' in locals() else 45,
            'nat_monthly': nat_monthly if 'nat_pricing' in locals() else 32.40,
            'cloudwatch_rate_per_gb': cloudwatch_rate,
            'region': region
        }
    }


def allocate_eks_costs_to_vms(eks_vms: List[Dict], eks_costs: Dict) -> List[Dict]:
    """Allocate EKS costs proportionally to VMs"""
    if not eks_vms or eks_costs.get('total_3yr', 0) == 0:
        return eks_vms
    
    total_vcpu = sum(vm.get('vcpu', 0) for vm in eks_vms)
    if total_vcpu == 0:
        return eks_vms
    
    for vm in eks_vms:
        vm_share = vm.get('vcpu', 0) / total_vcpu
        vm['eks_cost_3yr'] = eks_costs['total_3yr'] * vm_share
        vm['eks_cost_monthly'] = eks_costs['monthly_avg'] * vm_share
    
    return eks_vms



def recommend_eks_strategy(mra_data: Dict, project_info: Dict, vm_inventory: List[Dict]) -> Dict:
    """
    Recommend EKS strategy based on MRA findings and project context.
    
    Args:
        mra_data: Parsed MRA assessment data (can be None)
        project_info: Project description and goals from UI
        vm_inventory: VM inventory data
    
    Returns:
        Recommended strategy with rationale and confidence level
    """
    # Default to hybrid if no MRA data
    if not mra_data:
        avg_vm_size = sum(vm.get('vcpu', 0) for vm in vm_inventory) / len(vm_inventory) if vm_inventory else 4
        threshold = 8 if avg_vm_size < 4 else 4
        
        return {
            'recommended_strategy': 'hybrid',
            'rationale': [
                'No MRA data available - using balanced approach',
                f'Average VM size: {avg_vm_size:.1f} vCPU',
                f'Threshold set to {threshold} vCPU for optimal balance'
            ],
            'vcpu_threshold': threshold,
            'confidence': 'Medium',
            'timeline_months': 9
        }
    
    # Extract MRA scores (from mra_analysis.py functions)
    cloud_readiness = mra_data.get('cloud_readiness_score', 3)
    container_expertise = mra_data.get('container_expertise_score', 3)
    devops_maturity = mra_data.get('devops_maturity_score', 3)
    
    # Analyze project description for goals
    project_goals = _analyze_project_description(project_info.get('projectDescription', ''))
    
    # Decision logic
    if 'cloud-native' in project_goals or 'modernization' in project_goals:
        if container_expertise >= 3 and devops_maturity >= 3:
            return {
                'recommended_strategy': 'all-eks',
                'rationale': [
                    'Project goals emphasize cloud-native transformation',
                    f'Strong container expertise (MRA score: {container_expertise}/5)',
                    f'Mature DevOps practices (MRA score: {devops_maturity}/5)',
                    'Organization ready for full containerization'
                ],
                'vcpu_threshold': None,
                'confidence': 'High',
                'timeline_months': 12
            }
        else:
            return {
                'recommended_strategy': 'hybrid',
                'rationale': [
                    'Project goals include modernization',
                    f'Developing container expertise (MRA score: {container_expertise}/5)',
                    'Hybrid approach balances innovation with risk',
                    'Containerize smaller workloads first to build expertise'
                ],
                'vcpu_threshold': 4,
                'confidence': 'Medium-High',
                'timeline_months': 9
            }
    
    elif 'lift-and-shift' in project_goals or 'fast migration' in project_goals:
        if cloud_readiness >= 4:
            return {
                'recommended_strategy': 'hybrid',
                'rationale': [
                    'Fast migration timeline prioritized',
                    f'Good cloud readiness (MRA score: {cloud_readiness}/5)',
                    'Hybrid approach provides quick wins with smaller VMs',
                    'Larger workloads migrate directly to EC2 for speed'
                ],
                'vcpu_threshold': 4,
                'confidence': 'Medium',
                'timeline_months': 6
            }
        else:
            return {
                'recommended_strategy': 'disabled',
                'rationale': [
                    'Lift-and-shift approach prioritized',
                    f'Building cloud readiness (MRA score: {cloud_readiness}/5)',
                    'Focus on EC2 migration to minimize complexity',
                    'Consider EKS in future phases after cloud adoption'
                ],
                'vcpu_threshold': None,
                'confidence': 'High',
                'timeline_months': 6
            }
    
    else:
        # Default: Balanced approach
        avg_vm_size = sum(vm.get('vcpu', 0) for vm in vm_inventory) / len(vm_inventory) if vm_inventory else 4
        threshold = 8 if avg_vm_size < 4 else 4
        
        return {
            'recommended_strategy': 'hybrid',
            'rationale': [
                'Balanced approach recommended',
                f'Average VM size: {avg_vm_size:.1f} vCPU',
                f'Container expertise: {container_expertise}/5 (MRA)',
                f'Threshold set to {threshold} vCPU for optimal balance'
            ],
            'vcpu_threshold': threshold,
            'confidence': 'Medium',
            'timeline_months': 9
        }


def _analyze_project_description(description: str) -> List[str]:
    """Extract goals from project description"""
    description_lower = description.lower()
    goals = []
    
    if any(word in description_lower for word in ['cloud-native', 'modernization', 'containerization', 'kubernetes', 'microservices']):
        goals.append('cloud-native')
    
    if any(word in description_lower for word in ['lift-and-shift', 'rehost', 'fast migration', 'quick migration']):
        goals.append('lift-and-shift')
    
    if any(word in description_lower for word in ['cost', 'savings', 'optimize', 'reduce spend']):
        goals.append('cost-optimization')
    
    if any(word in description_lower for word in ['innovation', 'agility', 'devops', 'automation']):
        goals.append('innovation')
    
    return goals


# Quick test function
if __name__ == "__main__":
    print("EKS Pricing Module - Quick Test")
    
    # Test VM categorization
    test_vms = [
        {'name': 'web-server-01', 'vcpu': 2, 'memory': 8, 'os': 'Linux'},
        {'name': 'app-server-01', 'vcpu': 4, 'memory': 16, 'os': 'Linux'},
        {'name': 'db-server-01', 'vcpu': 8, 'memory': 32, 'os': 'Linux'},
        {'name': 'win-server-01', 'vcpu': 2, 'memory': 8, 'os': 'Windows Server 2019'},
    ]
    
    result = categorize_vms_for_eks(test_vms, strategy='hybrid', vcpu_threshold=4)
    print(f"\nCategorization (Hybrid):")
    print(f"  EKS Linux: {len(result['eks_linux'])} VMs")
    print(f"  EKS Windows: {len(result['eks_windows'])} VMs")
    print(f"  EC2: {len(result['ec2'])} VMs")
    
    # Test cluster sizing
    if result['eks_linux']:
        cluster = calculate_eks_cluster_size(result['eks_linux'])
        print(f"\nCluster Sizing:")
        print(f"  Worker nodes: {len(cluster['all_worker_nodes'])}")
        print(f"  Required vCPU: {cluster['required_vcpu']:.1f}")
    
    print("\n✓ EKS Pricing Module tests complete")
