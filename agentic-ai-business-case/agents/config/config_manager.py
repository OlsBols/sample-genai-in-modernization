"""
Configuration management with user overrides.
Merges default config.py values with user overrides from JSON file.
"""
import json
import os
import sys
from typing import Any, Dict

# Add current directory to path to import agents.config.config as config
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import agents.config.config as config

OVERRIDE_FILE = 'output/config_overrides.json'

def get_config_schema() -> Dict[str, Any]:
    """
    Return configuration schema with metadata for UI.
    Only includes actively used settings (not experimental/NYI).
    """
    return {
        'pricing': {
            'label': 'Pricing Configuration',
            'description': 'Control AWS pricing models and instance preferences',
            'settings': {
                'USE_DETERMINISTIC_PRICING': {
                    'type': 'boolean',
                    'default': config.USE_DETERMINISTIC_PRICING,
                    'label': 'Use Deterministic Pricing',
                    'description': 'Use AWS Price List API for accurate pricing instead of LLM estimation'
                },
                'pricing_model': {
                    'type': 'select',
                    'default': config.PRICING_CONFIG['pricing_model'],
                    'options': ['3yr_compute_sp', '3yr_ec2_sp', '3yr_no_upfront', '1yr_no_upfront', 'on_demand'],
                    'label': 'Pricing Model',
                    'description': '3yr_compute_sp = 3-Year Compute Savings Plan (recommended, most flexible)'
                },
                'prefer_graviton': {
                    'type': 'boolean',
                    'default': config.PRICING_CONFIG['prefer_graviton'],
                    'label': 'Prefer AWS Graviton',
                    'description': 'Use ARM-based Graviton instances for Linux (20% cheaper, better performance)'
                },
                'generation_preference': {
                    'type': 'select',
                    'default': config.PRICING_CONFIG['generation_preference'],
                    'options': ['latest', 'newer', 'current', 'cost_optimized'],
                    'label': 'Instance Generation',
                    'description': 'newer = 6th gen (recommended for best price/performance balance)'
                }
            }
        },
        'right_sizing': {
            'label': 'Right-Sizing Configuration',
            'description': 'Apply right-sizing based on actual utilization (ATX methodology)',
            'settings': {
                'enable_right_sizing': {
                    'type': 'boolean',
                    'default': config.RIGHT_SIZING_CONFIG['enable_right_sizing'],
                    'label': 'Enable Right-Sizing',
                    'description': 'Optimize instance sizes based on actual CPU/memory utilization'
                },
                'cpu_peak_utilization_percent': {
                    'type': 'number',
                    'default': config.RIGHT_SIZING_CONFIG['cpu_peak_utilization_percent'],
                    'min': 10,
                    'max': 100,
                    'label': 'CPU Peak Utilization (%)',
                    'description': 'ATX standard: 25% peak CPU utilization for right-sizing'
                },
                'memory_peak_utilization_percent': {
                    'type': 'number',
                    'default': config.RIGHT_SIZING_CONFIG['memory_peak_utilization_percent'],
                    'min': 10,
                    'max': 100,
                    'label': 'Memory Peak Utilization (%)',
                    'description': 'ATX standard: 60% peak memory utilization for right-sizing'
                },
                'storage_utilization_percent': {
                    'type': 'number',
                    'default': config.RIGHT_SIZING_CONFIG['storage_utilization_percent'],
                    'min': 10,
                    'max': 100,
                    'label': 'Storage Utilization (%)',
                    'description': 'ATX standard: 50% storage utilization if data missing'
                }
            }
        },
        'eks': {
            'label': 'EKS Configuration',
            'description': 'Elastic Kubernetes Service migration options',
            'settings': {
                'ENABLE_EKS_ANALYSIS': {
                    'type': 'boolean',
                    'default': config.ENABLE_EKS_ANALYSIS,
                    'label': 'Enable EKS Analysis',
                    'description': 'Include EKS as a migration option (recommended for 50+ small VMs)'
                },
                'strategy': {
                    'type': 'select',
                    'default': config.EKS_CONFIG['strategy'],
                    'options': ['hybrid', 'all-eks', 'disabled'],
                    'label': 'EKS Strategy',
                    'description': 'hybrid = Small VMs to EKS, large VMs to EC2 (recommended)'
                },
                'vcpu_threshold': {
                    'type': 'number',
                    'default': config.EKS_CONFIG['vcpu_threshold'],
                    'min': 1,
                    'max': 16,
                    'label': 'vCPU Threshold',
                    'description': 'VMs with < X vCPU go to EKS in hybrid mode (default: 4)'
                },
                'linux_small_ratio': {
                    'type': 'number',
                    'default': config.EKS_CONFIG['linux_consolidation_ratios']['small'],
                    'min': 1.0,
                    'max': 5.0,
                    'step': 0.1,
                    'label': 'Linux Small Consolidation Ratio',
                    'description': 'Consolidation ratio for small Linux VMs (<4 vCPU). Default: 3.5x'
                },
                'linux_medium_ratio': {
                    'type': 'number',
                    'default': config.EKS_CONFIG['linux_consolidation_ratios']['medium'],
                    'min': 1.0,
                    'max': 4.0,
                    'step': 0.1,
                    'label': 'Linux Medium Consolidation Ratio',
                    'description': 'Consolidation ratio for medium Linux VMs (4-8 vCPU). Default: 2.5x'
                },
                'enable_graviton': {
                    'type': 'boolean',
                    'default': config.EKS_CONFIG['enable_graviton'],
                    'label': 'Enable Graviton for EKS',
                    'description': 'Use ARM-based Graviton instances for EKS worker nodes (20% savings)'
                },
                'spot_enabled': {
                    'type': 'boolean',
                    'default': config.EKS_CONFIG['spot_enabled'],
                    'label': 'Enable Spot Instances',
                    'description': 'Use Spot instances for cost savings (70% discount)'
                },
                'spot_percentage': {
                    'type': 'number',
                    'default': config.EKS_CONFIG['spot_percentage'],
                    'min': 0,
                    'max': 1,
                    'step': 0.05,
                    'label': 'Spot Instance Percentage',
                    'description': 'Percentage of capacity using Spot instances (default: 30%)'
                }
            }
        },
        'backup': {
            'label': 'Backup Configuration',
            'description': 'AWS Backup service configuration and retention policies',
            'settings': {
                'enabled': {
                    'type': 'boolean',
                    'default': config.BACKUP_CONFIG['enabled'],
                    'label': 'Enable Backup Costs',
                    'description': 'Include AWS Backup costs in business case calculations'
                },
                'prod_daily_retention': {
                    'type': 'number',
                    'default': config.BACKUP_CONFIG['production']['daily_retention_days'],
                    'min': 1,
                    'max': 365,
                    'label': 'Production Daily Retention (days)',
                    'description': 'How long to keep daily production backups (default: 7 days)'
                },
                'prod_weekly_retention': {
                    'type': 'number',
                    'default': config.BACKUP_CONFIG['production']['weekly_retention_weeks'],
                    'min': 0,
                    'max': 52,
                    'label': 'Production Weekly Retention (weeks)',
                    'description': 'How long to keep weekly production backups (default: 2 weeks)'
                },
                'prod_monthly_retention': {
                    'type': 'number',
                    'default': config.BACKUP_CONFIG['production']['monthly_retention_months'],
                    'min': 0,
                    'max': 120,
                    'label': 'Production Monthly Retention (months)',
                    'description': 'How long to keep monthly production backups (default: 12 months)'
                },
                'compression_ratio': {
                    'type': 'number',
                    'default': config.BACKUP_CONFIG['compression_ratio'],
                    'min': 0.1,
                    'max': 1.0,
                    'step': 0.05,
                    'label': 'Compression Ratio',
                    'description': 'AWS automatic compression (0.7 = 30% reduction, conservative)'
                },
                'deduplication_ratio': {
                    'type': 'number',
                    'default': config.BACKUP_CONFIG['deduplication_ratio'],
                    'min': 0.1,
                    'max': 1.0,
                    'step': 0.05,
                    'label': 'Deduplication Ratio',
                    'description': '1.0 = No deduplication (AWS does not provide cross-volume dedup)'
                },
                'incremental_ratio': {
                    'type': 'number',
                    'default': config.BACKUP_CONFIG['incremental_ratio'],
                    'min': 0.05,
                    'max': 1.0,
                    'step': 0.05,
                    'label': 'Incremental Backup Ratio',
                    'description': 'Incremental backups as % of full backup (0.2 = 20%, conservative)'
                }
            }
        },
        'data_limits': {
            'label': 'Data Processing Limits',
            'description': 'Maximum rows to process from input files',
            'settings': {
                'MAX_ROWS_RVTOOLS': {
                    'type': 'number',
                    'default': config.MAX_ROWS_RVTOOLS,
                    'min': 100,
                    'max': 10000,
                    'label': 'Max RVTools Rows',
                    'description': 'Maximum VMs to analyze from RVTools export (default: 2500)'
                },
                'MAX_ROWS_IT_INVENTORY': {
                    'type': 'number',
                    'default': config.MAX_ROWS_IT_INVENTORY,
                    'min': 100,
                    'max': 5000,
                    'label': 'Max IT Inventory Rows',
                    'description': 'Maximum rows per sheet in IT inventory (default: 1500)'
                },
                'MAX_ROWS_PORTFOLIO': {
                    'type': 'number',
                    'default': config.MAX_ROWS_PORTFOLIO,
                    'min': 100,
                    'max': 5000,
                    'label': 'Max Portfolio Rows',
                    'description': 'Maximum applications in portfolio (default: 1000)'
                }
            }
        }
    }

def load_overrides() -> Dict[str, Any]:
    """Load user configuration overrides from JSON file."""
    if os.path.exists(OVERRIDE_FILE):
        try:
            with open(OVERRIDE_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config overrides: {e}")
            return {}
    return {}

def save_overrides(overrides: Dict[str, Any]):
    """Save user configuration overrides to JSON file."""
    os.makedirs(os.path.dirname(OVERRIDE_FILE), exist_ok=True)
    with open(OVERRIDE_FILE, 'w') as f:
        json.dump(overrides, f, indent=2)

def get_effective_config() -> Dict[str, Any]:
    """
    Get effective configuration (defaults + overrides).
    Returns flat dictionary of all config values.
    """
    schema = get_config_schema()
    overrides = load_overrides()
    effective = {}
    
    for group_key, group in schema.items():
        effective[group_key] = {}
        for setting_key, setting in group['settings'].items():
            # Use override if exists, otherwise use default
            override_key = f"{group_key}.{setting_key}"
            effective[group_key][setting_key] = overrides.get(override_key, setting['default'])
    
    return effective

def apply_overrides_to_config():
    """
    Apply user overrides to config module.
    Call this at the start of business case generation.
    """
    overrides = load_overrides()
    
    if not overrides:
        return  # No overrides to apply
    
    # Apply each override to the config module
    for key, value in overrides.items():
        if '.' in key:
            # Nested config (e.g., "pricing.pricing_model")
            group, setting = key.split('.', 1)
            
            if group == 'pricing':
                if setting == 'USE_DETERMINISTIC_PRICING':
                    config.USE_DETERMINISTIC_PRICING = value
                elif setting in config.PRICING_CONFIG:
                    config.PRICING_CONFIG[setting] = value
                    
            elif group == 'right_sizing':
                if setting in config.RIGHT_SIZING_CONFIG:
                    config.RIGHT_SIZING_CONFIG[setting] = value
                    
            elif group == 'eks':
                if setting == 'ENABLE_EKS_ANALYSIS':
                    config.ENABLE_EKS_ANALYSIS = value
                elif setting in config.EKS_CONFIG:
                    config.EKS_CONFIG[setting] = value
                elif setting == 'linux_small_ratio':
                    config.EKS_CONFIG['linux_consolidation_ratios']['small'] = value
                elif setting == 'linux_medium_ratio':
                    config.EKS_CONFIG['linux_consolidation_ratios']['medium'] = value
                    
            elif group == 'backup':
                if setting in config.BACKUP_CONFIG:
                    config.BACKUP_CONFIG[setting] = value
                elif setting == 'prod_daily_retention':
                    config.BACKUP_CONFIG['production']['daily_retention_days'] = value
                elif setting == 'prod_weekly_retention':
                    config.BACKUP_CONFIG['production']['weekly_retention_weeks'] = value
                elif setting == 'prod_monthly_retention':
                    config.BACKUP_CONFIG['production']['monthly_retention_months'] = value
                    
            elif group == 'data_limits':
                if setting == 'MAX_ROWS_RVTOOLS':
                    config.MAX_ROWS_RVTOOLS = value
                elif setting == 'MAX_ROWS_IT_INVENTORY':
                    config.MAX_ROWS_IT_INVENTORY = value
                elif setting == 'MAX_ROWS_PORTFOLIO':
                    config.MAX_ROWS_PORTFOLIO = value
