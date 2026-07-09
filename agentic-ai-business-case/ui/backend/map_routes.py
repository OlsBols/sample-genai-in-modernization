"""
MAP Assessment API Routes
Endpoints for MAP assessment features including modernization, migration strategy,
resource planning, learning pathways, business case validation, and architecture diagrams.
"""
from flask import Blueprint, request, jsonify
import os
import sys
import logging
import tempfile
import pandas as pd
import json
import re
import gzip
import requests as http_requests
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from werkzeug.utils import secure_filename
from datetime import datetime
import io
import fitz  # PyMuPDF for PDF processing

# Add project root to Python path
# Get the absolute path to the agentic-ai-business-case directory (two levels up from this file)
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
UI_DIR = os.path.dirname(BACKEND_DIR)
PROJECT_ROOT = os.path.dirname(UI_DIR)  # This is agentic-ai-business-case/

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
    print(f"✓ Added PROJECT_ROOT to sys.path: {PROJECT_ROOT}")

# Import prompt library functions
from prompt_library.modernization_opportunity.inventory_analysis_prompt import get_invventory_analysis_prompt
from prompt_library.modernization_opportunity.onprem_architecture_prompt import get_onprem_architecture_prompt
from prompt_library.modernization_opportunity.modernization_pathways_prompt import get_modernization_pathways_prompt
from prompt_library.migration_patterns.migration_patterns_prompt import get_migration_patterns_prompt
from prompt_library.resource_planning.resource_planning_prompt import get_resource_planning_prompt
from prompt_library.learning_pathway.learning_pathway_prompt import get_learning_pathway_prompt
from prompt_library.business_case_validation.business_case_validation_prompt import get_business_case_validation_prompt
from prompt_library.architecture_diagram.architecture_diagram_prompt import get_architecture_diagram_prompt

# Import utility functions
from utils.bedrock_client import (
    invoke_bedrock_model_with_reasoning,
    invoke_bedrock_model_for_image_analysis,
    invoke_bedrock_model_without_reasoning,
    invoke_bedrock_model_claude_3_5,
    invoke_bedrock_haiku
)
from utils.image_processor import resize_image, convert_image_to_base64, get_image_type
from utils.pdf_processor import convert_pdf_to_images, prepare_content_for_claude
from utils.file_handler import process_pdf_bytes

# Create Blueprint
map_bp = Blueprint('map', __name__, url_prefix='/api/map')

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'jpg', 'jpeg', 'png', 'pdf'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file_size(file):
    """Validate file size"""
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    if size > MAX_FILE_SIZE:
        return False, f"File size exceeds {MAX_FILE_SIZE / (1024*1024)}MB limit"
    return True, "Valid"

# ============================================================================
# MODERNIZATION PATHWAY MAPPING (from AWS modernization pathways)
# Maps normalized service names to their modernization pathway category
# ============================================================================
SERVICE_CODE_TO_PATHWAY = {}
_PATHWAY_SERVICE_KEYS = {
    "Move to AI": [
        "amazon augmented ai", "amazon bedrock", "amazon comprehend", "amazon comprehend medical",
        "amazon forecast", "amazon lex", "amazon personalize", "amazon polly",
        "amazon q developer", "amazon rekognition", "amazon sagemaker",
        "amazon sagemaker ground truth", "amazon textract", "amazon transcribe",
        "amazon transcribe medical", "amazon translate", "amazon bedrock agentcore",
    ],
    "Move to Cloud Native": [
        "aws appsync", "aws lambda", "aws step functions", "amazon api gateway",
        "amazon cognito", "amazon eventbridge", "amazon mq",
        "amazon simple notification service", "amazon simple queue service",
        "awslambda", "amazonapigateway", "amazoncognito", "amazoneventbridge",
        "amazonsqs", "amazonsns", "awsstepfunctions",
    ],
    "Move to Containers": [
        "aws app runner", "aws fargate", "amazon eks", "amazon elastic container registry",
        "amazon ecs", "awseks", "awsfargate", "awsapprunner",
    ],
    "Move to Managed Analytics": [
        "aws glue", "aws lake formation", "amazon appflow", "amazon athena",
        "amazon data firehose", "amazon emr", "amazon healthlake", "amazon kendra",
        "amazon kinesis data streams", "amazon kinesis video streams",
        "amazon managed service for apache flink",
        "amazon managed streaming for apache kafka",
        "amazon managed workflows for apache airflow",
        "amazon opensearch service", "amazon quicksight", "amazon redshift",
        "amazon kinesis",
        "amazonelasticsearchservice", "amazonopensearchservice",
        "amazonredshift", "amazonathena", "awsglue", "amazonmsk",
    ],
    "Move to Managed Databases": [
        "aws database migration service", "amazon aurora",
        "amazon documentdb", "amazon dynamodb", "amazon elasticache",
        "amazon keyspaces", "amazon managed blockchain", "amazon memorydb",
        "amazon neptune", "amazon rds", "amazon timestream",
        "amazonelasticache", "amazondynamodb", "amazonaurora", "amazonneptune",
        "amazondocumentdb", "amazonmemorydb", "amazonrds",
    ],
    "Move to Modern DevOps": [
        "aws amplify", "aws cloudformation", "aws codeartifact", "aws codebuild",
        "aws codedeploy", "aws codepipeline", "aws config", "aws device farm",
        "aws x-ray", "amazon codeguru", "amazon managed service for prometheus",
    ],
}

# Build the lookup: for each pathway, store lowercased service name keys
_PATHWAY_LOOKUP = []
for _pathway_name, _service_names in _PATHWAY_SERVICE_KEYS.items():
    for _svc in _service_names:
        _PATHWAY_LOOKUP.append((_svc.lower().replace(' ', ''), _pathway_name))
# Sort longest first so more specific matches win (e.g. "amazonkinesisdatastreams" before "amazonkinesis")
_PATHWAY_LOOKUP.sort(key=lambda x: len(x[0]), reverse=True)


def classify_service_pathway(service_name):
    """Classify a service into its modernization pathway using normalized name matching.
    
    Special cases:
    - RDS for SQL Server and RDS for Oracle are Non Modern (lift-and-shift, not modernization)
    - Only RDS for MySQL, PostgreSQL, MariaDB are considered managed database modernization
    """
    normalized = service_name.lower().replace(' ', '')
    
    # Special case: RDS for SQL Server and Oracle are NOT modern (lift-and-shift)
    if 'rdsforsql' in normalized or 'rdsfororacle' in normalized:
        return 'Non Modern'
    
    for svc_key, pathway in _PATHWAY_LOOKUP:
        if svc_key in normalized:
            return pathway
    return 'Non Modern'


# Always-excluded service patterns (Data Transfer, Support, Glacier Deep Archive)
EXCLUDED_PATTERNS = {
    'datatransfer': 'data_transfer',
    'data transfer': 'data_transfer',
    'awssupport': 'aws_support',
    'aws support': 'aws_support',
    'glacierdeeparchive': 'glacier_deep_archive',
    'glacier deep archive': 'glacier_deep_archive',
}

# ============================================================================
# EC2 SAVINGS PLANS PRICING HELPERS
# ============================================================================
EC2_PRICING_BASE_URL = 'https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps'
HOURS_PER_MONTH = 730

# European Sovereign Cloud (ESC) configuration
ESC_PRICING_BASE_URL = 'https://artifacts.eusc-de-east-1.prod.plc.billing.a2z.eu/pricing/2.0/meteredUnitMaps/aws-eusc'
ESC_REGION_CODE = 'eusc-de-east-1'
ESC_CURRENCY = 'EUR'
ESC_REGION_NAME = 'AWS European Sovereign Cloud (Germany)'

REGION_CODE_TO_NAME = {
    'us-east-1': 'US East (N. Virginia)',
    'us-east-2': 'US East (Ohio)',
    'us-west-1': 'US West (N. California)',
    'us-west-2': 'US West (Oregon)',
    'eu-central-1': 'EU (Frankfurt)',
    'eu-central-2': 'EU (Zurich)',
    'eu-west-1': 'EU (Ireland)',
    'eu-west-2': 'EU (London)',
    'eu-west-3': 'EU (Paris)',
    'eu-north-1': 'EU (Stockholm)',
    'eu-south-1': 'EU (Milan)',
    'eu-south-2': 'EU (Spain)',
    'ap-south-1': 'Asia Pacific (Mumbai)',
    'ap-south-2': 'Asia Pacific (Hyderabad)',
    'ap-northeast-1': 'Asia Pacific (Tokyo)',
    'ap-northeast-2': 'Asia Pacific (Seoul)',
    'ap-northeast-3': 'Asia Pacific (Osaka)',
    'ap-southeast-1': 'Asia Pacific (Singapore)',
    'ap-southeast-2': 'Asia Pacific (Sydney)',
    'ap-southeast-3': 'Asia Pacific (Jakarta)',
    'ap-southeast-4': 'Asia Pacific (Melbourne)',
    'ap-southeast-5': 'Asia Pacific (Malaysia)',
    'ap-southeast-7': 'Asia Pacific (Thailand)',
    'ca-central-1': 'Canada (Central)',
    'ca-west-1': 'Canada West (Calgary)',
    'sa-east-1': 'South America (Sao Paulo)',
    'ap-east-1': 'Asia Pacific (Hong Kong)',
    'me-south-1': 'Middle East (Bahrain)',
    'me-central-1': 'Middle East (UAE)',
    'af-south-1': 'Africa (Cape Town)',
    'il-central-1': 'Israel (Tel Aviv)',
    'mx-central-1': 'Mexico (Central)',
    'ap-southeast-6': 'Asia Pacific (Taipei)',
    'eusc-de-east-1': 'AWS European Sovereign Cloud (Germany)',
}

# Reverse mapping: display name -> region code (for CSV region column)
REGION_NAME_TO_CODE = {v: k for k, v in REGION_CODE_TO_NAME.items()}


def get_ec2_sp_savings(region_code, instance_type, os_type, quantity, od_cache, sp_cache):
    """Calculate EC2 Savings Plan savings by fetching on-demand and SP rates from AWS.

    Uses od_cache/sp_cache dicts keyed by region_code to avoid redundant API calls.
    Returns dict with savings info or None if no savings available.
    Supports both standard AWS regions and European Sovereign Cloud (ESC).
    """
    region_name = REGION_CODE_TO_NAME.get(region_code)
    if not region_name:
        return None

    is_esc = (region_code == ESC_REGION_CODE)
    base_url = ESC_PRICING_BASE_URL if is_esc else EC2_PRICING_BASE_URL
    currency = ESC_CURRENCY if is_esc else 'USD'

    os_map = {'linux': 'Linux', 'windows': 'Windows'}
    os_name = os_map.get(os_type.lower(), 'Linux')
    family = instance_type.split('.')[0]

    try:
        # --- On-demand rates (cached per region+os) ---
        od_cache_key = f"{region_code}_{os_name}"
        if od_cache_key not in od_cache:
            od_url = f"{base_url}/ec2/{currency}/current/ec2-ondemand-without-sec-sel/{region_name}/{os_name}/index.json"
            od_resp = http_requests.get(od_url, timeout=15)
            od_resp.raise_for_status()
            try:
                od_data = json.loads(gzip.decompress(od_resp.content))
            except Exception:
                od_data = od_resp.json()
            od_cache[od_cache_key] = {
                v['Instance Type']: float(v['price'])
                for v in od_data['regions'][region_name].values()
                if 'Instance Type' in v
            }

        od_rate = od_cache[od_cache_key].get(instance_type)
        if not od_rate:
            return None

        # --- Savings Plans rates - different URL structure for ESC ---
        if is_esc:
            # ESC: uses full instance type, different path, Linux/NA structure
            esc_os = os_name
            esc_sql = 'NA'
            sp_cache_key = f"{region_code}_{os_name}_{instance_type}"
            if sp_cache_key not in sp_cache:
                sp_url = f"{base_url}/computesavingsplan/{currency}/current/compute-instance-savings-plan-ec2-calc/{instance_type}/{region_name}/{esc_os}/{esc_sql}/Shared/index.json"
                sp_resp = http_requests.get(sp_url, timeout=15)
                sp_resp.raise_for_status()
                try:
                    sp_data = json.loads(gzip.decompress(sp_resp.content))
                except Exception:
                    sp_data = sp_resp.json()
                # Filter: EC2 Instance SP (InstanceFamily set), 1yr No Upfront
                sp_cache[sp_cache_key] = {
                    v['ec2:InstanceType']: float(v['price'])
                    for v in sp_data['regions'][region_name].values()
                    if 'ec2:InstanceType' in v
                    and v.get('InstanceFamily')
                    and v.get('PurchaseOption') == 'No Upfront'
                    and v.get('LeaseContractLength') == '1'
                }
        else:
            # Standard AWS: uses family, standard path
            sp_cache_key = f"{region_code}_{os_name}_{family}"
            if sp_cache_key not in sp_cache:
                sp_url = (
                    f"{base_url}/computesavingsplan/{currency}/current/"
                    f"instance-savings-plan-ec2/1%20year/No%20Upfront/"
                    f"{family}/{region_name}/{os_name}/Shared/index.json"
                )
                sp_resp = http_requests.get(sp_url, timeout=15)
                sp_resp.raise_for_status()
                try:
                    sp_data = json.loads(gzip.decompress(sp_resp.content))
                except Exception:
                    sp_data = sp_resp.json()
                sp_cache[sp_cache_key] = {
                    v['ec2:InstanceType']: float(v['price'])
                    for v in sp_data['regions'][region_name].values()
                    if 'ec2:InstanceType' in v
                }

        sp_rate = sp_cache[sp_cache_key].get(instance_type)
        if not sp_rate or sp_rate >= od_rate:
            return None

        monthly_od = od_rate * HOURS_PER_MONTH * quantity
        monthly_sp = sp_rate * HOURS_PER_MONTH * quantity
        monthly_savings = monthly_od - monthly_sp

        if monthly_savings <= 0:
            return None

        return {
            'sp_hourly_rate': round(sp_rate, 5),
            'annual_savings': round(monthly_savings * 12, 2),
            'plan_type': 'EC2 Instance Savings Plan (1yr/No Upfront)',
        }
    except Exception as e:
        logging.warning(f"EC2 SP lookup failed for {instance_type} in {region_code}: {e}")
        return None


# ============================================================================
# SERVICE RI/SP OPTIMIZATION HELPERS (RDS, Redshift, ElastiCache, OpenSearch)
# ============================================================================
_service_od_cache = {}  # {cache_key: {instance_type: price}}
_service_ri_cache = {}  # {cache_key: {instance_type: price}}


def _fetch_pricing_json(url):
    """Fetch and decompress pricing JSON from AWS endpoint."""
    try:
        resp = http_requests.get(url, timeout=15)
        resp.raise_for_status()
        try:
            return json.loads(gzip.decompress(resp.content))
        except Exception:
            return resp.json()
    except Exception as e:
        logging.warning(f"Failed to fetch pricing from {url}: {e}")
        return None


def _get_od_rates(url, region_name, cache_key):
    """Get on-demand rates for a service. Returns {instance_type: hourly_price}."""
    if cache_key in _service_od_cache:
        return _service_od_cache[cache_key]
    data = _fetch_pricing_json(url)
    if not data:
        return {}
    region_data = data.get('regions', {}).get(region_name, {})
    rates = {}
    for k, v in region_data.items():
        inst = v.get('Instance Type') or v.get('instanceType') or v.get('Instance type')
        price = v.get('price')
        if inst and price:
            try:
                rates[inst] = float(price)
            except (ValueError, TypeError):
                pass
    _service_od_cache[cache_key] = rates
    return rates


def _get_ri_rates(url, region_name, cache_key):
    """Get RI rates for a service. Returns {instance_type: hourly_price}."""
    if cache_key in _service_ri_cache:
        return _service_ri_cache[cache_key]
    data = _fetch_pricing_json(url)
    if not data:
        return {}
    region_data = data.get('regions', {}).get(region_name, {})
    rates = {}
    for k, v in region_data.items():
        inst = v.get('Instance Type') or v.get('instanceType') or v.get('Instance type')
        price = v.get('price')
        if inst and price:
            try:
                rates[inst] = float(price)
            except (ValueError, TypeError):
                pass
    _service_ri_cache[cache_key] = rates
    return rates


def get_rds_ri_savings(region_code, instance_type, svc_code, quantity, deployment='single'):
    """Calculate RDS Reserved Instance savings."""
    region_name = REGION_CODE_TO_NAME.get(region_code)
    if not region_name:
        return None

    is_esc = (region_code == ESC_REGION_CODE)
    base = ESC_PRICING_BASE_URL if is_esc else EC2_PRICING_BASE_URL
    currency = ESC_CURRENCY if is_esc else 'USD'

    engine_map = {
        'amazonRDSMySQLDB': 'mysql',
        'amazonRDSPostgreSQLDB': 'postgresql',
        'amazonRDSMariaDB': 'mariadb',
        'amazonRDSForSQLServer': 'sqlserver',
        'amazonAuroraMySQLCompatible': 'mysql',
        'amazonRDSAuroraPostgreSQLCompatibleDB': 'postgresql',
    }
    engine = engine_map.get(svc_code)
    if not engine:
        return None

    try:
        od_url = f"{base}/rds/{currency}/current/rds-{engine}-ondemand.json"
        # RDS on-demand has separate entries for Single-AZ and Multi-AZ
        # Filter by deployment option in the key name
        od_cache_key = f"rds_{engine}_od_{deployment}"
        if od_cache_key not in _service_od_cache:
            od_data = _fetch_pricing_json(od_url)
            if not od_data:
                return None
            region_data = od_data.get('regions', {}).get(region_name, {})
            rates = {}
            deploy_filter = 'Multi' if deployment == 'multi' else 'Single'
            for k, v in region_data.items():
                inst = v.get('Instance Type', '')
                price = v.get('price')
                if inst and price:
                    # Match deployment option in key name, or accept if no deployment info in key
                    if deploy_filter in k or ('Single' not in k and 'Multi' not in k):
                        try:
                            rates[inst] = float(price)
                        except (ValueError, TypeError):
                            pass
            _service_od_cache[od_cache_key] = rates
        od_rates = _service_od_cache[od_cache_key]
        od_rate = od_rates.get(instance_type)
        if not od_rate:
            return None

        az = 'singleaz' if deployment == 'single' else 'multiaz'
        enc_rn = urllib.parse.quote(region_name, safe='')
        if engine == 'mysql':
            ri_url = f"{base}/rds/{currency}/current/rds-mysql-reservedinstance-{az}/{enc_rn}/1%20year/No%20Upfront/index.json"
        elif engine == 'postgresql':
            az_label = 'Single-AZ' if deployment == 'single' else 'Multi-AZ'
            ri_url = f"{base}/rds/{currency}/current/rds-postgresql-reservedinstance/{az_label}/1%20year/No%20Upfront/{enc_rn}/index.json"
        elif engine == 'mariadb':
            ri_url = f"{base}/rds/{currency}/current/rds-mariadb-reservedinstance-{az}/{enc_rn}/index.json"
        elif engine == 'sqlserver':
            az_label = 'Single-AZ' if deployment == 'single' else 'Multi-AZ'
            ri_url = f"{base}/rds/{currency}/current/rds-sqlserver-reservedinstance/{az_label}/1%20year/No%20Upfront/Standard/{enc_rn}/index.json"
        else:
            return None

        ri_rates = _get_ri_rates(ri_url, region_name, f"rds_{engine}_ri_{region_code}_{az}")
        ri_rate, best_instance = _find_best_ri_rate(ri_rates, instance_type, prefix='db.')
        if not ri_rate or ri_rate >= od_rate:
            return None

        monthly_savings = (od_rate - ri_rate) * HOURS_PER_MONTH * quantity
        if monthly_savings <= 0:
            return None

        plan_note = ''
        if best_instance and best_instance != instance_type:
            plan_note = f' (migrate to {best_instance})'

        return {
            'sp_hourly_rate': round(ri_rate, 5),
            'annual_savings': round(monthly_savings * 12, 2),
            'plan_type': f'RDS Reserved Instance (1yr/No Upfront){plan_note}',
        }
    except Exception as e:
        logging.warning(f"RDS RI lookup failed for {instance_type} in {region_code}: {e}")
        return None


def get_redshift_ri_savings(region_code, instance_type, quantity):
    """Calculate Redshift Reserved Node savings."""
    region_name = REGION_CODE_TO_NAME.get(region_code)
    if not region_name:
        return None

    is_esc = (region_code == ESC_REGION_CODE)
    base = ESC_PRICING_BASE_URL if is_esc else EC2_PRICING_BASE_URL
    currency = ESC_CURRENCY if is_esc else 'USD'

    try:
        od_url = f"{base}/redshift/{currency}/current/redshift.json"
        od_rates = _get_od_rates(od_url, region_name, "redshift_od")
        od_rate = od_rates.get(instance_type)
        if not od_rate:
            return None

        # ESC uses /Yes/ which returns all instance types — can find Graviton equivalents
        if is_esc:
            enc_rn = urllib.parse.quote(region_name, safe='')
            ri_url = f"{base}/redshift/{currency}/current/redshift-reservedinstance/{enc_rn}/1%20year/No%20Upfront/Yes/index.json"
            ri_rates = _get_ri_rates(ri_url, region_name, f"redshift_ri_{region_code}_all")
            ri_rate, best_instance = _find_best_ri_rate(ri_rates, instance_type, prefix='')
        else:
            # Standard AWS: try Graviton equivalent first, then current instance
            ri_rate = None
            best_instance = instance_type
            # Try Graviton equivalent
            fam_match = re.match(r'^([a-z]+)(\d+)([a-z]*)\.(.+)$', instance_type, re.IGNORECASE)
            if fam_match:
                fam_letter, fam_gen, fam_spec, size = fam_match.groups()
                if fam_spec != 'g':
                    graviton_inst = f"{fam_letter}{fam_gen}g.{size}"
                    grav_ri_url = f"{base}/redshift/{currency}/current/redshift-reservedinstance/{region_name}/1%20year/No%20Upfront/{graviton_inst}/index.json"
                    grav_ri_rates = _get_ri_rates(grav_ri_url, region_name, f"redshift_ri_{region_code}_{graviton_inst}")
                    grav_rate = grav_ri_rates.get(graviton_inst)
                    if grav_rate:
                        ri_rate = grav_rate
                        best_instance = graviton_inst
            # Try current instance if Graviton not found
            if not ri_rate:
                ri_url = f"{base}/redshift/{currency}/current/redshift-reservedinstance/{region_name}/1%20year/No%20Upfront/{instance_type}/index.json"
                ri_rates = _get_ri_rates(ri_url, region_name, f"redshift_ri_{region_code}_{instance_type}")
                ri_rate = ri_rates.get(instance_type)
                best_instance = instance_type

        if not ri_rate or ri_rate >= od_rate:
            return None

        monthly_savings = (od_rate - ri_rate) * HOURS_PER_MONTH * quantity
        if monthly_savings <= 0:
            return None

        plan_note = ''
        if best_instance and best_instance != instance_type:
            plan_note = f' (migrate to {best_instance})'

        return {
            'sp_hourly_rate': round(ri_rate, 5),
            'annual_savings': round(monthly_savings * 12, 2),
            'plan_type': f'Redshift Reserved Node (1yr/No Upfront){plan_note}',
        }
    except Exception as e:
        logging.warning(f"Redshift RI lookup failed for {instance_type} in {region_code}: {e}")
        return None


def get_elasticache_ri_savings(region_code, instance_type, quantity, engine='Redis'):
    """Calculate ElastiCache Reserved Node savings."""
    region_name = REGION_CODE_TO_NAME.get(region_code)
    if not region_name:
        return None

    is_esc = (region_code == ESC_REGION_CODE)
    base = ESC_PRICING_BASE_URL if is_esc else EC2_PRICING_BASE_URL
    currency = ESC_CURRENCY if is_esc else 'USD'

    try:
        # ElastiCache on-demand has multiple entries per instance type (one per engine)
        # Need to filter by engine in the key name
        od_url = f"{base}/elasticache/{currency}/current/elasticache.json"
        od_cache_key = f"elasticache_od_{engine}"
        if od_cache_key not in _service_od_cache:
            od_data = _fetch_pricing_json(od_url)
            if not od_data:
                return None
            region_data = od_data.get('regions', {}).get(region_name, {})
            rates = {}
            engine_lower = engine.lower()
            for k, v in region_data.items():
                inst = v.get('Instance Type', '')
                price = v.get('price')
                # Filter by engine in the key name
                if inst and price and engine_lower in k.lower():
                    try:
                        rates[inst] = float(price)
                    except (ValueError, TypeError):
                        pass
            _service_od_cache[od_cache_key] = rates
        od_rates = _service_od_cache[od_cache_key]
        od_rate = od_rates.get(instance_type)
        if not od_rate:
            return None
            return None

        enc_rn = urllib.parse.quote(region_name, safe='')
        ri_url = f"{base}/elasticache/{currency}/current/elasticache-reservedinstance/1%20year/No%20Upfront/{enc_rn}/Standard/{engine}/index.json"
        ri_rates = _get_ri_rates(ri_url, region_name, f"elasticache_ri_{region_code}_{engine}")
        ri_rate, best_instance = _find_best_ri_rate(ri_rates, instance_type, prefix='cache.')
        if not ri_rate or ri_rate >= od_rate:
            return None

        monthly_savings = (od_rate - ri_rate) * HOURS_PER_MONTH * quantity
        if monthly_savings <= 0:
            return None

        plan_note = ''
        if best_instance and best_instance != instance_type:
            plan_note = f' (migrate to {best_instance})'

        return {
            'sp_hourly_rate': round(ri_rate, 5),
            'annual_savings': round(monthly_savings * 12, 2),
            'plan_type': f'ElastiCache Reserved Node (1yr/No Upfront){plan_note}',
        }
    except Exception as e:
        logging.warning(f"ElastiCache RI lookup failed for {instance_type} in {region_code}: {e}")
        return None


def get_opensearch_ri_savings(region_code, instance_type, quantity):
    """Calculate OpenSearch Reserved Instance savings."""
    region_name = REGION_CODE_TO_NAME.get(region_code)
    if not region_name:
        return None

    is_esc = (region_code == ESC_REGION_CODE)
    base = ESC_PRICING_BASE_URL if is_esc else EC2_PRICING_BASE_URL
    currency = ESC_CURRENCY if is_esc else 'USD'

    try:
        if is_esc:
            # ESC uses es.json combined file — no Instance Type field, pricing info in key names
            # On-demand: key contains "OnDemand" and instance type with spaces (e.g. "c7g 12xlarge.search")
            # RI: key contains "No Upfront - 1yr - Hourly Cost"
            combined_url = f"{base}/es/{currency}/current/es.json"
            combined_cache_key = f"opensearch_esc_combined_{region_code}"
            if combined_cache_key not in _service_od_cache:
                combined_data = _fetch_pricing_json(combined_url)
                if not combined_data:
                    return None
                region_data = combined_data.get('regions', {}).get(region_name, {})
                od = {}
                ri = {}
                for k, v in region_data.items():
                    price = v.get('price', '0')
                    try:
                        price_f = float(price)
                    except (ValueError, TypeError):
                        continue
                    if price_f <= 0:
                        continue
                    # Extract instance type from key: "c7g 12xlarge.search - ..."
                    # Convert spaces to dots for matching: "c7g 12xlarge.search" -> "c7g.12xlarge.search"
                    parts = k.split(' - ')
                    if len(parts) >= 2:
                        raw_inst = parts[0].strip().replace(' ', '.')
                        if 'OnDemand' in k and 'Hourly Cost' in k:
                            od[raw_inst] = price_f
                        elif 'No Upfront' in k and '1yr' in k and 'Hourly Cost' in k:
                            ri[raw_inst] = price_f
                _service_od_cache[combined_cache_key] = {'od': od, 'ri': ri}

            cached = _service_od_cache[combined_cache_key]
            od_rate = cached['od'].get(instance_type)
            # Find best Graviton RI rate from combined file
            ri_rate, best_instance = _find_best_ri_rate(cached['ri'], instance_type, prefix='')
            if not od_rate or not ri_rate or ri_rate >= od_rate:
                return None
        else:
            od_url = f"{base}/es/{currency}/current/es-ondemand.json"
            od_rates = _get_od_rates(od_url, region_name, "opensearch_od")
            od_rate = od_rates.get(instance_type)
            if not od_rate:
                return None

            enc_rn = urllib.parse.quote(region_name, safe='')
            ri_url = f"{base}/es/{currency}/current/es-reservedinstance/1%20year/No%20Upfront/{enc_rn}/Standard/index.json"
            ri_rates = _get_ri_rates(ri_url, region_name, f"opensearch_ri_{region_code}")
            ri_rate, best_instance = _find_best_ri_rate(ri_rates, instance_type, prefix='')
            if not ri_rate or ri_rate >= od_rate:
                return None

        monthly_savings = (od_rate - ri_rate) * HOURS_PER_MONTH * quantity
        if monthly_savings <= 0:
            return None

        plan_note = ''
        if best_instance and best_instance != instance_type:
            plan_note = f' (migrate to {best_instance})'

        return {
            'sp_hourly_rate': round(ri_rate, 5),
            'annual_savings': round(monthly_savings * 12, 2),
            'plan_type': f'OpenSearch Reserved Instance (1yr/No Upfront){plan_note}',
        }
    except Exception as e:
        logging.warning(f"OpenSearch RI lookup failed for {instance_type} in {region_code}: {e}")
        return None


# Service codes eligible for RI optimization lookup
SERVICE_RI_LOOKUP = {
    'amazonRDSMySQLDB': get_rds_ri_savings,
    'amazonRDSPostgreSQLDB': get_rds_ri_savings,
    'amazonRDSMariaDB': get_rds_ri_savings,
    'amazonRDSForSQLServer': get_rds_ri_savings,
    'amazonAuroraMySQLCompatible': get_rds_ri_savings,
    'amazonRDSAuroraPostgreSQLCompatibleDB': get_rds_ri_savings,
    'amazonRedshift': get_redshift_ri_savings,
    'amazonElastiCache': get_elasticache_ri_savings,
    'amazonElasticsearchService': get_opensearch_ri_savings,
}

# RDS service codes that need the engine parameter
RDS_SERVICE_CODES = {
    'amazonRDSMySQLDB', 'amazonRDSPostgreSQLDB', 'amazonRDSMariaDB',
    'amazonRDSForSQLServer', 'amazonAuroraMySQLCompatible',
    'amazonRDSAuroraPostgreSQLCompatibleDB',
}

# EBS pricing URLs
EBS_PRICING_URL = 'https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/ec2/USD/current/ebs.json'
ESC_EBS_PRICING_URL = 'https://artifacts.eusc-de-east-1.prod.plc.billing.a2z.eu/pricing/2.0/meteredUnitMaps/aws-eusc/ec2/EUR/current/ebs-calculator.json'

# io2 supported regions
IO2_SUPPORTED_REGIONS = {
    'US East (Ohio)', 'US East (N. Virginia)', 'US West (N. California)', 'US West (Oregon)',
    'Asia Pacific (Hong Kong)', 'Asia Pacific (Mumbai)', 'Asia Pacific (Seoul)',
    'Asia Pacific (Singapore)', 'Asia Pacific (Sydney)', 'Asia Pacific (Tokyo)',
    'Canada (Central)', 'Europe (Frankfurt)', 'Europe (Ireland)', 'Europe (London)',
    'Europe (Stockholm)', 'Middle East (Bahrain)', 'AWS European Sovereign Cloud (Germany)',
}

_ebs_pricing_cache = {}


def _get_ebs_prices(region_code):
    """Fetch EBS pricing for a region. Returns dict of price keys to prices."""
    if region_code in _ebs_pricing_cache:
        return _ebs_pricing_cache[region_code]

    is_esc = (region_code == ESC_REGION_CODE)
    url = ESC_EBS_PRICING_URL if is_esc else EBS_PRICING_URL
    region_name = REGION_CODE_TO_NAME.get(region_code)
    if not region_name:
        return {}

    data = _fetch_pricing_json(url)
    if not data:
        return {}

    region_data = data.get('regions', {}).get(region_name, {})
    prices = {}
    for k, v in region_data.items():
        price = v.get('price')
        if price:
            try:
                prices[k] = float(price)
            except (ValueError, TypeError):
                pass
    _ebs_pricing_cache[region_code] = prices
    return prices


def calculate_ebs_savings(storage_amount, storage_type, iops, region_code, quantity, svc_code):
    """Calculate EBS storage optimization savings (gp2→gp3, io1→io2).
    
    Returns dict with savings info or None.
    """
    region_name = REGION_CODE_TO_NAME.get(region_code, '')
    prices = _get_ebs_prices(region_code)
    if not prices:
        return None

    try:
        if 'gp2' in storage_type.lower():
            gp2_price = prices.get('Storage General Purpose gp2 GB Mo')
            gp3_price = prices.get('Storage General Purpose gp3 GB Mo')
            gp3_iops_price = prices.get('Provisioned EBS IOPS gp3 Volumes per IOPS Mo')
            gp3_thr_price = prices.get('Provisioned Throughput gp3 per GiBps mo')

            if not all([gp2_price, gp3_price, gp3_iops_price, gp3_thr_price]):
                return None

            # gp2 baseline IOPS: min(max(100, storage*3), 16000)
            gp2_baseline_iops = min(max(100, storage_amount * 3), 16000)
            # gp2 baseline throughput: min(gp2_iops * 256/1024, 250) MB/s
            gp2_baseline_thr = round(min(gp2_baseline_iops * (256 / 1024), 250))

            # gp3 provisioned IOPS above 3000 baseline
            gp3_extra_iops = max(3000, gp2_baseline_iops) - 3000
            # gp3 provisioned throughput above 125 MB/s baseline
            gp3_extra_thr = max(125, gp2_baseline_thr) - 125

            # For RDS, gp3 minimum IOPS is 12000 and throughput is 500
            if svc_code in RDS_SERVICE_CODES:
                gp3_extra_iops = max(12000, gp3_extra_iops)
                gp3_extra_thr = max(500, gp3_extra_thr)

            gp2_cost = storage_amount * gp2_price
            gp3_cost = (storage_amount * gp3_price +
                        gp3_extra_iops * gp3_iops_price +
                        (gp3_extra_thr / 1024) * gp3_thr_price)

            monthly_savings = max(0, quantity * (gp2_cost - gp3_cost))
            if monthly_savings <= 0:
                return None

            return {
                'annual_savings': round(monthly_savings * 12, 2),
                'plan_type': 'EBS gp2 → gp3 migration',
                'detail': f'{storage_amount} GB gp2 → gp3 (saves {round(monthly_savings, 2)}/mo)',
            }

        elif 'io1' in storage_type.lower():
            # io1→io2 only in supported regions and for EC2 only
            if region_name not in IO2_SUPPORTED_REGIONS:
                return None
            if svc_code not in ('ec2Enhancement',):
                return None

            storage_price = prices.get('Storage Provisioned IOPS GB Mo') or prices.get('Storage Provisioned IOPS io1 GB Mo')
            io1_iops_price = prices.get('Provisioned EBS IOPS io1 Volumes per IOPS Mo')
            io2_tier1_price = prices.get('Provisioned EBS IOPS io2 Volumes per IOPS Mo')
            io2_tier2_price = prices.get('Provisioned EBS IOPS Tier 2 io2 Volumes per IOPS Mo')
            io2_tier3_price = prices.get('Provisioned EBS IOPS Tier 3 io2 Volumes per IOPS Mo')

            if not all([storage_price, io1_iops_price, io2_tier1_price, io2_tier2_price, io2_tier3_price]):
                return None

            if not iops or iops <= 0:
                return None

            io1_cost = storage_price * storage_amount + iops * io1_iops_price

            # io2 tiered IOPS pricing
            tier1_limit = 32000
            tier2_limit = 64000
            io2_iops_cost = (min(iops, tier1_limit) * io2_tier1_price +
                             max(0, min(iops, tier2_limit) - tier1_limit) * io2_tier2_price +
                             max(0, iops - tier2_limit) * io2_tier3_price)
            io2_cost = storage_price * storage_amount + io2_iops_cost

            monthly_savings = max(0, quantity * (io1_cost - io2_cost))
            if monthly_savings <= 0:
                return None

            return {
                'annual_savings': round(monthly_savings * 12, 2),
                'plan_type': 'EBS io1 → io2 migration',
                'detail': f'{storage_amount} GB io1 → io2, {iops} IOPS (saves {round(monthly_savings, 2)}/mo)',
            }
    except Exception as e:
        logging.warning(f"EBS savings calculation failed: {e}")

    return None


def _run_ebs_optimization(raw_services):
    """Check all services for EBS storage optimization opportunities (gp2→gp3, io1→io2)."""
    ebs_found = 0
    for svc in raw_services:
        cfg = svc.get('config_summary', '')
        region_code = svc.get('_ec2_region', '') or svc.get('region', '')

        # Try _ebs_* fields first (from URL endpoint's calculationComponents)
        ebs_type = svc.get('_ebs_storage_type', '')
        ebs_amount = svc.get('_ebs_storage_amount', 0)
        ebs_iops = svc.get('_ebs_storage_iops', 0)

        # Detect storage type
        storage_type = ''
        if ebs_type:
            if 'general purpose' in ebs_type.lower() and 'gp3' not in ebs_type.lower():
                storage_type = 'gp2'
            elif 'io1' in ebs_type.lower() or 'provisioned iops' in ebs_type.lower():
                storage_type = 'io1'
        
        # Fallback: check configSummary
        if not storage_type:
            if 'gp2' in cfg.lower():
                storage_type = 'gp2'
            elif 'io1' in cfg.lower():
                storage_type = 'io1'

        if not storage_type:
            continue

        # Get storage amount
        storage_amount = int(ebs_amount) if ebs_amount else 0
        if not storage_amount:
            storage_match = re.search(r'(?:Storage amount|EBS Storage amount|Storage for each.*instance) \((\d+)', cfg)
            if not storage_match:
                storage_match = re.search(r'(\d+)\s*GB', cfg)
            if storage_match:
                storage_amount = int(storage_match.group(1))
        if storage_amount <= 0:
            continue

        # Get IOPS for io1
        iops = int(ebs_iops) if ebs_iops else 0
        if not iops and storage_type == 'io1':
            iops_match = re.search(r'(?:IOPS|Provisioned IOPS) \((\d+)', cfg)
            if iops_match:
                iops = int(iops_match.group(1))

        if not region_code or not REGION_CODE_TO_NAME.get(region_code):
            continue

        # Get quantity
        qty_match = re.search(r'(?:Nodes|Number of instances|Quantity) \((\d+)\)', cfg)
        quantity = int(qty_match.group(1)) if qty_match else 1

        result = calculate_ebs_savings(storage_amount, storage_type, iops, region_code, quantity, svc['service_code'])
        if result:
            svc['ebs_savings'] = result['annual_savings']
            svc['ebs_plan_type'] = result['plan_type']
            svc['ebs_detail'] = result['detail']


def _run_ri_optimization(raw_services, use_region_code=True):
    """Run RI optimization for RDS, Redshift, ElastiCache, OpenSearch services."""
    ri_tasks = []
    for idx, svc in enumerate(raw_services):
        sc = svc['service_code']
        if sc not in SERVICE_RI_LOOKUP:
            continue
        if svc.get('ec2_sp_annual_savings', 0) > 0:
            continue

        cfg = svc.get('config_summary', '')
        inst_match = re.search(r'Instance [Tt]ype \(([^)]+)\)', cfg)
        if not inst_match:
            inst_match = re.search(r'Node [Tt]ype \(([^)]+)\)', cfg)
        if not inst_match:
            continue

        instance_type = inst_match.group(1).strip()

        # Check if on-demand — multiple patterns in configSummary
        # IMPORTANT: Check Pricing strategy/Pricing Model FIRST — if Reserved/SP, skip
        pricing_match = re.search(r'Pricing strategy \(([^)]+)\)', cfg)
        pricing_model_match = re.search(r'Pricing Model \(([^)]+)\)', cfg)
        
        is_ondemand = True  # default assumption
        
        # If Pricing Model is set (Aurora, etc.), check it first
        if pricing_model_match:
            model = pricing_model_match.group(1).strip().lower()
            if 'reserved' in model or 'savings' in model:
                is_ondemand = False
        
        # If Pricing strategy is set (RDS, Redshift, etc.), check it
        if pricing_match:
            strategy = pricing_match.group(1).strip().lower()
            if 'reserved' in strategy or 'savings' in strategy:
                is_ondemand = False
            elif 'on-demand' in strategy or 'ondemand' in strategy:
                is_ondemand = True
        
        # Utilization field can say "On-Demand only" even when pricing is Reserved
        # Only use it as a fallback if no pricing strategy/model was found
        if not pricing_match and not pricing_model_match:
            util_match = re.search(r'Utilization \(([^)]+)\)', cfg)
            if util_match and 'on-demand' in util_match.group(1).lower():
                is_ondemand = True
        
        if not is_ondemand:
            continue

        # Extract quantity — try Nodes first (for Redshift/ElastiCache/OpenSearch), then others
        qty_match = re.search(r'Nodes \((\d+)\)', cfg)
        if not qty_match:
            qty_match = re.search(r'(?:Quantity|Number of nodes|Number of instances) \((\d+)\)', cfg)
        quantity = int(qty_match.group(1)) if qty_match else 1

        # Extract engine for ElastiCache
        engine = 'Redis'
        engine_match = re.search(r'Cache Engine \(([^)]+)\)', cfg)
        if engine_match:
            engine = engine_match.group(1).strip()

        # Extract deployment option for RDS (Multi-AZ vs Single-AZ)
        deployment = 'single'
        deploy_match = re.search(r'Deployment option \(([^)]+)\)', cfg)
        if deploy_match and 'multi' in deploy_match.group(1).lower():
            deployment = 'multi'

        if use_region_code:
            region_code = svc.get('_ec2_region', '') or svc.get('region', '')
        else:
            region_display = svc.get('region', '')
            region_code = REGION_NAME_TO_CODE.get(region_display, '')
            if not region_code:
                for rname, rcode in REGION_NAME_TO_CODE.items():
                    if rname in region_display or region_display in rname:
                        region_code = rcode
                        break

        if not region_code or not REGION_CODE_TO_NAME.get(region_code):
            continue

        ri_tasks.append((idx, sc, region_code, instance_type, quantity, engine, deployment))

    def _lookup_ri(task):
        idx, sc, region_code, instance_type, quantity, engine, deployment = task
        lookup_fn = SERVICE_RI_LOOKUP[sc]
        if sc in RDS_SERVICE_CODES:
            result = lookup_fn(region_code, instance_type, sc, quantity, deployment)
        elif sc == 'amazonElastiCache':
            result = lookup_fn(region_code, instance_type, quantity, engine)
        else:
            result = lookup_fn(region_code, instance_type, quantity)
        return idx, result

    if ri_tasks:
        with ThreadPoolExecutor(max_workers=min(len(ri_tasks), 10)) as executor:
            futures = {executor.submit(_lookup_ri, t): t for t in ri_tasks}
            for future in as_completed(futures):
                try:
                    idx, ri_result = future.result()
                    if ri_result:
                        raw_services[idx]['ec2_sp_annual_savings'] = ri_result['annual_savings']
                        raw_services[idx]['ec2_sp_hourly_rate'] = ri_result['sp_hourly_rate']
                        raw_services[idx]['ec2_sp_plan_type'] = ri_result['plan_type']
                except Exception as e:
                    logging.warning(f"RI lookup failed: {e}", exc_info=True)


def _get_fargate_sp_savings(svc, is_esc=False):
    """Calculate Fargate Compute Savings Plan savings for a single service.

    Fetches on-demand and 1yr/No Upfront Compute SP rates from AWS pricing
    endpoints, then computes the annual savings.

    Returns dict with savings info or None on failure / no savings.
    """
    region_code = svc.get('_fargate_region', '')
    region_name = REGION_CODE_TO_NAME.get(region_code)
    if not region_name:
        return None

    os_raw = svc.get('_fargate_os', 'linux')
    arch_raw = svc.get('_fargate_arch', 'x86')
    duration = svc.get('_fargate_duration', 730)
    vcpu = svc.get('_fargate_vcpu', 1)
    tasks = svc.get('_fargate_tasks', 1)
    memory = svc.get('_fargate_memory', 2)

    os_name = 'Windows' if 'windows' in str(os_raw).lower() else 'Linux'
    arch_name = 'ARM' if 'arm' in str(arch_raw).lower() else 'X86'

    base_url = ESC_PRICING_BASE_URL if is_esc else EC2_PRICING_BASE_URL
    currency = ESC_CURRENCY if is_esc else 'USD'

    try:
        # --- On-demand rates ---
        od_cache_key = f"fargate_od_{region_code}"
        if od_cache_key not in _service_od_cache:
            od_url = f"{base_url}/ecs/{currency}/current/ecs.json"
            od_data = _fetch_pricing_json(od_url)
            if not od_data:
                return None
            region_data = od_data.get('regions', {}).get(region_name, {})
            _service_od_cache[od_cache_key] = region_data
        region_data = _service_od_cache[od_cache_key]

        # Find on-demand CPU and memory rates
        od_cpu_rate = None
        od_gb_rate = None
        for k, v in region_data.items():
            price = v.get('price')
            if not price:
                continue
            kl = k.lower()
            if arch_name == 'ARM':
                if 'arm percpu per hour' in kl and 'windows' not in kl:
                    od_cpu_rate = float(price)
                elif 'arm pergb per hour' in kl and 'windows' not in kl:
                    od_gb_rate = float(price)
            elif os_name == 'Windows':
                if 'percpu per hour windows' in kl and 'arm' not in kl and 'license' not in kl:
                    od_cpu_rate = float(price)
                elif 'pergb per hour windows' in kl and 'arm' not in kl:
                    od_gb_rate = float(price)
            else:
                # x86 Linux: match entries WITHOUT 'arm', 'windows', 'license'
                if 'percpu per hour' in kl and 'arm' not in kl and 'windows' not in kl and 'license' not in kl:
                    od_cpu_rate = float(price)
                elif 'pergb per hour' in kl and 'arm' not in kl and 'windows' not in kl:
                    od_gb_rate = float(price)
                    od_gb_rate = float(price)

        if od_cpu_rate is None or od_gb_rate is None:
            logging.warning(f"Fargate OD rates not found for {region_code}, OS={os_name}, Arch={arch_name}. od_cpu={od_cpu_rate}, od_gb={od_gb_rate}")
            return None

        # --- Compute SP rates (1yr / No Upfront) ---
        arch_path = 'ARM' if arch_name == 'ARM' else 'X86'
        sp_cache_key = f"fargate_sp_{region_code}_{os_name}_{arch_path}"
        if sp_cache_key not in _service_od_cache:
            sp_url = (
                f"{base_url}/computesavingsplan/{currency}/current/"
                f"compute-savings-plan-fargate-with-arm/1%20year/No%20Upfront/"
                f"{region_name}/{os_name}/{arch_path}/index.json"
            )
            sp_data = _fetch_pricing_json(sp_url)
            if not sp_data:
                logging.warning(f"Fargate SP pricing fetch failed. URL: {sp_url}")
                return None
            sp_region_data = sp_data.get('regions', {}).get(region_name, {})
            _service_od_cache[sp_cache_key] = sp_region_data
        sp_region_data = _service_od_cache[sp_cache_key]

        sp_cpu_rate = None
        sp_gb_rate = None
        for k, v in sp_region_data.items():
            price = v.get('price')
            if not price:
                continue
            kl = k.lower()
            if 'percpu' in kl:
                sp_cpu_rate = float(price)
            elif 'pergb' in kl:
                sp_gb_rate = float(price)

        if sp_cpu_rate is None or sp_gb_rate is None:
            logging.warning(f"Fargate SP rates not found for {region_code}, OS={os_name}, Arch={arch_path}. sp_cpu={sp_cpu_rate}, sp_gb={sp_gb_rate}")
            return None

        # --- Calculate savings ---
        od_cost = (od_cpu_rate * vcpu * duration + od_gb_rate * memory * duration) * tasks
        sp_cost = (sp_cpu_rate * vcpu * duration + sp_gb_rate * memory * duration) * tasks
        monthly_savings = od_cost - sp_cost

        if monthly_savings <= 0:
            return None

        return {
            'annual_savings': round(monthly_savings * 12, 2),
            'plan_type': 'Compute Savings Plan (1yr/No Upfront)',
            'od_cpu_rate': od_cpu_rate,
            'od_gb_rate': od_gb_rate,
            'sp_cpu_rate': sp_cpu_rate,
            'sp_gb_rate': sp_gb_rate,
            'od_monthly': round(od_cost, 2),
            'sp_monthly': round(sp_cost, 2),
            'vcpu': vcpu,
            'memory': memory,
            'tasks': tasks,
            'duration': duration,
        }
    except Exception as e:
        logging.warning(f"Fargate SP lookup failed for {region_code}: {e}")
        return None


def _get_graviton_savings(svc, od_cache):
    """Calculate Graviton savings for an EC2 instance by comparing on-demand rates.

    Looks up the Graviton equivalent instance type and computes the annual
    cost difference.  Uses the same od_cache populated by EC2 SP optimization.

    Returns dict with savings info or None on failure / no savings.
    """
    instance_type = svc.get('_graviton_instance_type')
    region_code = svc.get('_graviton_region', '')
    current_instance = svc.get('_graviton_current_instance', '')
    if not instance_type or not region_code or not current_instance:
        return None

    region_name = REGION_CODE_TO_NAME.get(region_code)
    if not region_name:
        return None

    is_esc = (region_code == ESC_REGION_CODE)
    base_url = ESC_PRICING_BASE_URL if is_esc else EC2_PRICING_BASE_URL
    currency = ESC_CURRENCY if is_esc else 'USD'

    # Determine OS from the service
    os_type = svc.get('_ec2_os', 'linux')
    os_map = {'linux': 'Linux', 'windows': 'Windows'}
    os_name = os_map.get(os_type.lower(), 'Linux')

    try:
        od_cache_key = f"{region_code}_{os_name}"
        if od_cache_key not in od_cache:
            od_url = f"{base_url}/ec2/{currency}/current/ec2-ondemand-without-sec-sel/{region_name}/{os_name}/index.json"
            od_data = _fetch_pricing_json(od_url)
            if not od_data:
                return None
            od_cache[od_cache_key] = {
                v['Instance Type']: float(v['price'])
                for v in od_data.get('regions', {}).get(region_name, {}).values()
                if 'Instance Type' in v and v.get('price')
            }

        rates = od_cache[od_cache_key]
        current_rate = rates.get(current_instance)
        graviton_rate = rates.get(instance_type)

        if current_rate is None or graviton_rate is None:
            return None
        if graviton_rate >= current_rate:
            return None

        quantity = svc.get('_ec2_quantity', 1)
        annual_savings = round((current_rate - graviton_rate) * HOURS_PER_MONTH * quantity * 12, 2)

        if annual_savings <= 0:
            return None

        return {
            'annual_savings': annual_savings,
            'graviton_instance': instance_type,
        }
    except Exception as e:
        logging.warning(f"Graviton lookup failed for {current_instance}->{instance_type} in {region_code}: {e}")
        return None


def _add_advisory_notes(raw_services, od_cache=None, is_esc=False):
    """Add Fargate Compute SP savings and Graviton savings to services.

    For Fargate services: fetches real on-demand and Compute SP pricing to
    calculate exact annual savings.

    For EC2 services with non-Graviton instances: looks up the Graviton
    equivalent on-demand rate and calculates the annual savings.

    Advisory notes are always set regardless of whether pricing lookups succeed.
    """
    if od_cache is None:
        od_cache = {}

    fargate_tasks = []
    graviton_tasks = []

    for idx, svc in enumerate(raw_services):
        sc = svc['service_code']
        cfg = svc.get('config_summary', '')

        # --- Fargate: calculate Compute SP savings ---
        if sc == 'awsFargate':
            # Default note — will be enriched with calculation details after SP lookup
            svc['optimization_note'] = (
                'Fargate Spot and Compute Savings Plans are currently not supported on the AWS Pricing Calculator. '
                'Please calculate baseline Fargate costs first, then manually apply the appropriate Savings Plan '
                'discount rates and adjust the usage quantities in the calculator to reflect the net costs after savings.'
            )
            # Only attempt pricing if we have Fargate fields
            if svc.get('_fargate_region'):
                fargate_tasks.append(idx)

        # --- Graviton: calculate actual savings ---
        inst_match = re.search(r'(?:Instance type|Advance EC2 instance|Node type) \(([^)]+)\)', cfg)
        if inst_match:
            inst = inst_match.group(1).strip()
            if inst and '.' in inst:
                family = inst.split('.')[0]
                size = inst.split('.', 1)[1]
                # Skip if already Graviton (family ends with 'g' or 'gd' or 'gn')
                if family.endswith('g') or family.endswith('gd') or family.endswith('gn'):
                    continue
                # Extract numeric generation from family
                # e.g. m6i -> prefix='m', gen='6', suffix='i' -> graviton: m6g
                # e.g. r5 -> prefix='r', gen='5', suffix='' -> graviton: r5g
                # e.g. c5a -> prefix='c', gen='5', suffix='a' -> graviton: c5g
                gen_match = re.match(r'^([a-z]+)(\d+)([a-z]*)$', family, re.IGNORECASE)
                if gen_match:
                    fam_prefix = gen_match.group(1)
                    fam_gen = gen_match.group(2)
                    graviton_family = f"{fam_prefix}{fam_gen}g"
                    graviton_instance = f"{graviton_family}.{size}"
                    svc['_graviton_instance_type'] = graviton_instance
                    svc['_graviton_current_instance'] = inst
                    svc['_graviton_region'] = svc.get('_ec2_region', '') or svc.get('region', '')
                    # Always set advisory note
                    svc['graviton_note'] = (
                        f'Consider migrating from {inst} to Graviton-based {graviton_family} family '
                        f'for up to 20% better price-performance.'
                    )
                    if svc.get('_graviton_region'):
                        graviton_tasks.append(idx)

    # --- Parallel Fargate SP lookups ---
    def _lookup_fargate(idx):
        return idx, _get_fargate_sp_savings(raw_services[idx], is_esc=is_esc)

    if fargate_tasks:
        with ThreadPoolExecutor(max_workers=min(len(fargate_tasks), 10)) as executor:
            futures = {executor.submit(_lookup_fargate, i): i for i in fargate_tasks}
            for future in as_completed(futures):
                try:
                    idx, result = future.result()
                    if result:
                        raw_services[idx]['ec2_sp_annual_savings'] = result['annual_savings']
                        raw_services[idx]['ec2_sp_plan_type'] = result['plan_type']
                        # Enrich the note with calculation example
                        r = result
                        currency_sym = '€' if is_esc else '$'
                        raw_services[idx]['optimization_note'] = (
                            'Fargate Spot and Compute Savings Plans are currently not supported on the AWS Pricing Calculator. '
                            'Please calculate baseline Fargate costs first, then manually apply the appropriate Savings Plan '
                            'discount rates and adjust the usage quantities in the calculator to reflect the net costs after savings.\n\n'
                            'Calculation example for this service:\n'
                            f'  On-Demand rates: {currency_sym}{r["od_cpu_rate"]:.4f}/vCPU-hr, {currency_sym}{r["od_gb_rate"]:.6f}/GB-hr\n'
                            f'  Compute SP rates (1yr No Upfront): {currency_sym}{r["sp_cpu_rate"]:.4f}/vCPU-hr, {currency_sym}{r["sp_gb_rate"]:.6f}/GB-hr\n'
                            f'  Configuration: {r["vcpu"]:.0f} vCPU, {r["memory"]:.0f} GB memory, {r["tasks"]:.0f} tasks, {r["duration"]:.0f} hrs/month\n\n'
                            f'  On-Demand monthly cost: {currency_sym}{r["od_monthly"]:,.2f}\n'
                            f'  Compute SP monthly cost: {currency_sym}{r["sp_monthly"]:,.2f}\n'
                            f'  Annual savings: {currency_sym}{r["annual_savings"]:,.2f}\n\n'
                            'How to reflect this in the calculator:\n'
                            f'  Discount factor: {currency_sym}{r["sp_monthly"]:,.2f} / {currency_sym}{r["od_monthly"]:,.2f} = {r["sp_monthly"] / r["od_monthly"]:.4f}\n'
                            f'  Adjusted tasks: {r["tasks"]:.0f} tasks x {r["sp_monthly"] / r["od_monthly"]:.4f} = {r["tasks"] * r["sp_monthly"] / r["od_monthly"]:.2f} tasks\n'
                            f'  Or adjusted duration: {r["duration"]:.0f} hrs x {r["sp_monthly"] / r["od_monthly"]:.4f} = {r["duration"] * r["sp_monthly"] / r["od_monthly"]:.0f} hrs/month\n\n'
                            f'  Update the calculator with either the adjusted task count or duration to show the effective SP cost of {currency_sym}{r["sp_monthly"]:,.2f}/month '
                            f'instead of the on-demand cost of {currency_sym}{r["od_monthly"]:,.2f}/month.'
                        )
                except Exception as e:
                    logging.warning(f"Fargate SP future failed: {e}")

    # --- Parallel Graviton lookups ---
    def _lookup_graviton(idx):
        return idx, _get_graviton_savings(raw_services[idx], od_cache)

    if graviton_tasks:
        with ThreadPoolExecutor(max_workers=min(len(graviton_tasks), 10)) as executor:
            futures = {executor.submit(_lookup_graviton, i): i for i in graviton_tasks}
            for future in as_completed(futures):
                try:
                    idx, result = future.result()
                    if result:
                        raw_services[idx]['graviton_savings'] = result['annual_savings']
                        raw_services[idx]['graviton_note'] = (
                            f'Consider migrating from {raw_services[idx]["_graviton_current_instance"]} '
                            f'to Graviton-based {result["graviton_instance"]} — '
                            f'estimated annual savings: ${result["annual_savings"]:,.2f}.'
                        )
                except Exception as e:
                    logging.warning(f"Graviton future failed: {e}")


# ============================================================================
# MODERNIZATION OPPORTUNITY ENDPOINTS
# ============================================================================

@map_bp.route('/modernization/analyze-inventory', methods=['POST'])
def analyze_inventory():
    """Analyze IT inventory data"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        
        file = request.files['file']
        if not file or not allowed_file(file.filename):
            return jsonify({'success': False, 'message': 'Invalid file type'}), 400
        
        # Validate file size
        is_valid, error_msg = validate_file_size(file)
        if not is_valid:
            return jsonify({'success': False, 'message': error_msg}), 400
        
        # Read CSV data
        try:
            inventory_df = pd.read_csv(file)
            csv_text = inventory_df.to_string()
        except Exception as e:
            logging.error(f"Error reading CSV: {e}")
            return jsonify({'success': False, 'message': 'Error reading CSV file'}), 400
        
        # Check for custom prompt
        custom_prompt = request.form.get('custom_prompt')
        
        if custom_prompt:
            # Use custom prompt, replace placeholder with CSV data
            prompt = custom_prompt.replace('{inventory_csv}', csv_text)
            # Also try without placeholder if not found
            if '{inventory_csv}' not in custom_prompt:
                prompt = f"{custom_prompt}\n\nIT Inventory Data:\n{csv_text}"
        else:
            # Use default prompt
            prompt = get_invventory_analysis_prompt(inventory_df)
        
        # Generate analysis
        result = invoke_bedrock_model_with_reasoning(prompt)
        
        return jsonify({
            'success': True,
            'analysis': result['response'],
            'reasoning': result.get('reasoning', ''),
            'inventoryRecords': len(inventory_df),
            'usedCustomPrompt': bool(custom_prompt)
        })
        
    except Exception as e:
        logging.error(f"Inventory analysis failed: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500

@map_bp.route('/modernization/analyze-architecture', methods=['POST'])
def analyze_architecture():
    """Analyze on-premises architecture from image"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        
        file = request.files['file']
        if not file or not allowed_file(file.filename):
            return jsonify({'success': False, 'message': 'Invalid file type'}), 400
        
        # Validate file size
        is_valid, error_msg = validate_file_size(file)
        if not is_valid:
            return jsonify({'success': False, 'message': error_msg}), 400
        
        # Process image
        image_bytes = file.read()
        image_bytes = resize_image(image_bytes)
        encoded_image = convert_image_to_base64(image_bytes)
        image_type = get_image_type(file.filename)
        
        # Generate analysis
        prompt = get_onprem_architecture_prompt()
        arch_description = invoke_bedrock_model_for_image_analysis(
            encoded_image, prompt, image_type
        )
        
        return jsonify({
            'success': True,
            'analysis': arch_description
        })
        
    except Exception as e:
        logging.error(f"Architecture analysis failed: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500

@map_bp.route('/modernization/recommend-pathways', methods=['POST'])
def recommend_pathways():
    """Generate modernization pathway recommendations"""
    try:
        data = request.json
        
        if 'inventoryData' not in data:
            return jsonify({'success': False, 'message': 'Inventory data required'}), 400
        
        # Convert inventory data back to DataFrame
        inventory_df = pd.DataFrame(data['inventoryData'])
        scope_text = data.get('scope', '')
        architecture_description = data.get('architectureDescription', None)
        
        # Generate recommendations
        prompt = get_modernization_pathways_prompt(
            inventory_df, architecture_description, scope_text
        )
        result = invoke_bedrock_model_with_reasoning(prompt)
        
        return jsonify({
            'success': True,
            'recommendations': result['response'],
            'reasoning': result.get('reasoning', '')
        })
        
    except Exception as e:
        logging.error(f"Modernization pathways failed: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500

# ============================================================================
# MIGRATION STRATEGY ENDPOINTS
# ============================================================================

@map_bp.route('/migration-strategy/generate', methods=['POST'])
def generate_migration_strategy():
    """Generate migration strategy from AWS Calculator data"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        
        file = request.files['file']
        if not file or not allowed_file(file.filename):
            return jsonify({'success': False, 'message': 'Invalid file type'}), 400
        
        # Validate file size
        is_valid, error_msg = validate_file_size(file)
        if not is_valid:
            return jsonify({'success': False, 'message': error_msg}), 400
        
        # Parse AWS Calculator CSV
        csv_data = file.read().decode('utf-8')
        lines = csv_data.splitlines()
        
        # Find the start of the detailed estimate section
        # Look for common headers in English or German
        start_idx = 0
        header_patterns = [
            "Group hierarchy,Region,Description",
            "Gruppenhierarchie,Region,Beschreibung",
            "Group hierarchy",
            "Gruppenhierarchie"
        ]
        
        for i, line in enumerate(lines):
            if any(pattern in line for pattern in header_patterns):
                start_idx = i
                break
        
        # Read CSV with error handling for malformed lines
        try:
            calc_df = pd.read_csv(
                io.StringIO("\n".join(lines[start_idx:])), 
                encoding="utf-8",
                on_bad_lines='skip',  # Skip malformed lines
                quoting=1  # QUOTE_ALL to handle embedded commas
            )
        except Exception as e:
            # Fallback: try with different settings
            try:
                calc_df = pd.read_csv(
                    io.StringIO("\n".join(lines[start_idx:])), 
                    encoding="utf-8",
                    on_bad_lines='skip',
                    error_bad_lines=False
                )
            except:
                # Last resort: read with minimal parsing
                calc_df = pd.read_csv(
                    io.StringIO("\n".join(lines[start_idx:])), 
                    encoding="utf-8",
                    on_bad_lines='skip',
                    quoting=3  # QUOTE_NONE
                )
        
        # Get scope text
        scope_text = request.form.get('scope', '')
        
        # Check for custom prompt
        custom_prompt = request.form.get('custom_prompt')
        
        if custom_prompt:
            # Use custom prompt, replace placeholders
            services_summary = calc_df.to_string()
            prompt = custom_prompt.replace('{services_summary}', services_summary)
            prompt = prompt.replace('{scope_text}', scope_text if scope_text else '')
            # Also try without placeholders if not found
            if '{services_summary}' not in custom_prompt:
                prompt = f"{custom_prompt}\n\nAWS Calculator Data:\n{services_summary}\n\nScope: {scope_text}"
        else:
            # Use default prompt
            prompt = get_migration_patterns_prompt(calc_df, scope_text)
        
        # Generate strategy
        strategy_text = invoke_bedrock_model_without_reasoning(prompt)
        
        return jsonify({
            'success': True,
            'strategy': strategy_text,
            'recordsProcessed': len(calc_df),
            'usedCustomPrompt': bool(custom_prompt)
        })
        
    except Exception as e:
        logging.error(f"Migration strategy generation failed: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500

# ============================================================================
# RESOURCE PLANNING ENDPOINTS
# ============================================================================

@map_bp.route('/resource-planning/generate', methods=['POST'])
def generate_resource_planning():
    """Generate resource planning recommendations"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        
        file = request.files['file']
        if not file or not allowed_file(file.filename):
            return jsonify({'success': False, 'message': 'Invalid file type'}), 400
        
        # Validate file size
        is_valid, error_msg = validate_file_size(file)
        if not is_valid:
            return jsonify({'success': False, 'message': error_msg}), 400
        
        # Read resource profile CSV
        resource_df = pd.read_csv(file)
        
        # Get additional context
        migration_strategy = request.form.get('migrationStrategy', '')
        wave_planning = request.form.get('wavePlanning', '')
        
        # Check for custom prompt
        custom_prompt = request.form.get('custom_prompt')
        
        if custom_prompt:
            # Use custom prompt, replace placeholders
            resource_details = resource_df.to_string()
            prompt = custom_prompt.replace('{migration_strategy}', migration_strategy)
            prompt = prompt.replace('{wave_planning_data}', wave_planning)
            prompt = prompt.replace('{resource_details}', resource_details)
            # Also try without placeholders if not found
            if '{resource_details}' not in custom_prompt:
                prompt = f"{custom_prompt}\n\nResource Details:\n{resource_details}\n\nMigration Strategy:\n{migration_strategy}\n\nWave Planning:\n{wave_planning}"
        else:
            # Use default prompt
            prompt = get_resource_planning_prompt(resource_df, migration_strategy, wave_planning)
        
        # Generate resource plan
        result = invoke_bedrock_model_with_reasoning(prompt)
        
        return jsonify({
            'success': True,
            'resourcePlan': result['response'],
            'reasoning': result.get('reasoning', ''),
            'usedCustomPrompt': bool(custom_prompt)
        })
        
    except Exception as e:
        logging.error(f"Resource planning failed: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500

# ============================================================================
# LEARNING PATHWAY ENDPOINTS
# ============================================================================

@map_bp.route('/learning-pathway/generate', methods=['POST'])
def generate_learning_pathway():
    """Generate personalized learning pathway"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        
        file = request.files['file']
        if not file or not allowed_file(file.filename):
            return jsonify({'success': False, 'message': 'Invalid file type'}), 400
        
        # Validate file size
        is_valid, error_msg = validate_file_size(file)
        if not is_valid:
            return jsonify({'success': False, 'message': error_msg}), 400
        
        # Read training data CSV
        training_df = pd.read_csv(file)
        
        # Get parameters
        target_role = request.form.get('targetRole', '')
        experience_level = request.form.get('experienceLevel', '')
        duration = request.form.get('duration', '')
        
        # Check for custom prompt
        custom_prompt = request.form.get('custom_prompt')
        
        if custom_prompt:
            # Use custom prompt, replace placeholders
            training_data = training_df.to_string()
            prompt = custom_prompt.replace('{training_data}', training_data)
            prompt = prompt.replace('{target_role}', target_role)
            prompt = prompt.replace('{target_experience}', experience_level)
            prompt = prompt.replace('{learning_duration}', duration)
            # Also try without placeholders if not found
            if '{training_data}' not in custom_prompt:
                prompt = f"{custom_prompt}\n\nTraining Data:\n{training_data}\n\nTarget Role: {target_role}\nExperience Level: {experience_level}\nDuration: {duration}"
        else:
            # Use default prompt
            prompt = get_learning_pathway_prompt(training_df, target_role, experience_level, duration)
        
        # Generate learning pathway
        result = invoke_bedrock_model_with_reasoning(prompt)
        
        return jsonify({
            'success': True,
            'learningPathway': result['response'],
            'reasoning': result.get('reasoning', ''),
            'usedCustomPrompt': bool(custom_prompt)
        })
        
    except Exception as e:
        logging.error(f"Learning pathway generation failed: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500

# ============================================================================
# BUSINESS CASE VALIDATION ENDPOINTS
# ============================================================================

@map_bp.route('/business-validation/validate', methods=['POST'])
def validate_business_case():
    """Validate business case document"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        
        file = request.files['file']
        if not file or not allowed_file(file.filename):
            return jsonify({'success': False, 'message': 'Invalid file type'}), 400
        
        # Validate file size
        is_valid, error_msg = validate_file_size(file)
        if not is_valid:
            return jsonify({'success': False, 'message': error_msg}), 400
        
        # Process PDF - read bytes directly from Flask file object
        max_pages = 10
        pdf_bytes = file.read()
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        page_images = convert_pdf_to_images(pdf_document, max_pages)
        pdf_document.close()
        
        # Check for custom prompt
        custom_prompt = request.form.get('custom_prompt')
        
        if custom_prompt:
            # Use custom prompt
            prompt = custom_prompt
        else:
            # Use default prompt
            prompt = get_business_case_validation_prompt()
        
        # Prepare content for Claude with images
        pdf_content_with_prompt = prepare_content_for_claude(page_images, prompt)
        
        # Generate validation
        validation_result = invoke_bedrock_model_without_reasoning(pdf_content_with_prompt)
        
        return jsonify({
            'success': True,
            'validation': validation_result,
            'pagesProcessed': len(page_images),
            'usedCustomPrompt': bool(custom_prompt)
        })
        
    except Exception as e:
        logging.error(f"Business case validation failed: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500

# ============================================================================
# ARCHITECTURE DIAGRAM ENDPOINTS
# ============================================================================

@map_bp.route('/architecture-diagram/generate', methods=['POST'])
def generate_architecture_diagram():
    """Generate AWS architecture diagram in Draw.io XML format"""
    try:
        data = request.json
        
        if 'description' not in data:
            return jsonify({'success': False, 'message': 'Architecture description required'}), 400
        
        description = data['description']
        custom_prompt = data.get('custom_prompt')
        
        if custom_prompt:
            # Use custom prompt, replace placeholder
            prompt = custom_prompt.replace('{description}', description)
            # Also try without placeholder if not found
            if '{description}' not in custom_prompt:
                prompt = f"{custom_prompt}\n\nArchitecture Description:\n{description}"
        else:
            # Use default prompt
            prompt = get_architecture_diagram_prompt(description)
        
        # Generate diagram
        diagram_xml = invoke_bedrock_model_without_reasoning(prompt)
        
        return jsonify({
            'success': True,
            'diagramXml': diagram_xml,
            'usedCustomPrompt': bool(custom_prompt)
        })
        
    except Exception as e:
        logging.error(f"Architecture diagram generation failed: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500

# ============================================================================
# CHAT ASSISTANT ENDPOINTS
# ============================================================================

@map_bp.route('/chat/message', methods=['POST'])
def chat_message():
    """Process chat message with context"""
    try:
        data = request.json
        
        if 'message' not in data:
            return jsonify({'success': False, 'message': 'Message required'}), 400
        
        user_message = data['message']
        context = data.get('context', {})
        chat_history = data.get('history', [])
        context_type = context.get('type', 'general')
        context_data = context.get('data', '')
        
        # Build system prompt based on context type
        system_prompts = {
            'general': "You are an AWS migration and modernization expert. Provide clear, actionable guidance on AWS cloud migration strategies, best practices, and solutions.",
            'modernization': "You are an AWS modernization specialist. Help analyze modernization opportunities, containerization strategies, and cloud-native transformations. Focus on practical recommendations based on the provided analysis.",
            'migration-strategy': "You are an AWS migration strategist specializing in the 6Rs framework (Rehost, Replatform, Repurchase, Refactor, Retire, Retain). Provide strategic guidance on migration approaches and wave planning.",
            'resource-planning': "You are an AWS resource planning expert. Help with team structure, skill requirements, timeline planning, and resource allocation for cloud migration projects.",
            'learning-pathway': "You are an AWS training and certification advisor. Guide users through learning paths, certification roadmaps, and skill development strategies for cloud migration teams.",
            'business-case': "You are an AWS business case analyst. Help review and discuss business case details, ROI calculations, cost analysis, and business value propositions for cloud migration.",
            'architecture': "You are an AWS solutions architect. Provide guidance on AWS architecture patterns, service selection, design best practices, and technical implementation details.",
            'service-analysis': "You are an AWS infrastructure completeness expert. Help analyze service gaps, identify missing infrastructure components across 6 critical categories (Backup, Storage, DR/HA, Network, Observability, Security), and provide specific recommendations to ensure production-ready, well-architected solutions. Focus on the production-ready benchmark of 56% compute / 44% non-compute infrastructure.",
            'ola-analysis': "You are an AWS licensing optimization expert. Help analyze Windows Server, SQL Server, and Oracle licensing strategies. Explain BYOL vs License Included options, Software Assurance requirements, Microsoft October 2019 licensing changes, Dedicated Hosts vs shared EC2, RDS alternatives, and Oracle Database@AWS (Exadata). Provide ARR impact analysis and OLA engagement recommendations. Focus on cost optimization while ensuring license compliance.",
            'knowledge-base': "You are an AWS documentation expert with access to comprehensive AWS knowledge. Search and provide accurate information from AWS documentation, whitepapers, best practices, and official guidance. Always cite sources when possible."
        }
        
        system_prompt = system_prompts.get(context_type, system_prompts['general'])
        
        # Build context string
        context_str = f"System: {system_prompt}\n\n"
        
        if context_data:
            context_str += f"Context Data from {context_type}:\n{context_data}\n\n"
        
        # Add conversation history
        history_str = ""
        if chat_history:
            history_str = "Conversation History:\n"
            for msg in chat_history[-5:]:  # Last 5 messages
                role = "User" if msg['role'] == 'user' else "Assistant"
                history_str += f"{role}: {msg['content']}\n"
            history_str += "\n"
        
        # Build full prompt
        full_prompt = f"{context_str}{history_str}User: {user_message}\n\nAssistant:"
        
        # For knowledge-base context, add instruction to search AWS documentation
        if context_type == 'knowledge-base':
            full_prompt = f"{context_str}{history_str}User Question: {user_message}\n\nPlease provide a comprehensive answer based on AWS documentation, best practices, and official guidance. Include specific AWS service recommendations and implementation details where relevant.\n\nAssistant:"
        
        # Get response
        response = invoke_bedrock_model_without_reasoning(full_prompt)
        
        if not response:
            return jsonify({'success': False, 'message': 'No response from model. Please try again.'}), 500
        
        return jsonify({
            'success': True,
            'response': response,
            'contextType': context_type
        })
        
    except Exception as e:
        logging.error(f"Chat message processing failed: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500

# ============================================================================
# SERVICE ANALYSIS ENDPOINTS
# ============================================================================

@map_bp.route('/service-analysis/analyze', methods=['POST'])
def analyze_service_completeness():
    """Analyze AWS Calculator CSV for calculator review and infrastructure gaps"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        
        file = request.files['file']
        if not file or not allowed_file(file.filename):
            return jsonify({'success': False, 'message': 'Invalid file type'}), 400
        
        # Validate file size
        is_valid, error_msg = validate_file_size(file)
        if not is_valid:
            return jsonify({'success': False, 'message': error_msg}), 400
        
        # Parse AWS Calculator CSV
        csv_data = file.read().decode('utf-8')
        lines = csv_data.splitlines()
        
        # Find the start of the detailed estimate section
        start_idx = 0
        header_patterns = [
            "Group hierarchy,Region,Description",
            "Gruppenhierarchie,Region,Beschreibung",
            "Group hierarchy",
            "Gruppenhierarchie"
        ]
        
        for i, line in enumerate(lines):
            if any(pattern in line for pattern in header_patterns):
                start_idx = i
                break
        
        # Read CSV with error handling
        try:
            calc_df = pd.read_csv(
                io.StringIO("\n".join(lines[start_idx:])), 
                encoding="utf-8",
                on_bad_lines='skip',
                quoting=1
            )
        except Exception as e:
            try:
                calc_df = pd.read_csv(
                    io.StringIO("\n".join(lines[start_idx:])), 
                    encoding="utf-8",
                    on_bad_lines='skip',
                    quoting=3
                )
            except:
                return jsonify({'success': False, 'message': 'Failed to parse CSV file'}), 400
        
        # Get custom prompt (the comprehensive service analysis prompt)
        custom_prompt = request.form.get('custom_prompt')
        
        if not custom_prompt:
            return jsonify({'success': False, 'message': 'Analysis prompt required'}), 400
        
        # Prepare the data summary for analysis
        services_summary = calc_df.to_string()
        
        # Build the full prompt with CSV data
        full_prompt = f"{custom_prompt}\n\n**AWS Calculator CSV Data:**\n\n{services_summary}"
        
        # Generate analysis using Bedrock (Haiku for speed)
        try:
            analysis_result = invoke_bedrock_haiku(full_prompt)
        except Exception as bedrock_err:
            logging.error(f"Bedrock call failed: {bedrock_err}")
            return jsonify({'success': False, 'message': 'AI analysis failed. Check backend logs for details.'}), 500
        
        if not analysis_result:
            return jsonify({'success': False, 'message': 'AI analysis failed. Please try again.'}), 500
        
        return jsonify({
            'success': True,
            'analysis': analysis_result,
            'recordsProcessed': len(calc_df)
        })
        
    except Exception as e:
        logging.error(f"Service analysis failed: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500


# ============================================================================
# AWS Calculator URL-based analysis helpers
# ============================================================================
CALC_CLOUDFRONT_URL = 'https://d3knqfixx3sbls.cloudfront.net/{}'
CALC_ESC_URL = 'https://pricing.calculator.aws.eu/getSavedEstimates/{}'
CALC_MANIFEST_URL = 'https://d3knqfixx3sbls.cloudfront.net/manifest.json'
FULL_TIME_HOURS_PER_WEEK = 168

# Built-in service code to display name mapping
SERVICE_DISPLAY_NAMES = {
    'ec2Enhancement': 'Amazon EC2',
    'amazonVirtualPrivateCloud': 'Amazon Virtual Private Cloud (VPC)',
    'dataTransferVpc': 'Data Transfer',
    'publicIpv4Address': 'Amazon Virtual Private Cloud (VPC)',
    'networkAddressTranslationNatGatewayVpc': 'Amazon Virtual Private Cloud (VPC)',
    'transitGatewayVpc': 'Amazon Virtual Private Cloud (VPC)',
    'awsKeyManagementService': 'AWS Key Management Service',
    'awsCloudTrail': 'AWS CloudTrail',
    'amazonCloudWatch': 'Amazon CloudWatch',
    'awsSystemsManagerAutomation': 'AWS Systems Manager',
    'aWSStorageGateway': 'AWS Storage Gateway',
    'amazonCloudFront': 'Amazon CloudFront',
    'awsWebApplicationFirewall': 'AWS Web Application Firewall (WAF)',
    'awsSecretsManager': 'AWS Secrets Manager',
    'applicationLoadBalancer': 'Elastic Load Balancing',
    'networkLoadBalancer': 'Elastic Load Balancing',
    'amazonS3Standard': 'Amazon Simple Storage Service (S3)',
    'awsS3DataTransfer': 'Amazon Simple Storage Service (S3)',
    'amazonRDSMySQLDB': 'Amazon RDS for MySQL',
    'amazonRDSPostgreSQLDB': 'Amazon RDS for PostgreSQL',
    'amazonRDSMariaDB': 'Amazon RDS for MariaDB',
    'amazonRDSForSQLServer': 'Amazon RDS for SQL Server',
    'amazonRDSAuroraPostgreSQLCompatibleDB': 'Amazon Aurora PostgreSQL-Compatible',
    'amazonAuroraMySQLCompatible': 'Amazon Aurora MySQL-Compatible',
    'amazonElastiCache': 'Amazon ElastiCache',
    'amazonEFS': 'Amazon Elastic File System (EFS)',
    'amazonDynamoDB': 'Amazon DynamoDB',
    'amazonDynamoDbOnDemand': 'Amazon DynamoDB',
    'awsFargate': 'AWS Fargate',
    'awsEks': 'Amazon EKS',
    'amazonElasticContainerRegistry': 'Amazon Elastic Container Registry',
    'aWSLambda': 'AWS Lambda',
    'amazonApiGateway': 'Amazon API Gateway',
    'amazonSageMaker': 'Amazon SageMaker',
    'amazonBedrock': 'Amazon Bedrock',
    'amazonRedshift': 'Amazon Redshift',
    'amazonElasticsearchService': 'Amazon OpenSearch Service',
    'amazonOpenSearchService': 'Amazon OpenSearch Service',
    'amazonKinesisDataStreams': 'Amazon Kinesis Data Streams',
    'amazonKinesisFirehose': 'Amazon Data Firehose',
    'amazonManagedStreamingForApacheKafkaMsk': 'Amazon MSK',
    'awsGlue': 'AWS Glue',
    'amazonAthena': 'Amazon Athena',
    'amazonCognito': 'Amazon Cognito',
    'amazonEventBridge': 'Amazon EventBridge',
    'amazonSimpleQueueService': 'Amazon SQS',
    'amazonSimpleNotificationService': 'Amazon SNS',
    'awsStepFunctions': 'AWS Step Functions',
    'amazonRoute53': 'Amazon Route 53',
    'awsConfig': 'AWS Config',
    'amazonGuardDuty': 'Amazon GuardDuty',
    'awsShield': 'AWS Shield',
    'amazonMQ': 'Amazon MQ',
    'awsCodeBuild': 'AWS CodeBuild',
    'awsCodePipeline': 'AWS CodePipeline',
    'amazonNeptune': 'Amazon Neptune',
    'amazonDocumentDB': 'Amazon DocumentDB',
    'amazonMemoryDbForRedis': 'Amazon MemoryDB',
    'amazonTimestream': 'Amazon Timestream',
    'awsAppRunner': 'AWS App Runner',
    'awsAmplify': 'AWS Amplify',
    'amazonS3GlacierDeepArhive': 'Amazon S3 Glacier Deep Archive',
    'AWSDeveloperSupport': 'AWS Developer Support',
    'AWSSupportBusiness': 'AWS Business Support',
    'AWSSupportEnterprise': 'AWS Enterprise Support',
    'AWSEnterpriseOnRamp': 'AWS Enterprise On-Ramp Support',
    'amazonSimpleStorageServiceGroup': 'Amazon Simple Storage Service (S3)',
}

# Services whose cost should always be excluded (data transfer, not MAP eligible)
ALWAYS_EXCLUDE_DT_SERVICES = {
    'dataTransferVpc', 'networkAddressTranslationNatGatewayVpc',
    'awsS3DataTransfer',
}

# Data transfer and CloudFront pricing URLs (public, no auth needed)
DT_PRICING_URL = 'https://calculator.aws/pricing/2.0/meteredUnitMaps/datatransfer/USD/current/datatransfer-calc.json'
ESC_DT_PRICING_URL = 'https://artifacts.eusc-de-east-1.prod.plc.billing.a2z.eu/pricing/2.0/meteredUnitMaps/aws-eusc/datatransfer/EUR/current/datatransfer-calc.json'
CF_PRICING_URL = 'https://calculator.aws/pricing/2.0/meteredUnitMaps/cloudfront/USD/current/cloudfront.json'

# Caches for pricing data (loaded once per process)
_dt_pricing_cache = None
_esc_dt_pricing_cache = None
_cf_pricing_cache = None


def _load_dt_pricing(is_esc=False):
    """Load data transfer pricing from public AWS pricing endpoint. Cached per process."""
    global _dt_pricing_cache, _esc_dt_pricing_cache
    if is_esc:
        if _esc_dt_pricing_cache is not None:
            return _esc_dt_pricing_cache
        try:
            resp = http_requests.get(ESC_DT_PRICING_URL, timeout=15)
            resp.raise_for_status()
            _esc_dt_pricing_cache = resp.json()
            return _esc_dt_pricing_cache
        except Exception as e:
            logging.warning(f"Failed to load ESC DT pricing: {e}")
            return {}
    else:
        if _dt_pricing_cache is not None:
            return _dt_pricing_cache
        try:
            resp = http_requests.get(DT_PRICING_URL, timeout=15)
            resp.raise_for_status()
            _dt_pricing_cache = resp.json()
            return _dt_pricing_cache
        except Exception as e:
            logging.warning(f"Failed to load DT pricing: {e}")
            return {}


def _load_cf_pricing():
    """Load CloudFront pricing from public AWS pricing endpoint. Cached per process."""
    global _cf_pricing_cache
    if _cf_pricing_cache is not None:
        return _cf_pricing_cache
    try:
        resp = http_requests.get(CF_PRICING_URL, timeout=15)
        resp.raise_for_status()
        _cf_pricing_cache = resp.json()
        return _cf_pricing_cache
    except Exception as e:
        logging.warning(f"Failed to load CF pricing: {e}")
        return {}


# CloudFront calculator field suffix to region name mapping
CF_CALC_REGION_MAP = {
    '_US': 'United States', '_Canada': 'Canada', '_AP': 'Asia Pacific',
    '_Australia': 'Australia', '_EU': 'EU', '_India': 'India',
    '_Japan': 'Japan', '_ME': 'Middle East', '_SA': 'South Africa',
    '_SouthAmerica': 'South America',
}

# CloudFront tiers (in GB)
CF_TIERS = [
    ('First 10 TB', 0, 10240),
    ('Next 40 TB', 10240, 51200),
    ('next 100 TB', 51200, 153600),
    ('Next 350 TB', 153600, 512000),
    ('next 524 TB', 512000, 1048576),
    ('Next 4 PB', 1048576, 5242880),
    ('Over 5 PB', 5242880, float('inf')),
]

# Cache for service manifest
_service_manifest_cache = None

def _load_service_manifest():
    global _service_manifest_cache
    if _service_manifest_cache is not None:
        return _service_manifest_cache
    try:
        resp = http_requests.get(CALC_MANIFEST_URL, timeout=15)
        resp.raise_for_status()
        _service_manifest_cache = resp.json()
        return _service_manifest_cache
    except Exception as e:
        logging.warning(f"Failed to load service manifest: {e}")
        return []

def _get_service_name(service_code, manifest):
    """Get display name for a service code. Uses built-in mapping first, then manifest."""
    # Try built-in mapping first (manifest is not publicly accessible)
    if service_code in SERVICE_DISPLAY_NAMES:
        return SERVICE_DISPLAY_NAMES[service_code]
    # Fallback to manifest lookup
    for svc in manifest:
        if svc.get('serviceCode') == service_code:
            return svc.get('name', service_code)
    return service_code

def _find_best_ri_rate(ri_rates, instance_type, prefix='db.'):
    """Find the best (cheapest) RI rate for an instance type, including Graviton equivalents.
    
    For managed services, Graviton instances offer better price-performance with no
    application changes needed. This function finds the cheapest matching instance
    across same family letter, same size, same or newer generation.
    
    e.g. db.m5.4xlarge matches: db.m5.4xlarge, db.m6g.4xlarge, db.m7g.4xlarge
    e.g. cache.r6g.xlarge matches: cache.r6g.xlarge, cache.r7g.xlarge
    """
    # Parse the current instance type
    clean = instance_type.replace(prefix, '')
    parts = clean.split('.')
    if len(parts) != 2:
        # Try without prefix (for OpenSearch: c7g.12xlarge.search)
        parts = instance_type.split('.')
        if len(parts) < 2:
            return ri_rates.get(instance_type), instance_type
    
    family = parts[0]
    size = '.'.join(parts[1:])  # Handle multi-dot sizes like "12xlarge.search"
    
    # Extract family letter, generation, spec from family
    # e.g. m5 -> letter=m, gen=5, spec=''
    # e.g. m6g -> letter=m, gen=6, spec='g'
    # e.g. r6i -> letter=r, gen=6, spec='i'
    fam_match = re.match(r'^([a-z]+)(\d+)([a-z]*)$', family, re.IGNORECASE)
    if not fam_match:
        return ri_rates.get(instance_type), instance_type
    
    fam_letter = fam_match.group(1)
    fam_gen = int(fam_match.group(2))
    fam_spec = fam_match.group(3)
    
    # Find all matching instances in RI rates
    best_rate = None
    best_instance = None
    
    for ri_inst, ri_price in ri_rates.items():
        ri_clean = ri_inst.replace(prefix, '')
        ri_parts = ri_clean.split('.')
        if len(ri_parts) < 2:
            ri_parts = ri_inst.split('.')
            if len(ri_parts) < 2:
                continue
        
        ri_family = ri_parts[0]
        ri_size = '.'.join(ri_parts[1:])
        
        # Size must match exactly
        if ri_size != size:
            continue
        
        ri_fam_match = re.match(r'^([a-z]+)(\d+)([a-z]*)$', ri_family, re.IGNORECASE)
        if not ri_fam_match:
            continue
        
        ri_letter = ri_fam_match.group(1)
        ri_gen = int(ri_fam_match.group(2))
        ri_spec = ri_fam_match.group(3)
        
        # Family letter must match
        if ri_letter != fam_letter:
            continue
        
        # Generation must be same or newer
        if ri_gen < fam_gen:
            continue
        
        # Accept: same spec, or Graviton (spec='g') when current has no spec or different spec
        if ri_spec == fam_spec or ri_spec == 'g' or (ri_spec == '' and fam_spec == ''):
            if best_rate is None or ri_price < best_rate:
                best_rate = ri_price
                best_instance = ri_inst
    
    return best_rate, best_instance



    """Recursively find all OUTBOUND data transfer entries."""
    results = []
    if isinstance(obj, list):
        for item in obj:
            if isinstance(item, dict) and item.get('entryType') == 'OUTBOUND':
                results.append(item)
            else:
                results.extend(_find_outbound_entries(item))
    elif isinstance(obj, dict):
        for v in obj.values():
            results.extend(_find_outbound_entries(v))
    return results

# Region code to location name for data transfer pricing lookup
DT_REGION_TO_LOCATION = {
    'us-east-1': 'US East (N. Virginia)', 'us-east-2': 'US East (Ohio)',
    'us-west-1': 'US West (N. California)', 'us-west-2': 'US West (Oregon)',
    'eu-central-1': 'EU (Frankfurt)', 'eu-central-2': 'EU (Zurich)',
    'eu-west-1': 'EU (Ireland)', 'eu-west-2': 'EU (London)',
    'eu-west-3': 'EU (Paris)', 'eu-north-1': 'EU (Stockholm)',
    'eu-south-1': 'EU (Milan)', 'eu-south-2': 'EU (Spain)',
    'ap-south-1': 'Asia Pacific (Mumbai)', 'ap-south-2': 'Asia Pacific (Hyderabad)',
    'ap-northeast-1': 'Asia Pacific (Tokyo)', 'ap-northeast-2': 'Asia Pacific (Seoul)',
    'ap-northeast-3': 'Asia Pacific (Osaka)',
    'ap-southeast-1': 'Asia Pacific (Singapore)', 'ap-southeast-2': 'Asia Pacific (Sydney)',
    'ap-southeast-3': 'Asia Pacific (Jakarta)', 'ap-southeast-4': 'Asia Pacific (Melbourne)',
    'ap-southeast-5': 'Asia Pacific (Malaysia)', 'ap-southeast-7': 'Asia Pacific (Thailand)',
    'ca-central-1': 'Canada (Central)', 'ca-west-1': 'Canada West (Calgary)',
    'sa-east-1': 'South America (Sao Paulo)',
    'ap-east-1': 'Asia Pacific (Hong Kong)', 'me-south-1': 'Middle East (Bahrain)',
    'me-central-1': 'Middle East (UAE)',
    'af-south-1': 'Africa (Cape Town)', 'il-central-1': 'Israel (Tel Aviv)',
    'mx-central-1': 'Mexico (Central)', 'ap-southeast-6': 'Asia Pacific (Taipei)',
    'eusc-de-east-1': 'AWS European Sovereign Cloud (Germany)',
}

def _find_outbound_entries(obj):
    """Recursively find all OUTBOUND data transfer entries."""
    results = []
    if isinstance(obj, list):
        for item in obj:
            if isinstance(item, dict) and item.get('entryType') == 'OUTBOUND':
                results.append(item)
            else:
                results.extend(_find_outbound_entries(item))
    elif isinstance(obj, dict):
        for v in obj.values():
            results.extend(_find_outbound_entries(v))
    return results


def _calculate_outbound_dt_cost(service_data):
    """Calculate outbound data transfer cost using real AWS pricing data."""
    calc_components = service_data.get('calculationComponents', {})
    region = service_data.get('region', '')
    is_esc = region == ESC_REGION_CODE
    total_cost = 0

    # --- Standard outbound entries (VPC, EC2, etc.) ---
    outbound_entries = _find_outbound_entries(calc_components)
    if outbound_entries:
        dt_pricing = _load_dt_pricing(is_esc)
        from_location = DT_REGION_TO_LOCATION.get(region, '')
        for entry in outbound_entries:
            if not entry.get('value') or not entry.get('toRegion'):
                continue
            try:
                value = float(entry.get('value', 0))
                value_gb = value * 1024 if entry.get('unit') == 'tb_month' else value
                to_region = entry.get('toRegion')
                if to_region == 'External' and from_location:
                    region_data = dt_pricing.get('regions', {}).get(from_location, {})
                    t1 = float(region_data.get('DataTransfer External Outbound Next 10 TB', {}).get('price', 0))
                    if is_esc and t1 == 0:
                        t1 = float(region_data.get('DataTransfer External Outbound for 100 to 10240', {}).get('price', 0.077))
                    t2 = float(region_data.get('DataTransfer External Outbound Next 40 TB', {}).get('price', 0))
                    t3 = float(region_data.get('DataTransfer External Outbound Next 100 TB', {}).get('price', 0))
                    t4 = float(region_data.get('DataTransfer External Outbound Greater than 150 TB', {}).get('price', 0))
                    # Use correct fallback rates per region type
                    if is_esc:
                        t1 = t1 or 0.077
                        t2 = t2 or 0.073
                        t3 = t3 or 0.060
                        t4 = t4 or 0.043
                    else:
                        t1 = t1 or 0.09
                        t2 = t2 or 0.085
                        t3 = t3 or 0.07
                        t4 = t4 or 0.05
                    if is_esc:
                        tiers = [(0, 100, 0), (100, 10240, t1), (10240, 51200, t2), (51200, 153600, t3), (153600, float('inf'), t4)]
                    else:
                        tiers = [(0, 10240, t1), (10240, 51200, t2), (51200, 153600, t3), (153600, float('inf'), t4)]
                    remaining = value_gb
                    for begin, end, rate in tiers:
                        if remaining <= 0:
                            break
                        gb_in_tier = min(remaining, end - begin)
                        total_cost += gb_in_tier * rate
                        remaining -= gb_in_tier
                else:
                    total_cost += value_gb * 0.02
            except (ValueError, TypeError):
                continue

    # --- CloudFront data transfer out ---
    cf_pricing = _load_cf_pricing()
    cf_regions = cf_pricing.get('regions', {}).get('', {})
    cf_rate_to_price = {}
    cf_region_tier_to_rate = {}
    for rate_hash, rate_info in cf_regions.items():
        if not isinstance(rate_info, dict):
            continue
        rc = rate_info.get('rateCode')
        price = float(rate_info.get('price', 0))
        if rc:
            cf_rate_to_price[rc] = price
        mu = rate_info.get('meteredUnit', '')
        if 'Regional DT from' in mu and 'to Internet' in mu:
            parts = mu.split(' to Internet ')
            if len(parts) == 2:
                cf_region_tier_to_rate[(parts[0].replace('Regional DT from ', ''), parts[1])] = rc

    cf_origin_rates = {}
    for key, rate_info in cf_regions.items():
        if isinstance(rate_info, dict) and isinstance(key, str) and key.startswith('Regional DT to Origin from '):
            cf_origin_rates[key.replace('Regional DT to Origin from ', '')] = rate_info.get('rateCode')

    for field_name, value_obj in calc_components.items():
        if not isinstance(value_obj, dict):
            continue
        if 'dataTransferedToInternet' in field_name:
            try:
                val = value_obj.get('value', '')
                if not val or val == '':
                    continue
                amount = float(val)
                unit = value_obj.get('unit', 'gb|month')
                gb = amount * 1024 if 'tb' in unit else amount
                suffix = field_name.replace('dataTransferedToInternet', '')
                rn = CF_CALC_REGION_MAP.get(suffix)
                if not rn:
                    continue
                remaining = gb
                for tier_name, begin_gb, end_gb in CF_TIERS:
                    if remaining <= 0:
                        break
                    rc = cf_region_tier_to_rate.get((rn, tier_name))
                    price = cf_rate_to_price.get(rc, 0.085) if rc else 0.085
                    gb_in_tier = min(remaining, end_gb - begin_gb)
                    total_cost += gb_in_tier * price
                    remaining -= gb_in_tier
            except (ValueError, TypeError):
                continue
        elif 'dataTransferedToOrigin' in field_name:
            try:
                val = value_obj.get('value', '')
                if not val or val == '':
                    continue
                amount = float(val)
                unit = value_obj.get('unit', 'gb|month')
                gb = amount * 1024 if 'tb' in unit else amount
                suffix = field_name.replace('dataTransferedToOrigin', '')
                rn = CF_CALC_REGION_MAP.get(suffix)
                if not rn:
                    continue
                rc = cf_origin_rates.get(rn)
                price = cf_rate_to_price.get(rc, 0.02) if rc else 0.02
                total_cost += gb * price
            except (ValueError, TypeError):
                continue

    return total_cost


@map_bp.route('/service-completeness/analyze-url', methods=['POST'])
def analyze_calculator_url():
    """Fetch and analyze AWS Calculator data directly from URL for accurate service breakdown."""
    try:
        data = request.json
        calculator_url = data.get('calculator_url', '').strip()

        if not calculator_url:
            return jsonify({'success': False, 'message': 'Calculator URL is required'}), 400

        # Extract calculator ID
        id_match = re.search(r'id=([a-f0-9]+)', calculator_url)
        if not id_match:
            return jsonify({'success': False, 'message': 'Invalid calculator URL. Must contain a valid calculator ID (e.g. ?id=abc123...)'}), 400

        calculator_id = id_match.group(1)
        is_esc = 'pricing.calculator.aws.eu' in calculator_url

        # Fetch calculator JSON
        fetch_url = CALC_ESC_URL.format(calculator_id) if is_esc else CALC_CLOUDFRONT_URL.format(calculator_id)
        try:
            calc_resp = http_requests.get(fetch_url, timeout=30)
            if calc_resp.status_code != 200:
                return jsonify({'success': False, 'message': f'Calculator not found (HTTP {calc_resp.status_code}). Check the URL and try again.'}), 400
            calc_data = calc_resp.json()
        except Exception as e:
            logging.error(f"Failed to fetch calculator data: {e}")
            return jsonify({'success': False, 'message': 'Failed to fetch calculator data. Check the URL and try again.'}), 400

        # Load service manifest for display names
        manifest = _load_service_manifest()

        # Walk the nested JSON structure to extract services
        raw_services = []

        def process_node(node, path=''):
            for resource_id, service_data in node.get('services', {}).items():
                try:
                    if 'subServices' in service_data:
                        # Parent service with sub-services (e.g. EC2 with EBS)
                        parent_code = service_data.get('serviceCode', '')
                        parent_name = _get_service_name(parent_code, manifest)
                        parent_config = service_data.get('configSummary', '')

                        for idx, sub in enumerate(service_data['subServices']):
                            svc_code = sub.get('serviceCode', '')
                            monthly = sub.get('serviceCost', {}).get('monthly', 0)
                            upfront = sub.get('serviceCost', {}).get('upfront', 0)
                            region = sub.get('region', '')
                            desc = (sub.get('description') or '')[:100]

                            # Calculate outbound data transfer exclusion
                            dt_cost = _calculate_outbound_dt_cost(sub)

                            # Glacier Deep Archive: exclude entire monthly cost
                            if svc_code == 'amazonS3GlacierDeepArhive':
                                excluded = monthly
                                exc_type = 'glacier_deep_archive'
                            # Services always excluded from MAP (DT, NAT GW, CloudFront DT, S3 DT)
                            elif svc_code in ALWAYS_EXCLUDE_DT_SERVICES:
                                excluded = monthly
                                exc_type = 'data_transfer'
                            else:
                                excluded = dt_cost
                                exc_type = 'data_transfer' if dt_cost > 0 else None

                            pathway = classify_service_pathway(parent_name or svc_code)
                            # Fallback: try service code if display name didn't match
                            if pathway == 'Non Modern' and parent_name:
                                pathway = classify_service_pathway(svc_code)

                            # EC2 details from calculationComponents
                            ec2_instance_type = None
                            ec2_os = 'linux'
                            ec2_quantity = 1
                            ec2_is_ondemand = False
                            ec2_full_util = False

                            if svc_code == 'ec2Enhancement':
                                cc = sub.get('calculationComponents', {})
                                ec2_instance_type = cc.get('instanceType', {}).get('value')
                                ec2_os = cc.get('selectedOS', {}).get('value', 'linux')
                                pricing = cc.get('pricingStrategy', {}).get('value', {})
                                selected = (pricing.get('selectedOption') or '').lower()
                                ec2_is_ondemand = not selected or 'ondemand' in selected or 'on-demand' in selected
                                workload = cc.get('workload', {}).get('value', {})
                                ec2_quantity = int(workload.get('data', 1)) if isinstance(workload, dict) else 1
                                util_value = pricing.get('utilizationValue', 168)
                                util_unit = pricing.get('utilizationUnit', 'Hours/Week')
                                if util_unit == '%Utilized/Month':
                                    ec2_full_util = float(util_value) == 100
                                else:
                                    ec2_full_util = float(util_value) == FULL_TIME_HOURS_PER_WEEK

                            exclusion_breakdown = None
                            if exc_type:
                                exclusion_breakdown = str({
                                    'type': exc_type,
                                    'reason': f'{parent_name or svc_code} outbound data transfer excluded' if exc_type == 'data_transfer' else f'{parent_name or svc_code} not MAP eligible',
                                    'arr': excluded * 12
                                })

                            # Fargate details from calculationComponents
                            fargate_os = None
                            fargate_arch = None
                            fargate_duration = 0
                            fargate_vcpu = 0
                            fargate_tasks = 0
                            fargate_memory = 0
                            fargate_region = ''

                            if svc_code == 'awsFargate':
                                cc = sub.get('calculationComponents', {})
                                fargate_os = cc.get('operatingSystem', {}).get('value', 'linux')
                                fargate_arch = cc.get('selectArchitecture', {}).get('value', 'x86')
                                fargate_duration = float(cc.get('taskDuration', {}).get('value', 730))
                                fargate_vcpu = float(cc.get('vcpuPerTask', {}).get('value', 1))
                                fargate_tasks = float(cc.get('numberOfTasks', {}).get('value', 1))
                                fargate_memory = float(cc.get('memoryStandardFargateOnDemand', {}).get('value', 2))
                                fargate_region = region

                            raw_services.append({
                                'service_name': parent_name or svc_code,
                                'service_code': svc_code,
                                'monthly_cost': monthly,
                                'upfront_cost': upfront,
                                'region': region,
                                'group': path,
                                'modernization_pathway': pathway,
                                'map_qualified_mrr': monthly - excluded,
                                'monthly_always_excluded': excluded,
                                'exclusion_breakdown': exclusion_breakdown,
                                'config_summary': parent_config or '',
                                'description': desc or parent_name or svc_code,
                                '_ec2_instance_type': ec2_instance_type,
                                '_ec2_os': ec2_os,
                                '_ec2_quantity': ec2_quantity,
                                '_ec2_is_ondemand': ec2_is_ondemand,
                                '_ec2_full_util': ec2_full_util,
                                '_ec2_region': region,
                                '_ebs_storage_type': sub.get('calculationComponents', {}).get('storageType', {}).get('value', ''),
                                '_ebs_storage_amount': float(sub.get('calculationComponents', {}).get('storageAmount', {}).get('value', 0) or 0),
                                '_ebs_storage_iops': float(sub.get('calculationComponents', {}).get('storageIOPS', {}).get('value', 0) or 0),
                                '_fargate_os': fargate_os,
                                '_fargate_arch': fargate_arch,
                                '_fargate_duration': fargate_duration,
                                '_fargate_vcpu': fargate_vcpu,
                                '_fargate_tasks': fargate_tasks,
                                '_fargate_memory': fargate_memory,
                                '_fargate_region': fargate_region,
                            })
                    else:
                        # Single service
                        svc_code = service_data.get('serviceCode', '')
                        monthly = service_data.get('serviceCost', {}).get('monthly', 0)
                        upfront = service_data.get('serviceCost', {}).get('upfront', 0)
                        region = service_data.get('region', '')
                        svc_name = _get_service_name(svc_code, manifest) or svc_code
                        desc = (service_data.get('description') or '')[:100]
                        config = service_data.get('configSummary', '')

                        dt_cost = _calculate_outbound_dt_cost(service_data)

                        if svc_code == 'amazonS3GlacierDeepArhive':
                            excluded = monthly
                            exc_type = 'glacier_deep_archive'
                        elif svc_code in ALWAYS_EXCLUDE_DT_SERVICES:
                            excluded = monthly
                            exc_type = 'data_transfer'
                        else:
                            excluded = dt_cost
                            exc_type = 'data_transfer' if dt_cost > 0 else None

                        pathway = classify_service_pathway(svc_name)
                        # Fallback: try service code if display name didn't match
                        if pathway == 'Non Modern' and svc_name != svc_code:
                            pathway = classify_service_pathway(svc_code)

                        ec2_instance_type = None
                        ec2_os = 'linux'
                        ec2_quantity = 1
                        ec2_is_ondemand = False
                        ec2_full_util = False

                        if svc_code == 'ec2Enhancement':
                            cc = service_data.get('calculationComponents', {})
                            ec2_instance_type = cc.get('instanceType', {}).get('value')
                            ec2_os = cc.get('selectedOS', {}).get('value', 'linux')
                            pricing = cc.get('pricingStrategy', {}).get('value', {})
                            selected = (pricing.get('selectedOption') or '').lower()
                            ec2_is_ondemand = not selected or 'ondemand' in selected or 'on-demand' in selected
                            workload = cc.get('workload', {}).get('value', {})
                            ec2_quantity = int(workload.get('data', 1)) if isinstance(workload, dict) else 1
                            util_value = pricing.get('utilizationValue', 168)
                            util_unit = pricing.get('utilizationUnit', 'Hours/Week')
                            if util_unit == '%Utilized/Month':
                                ec2_full_util = float(util_value) == 100
                            else:
                                ec2_full_util = float(util_value) == FULL_TIME_HOURS_PER_WEEK

                        exclusion_breakdown = None
                        if exc_type:
                            exclusion_breakdown = str({
                                'type': exc_type,
                                'reason': f'{svc_name} outbound data transfer excluded' if exc_type == 'data_transfer' else f'{svc_name} not MAP eligible',
                                'arr': excluded * 12
                            })

                        # Fargate details from calculationComponents
                        fargate_os = None
                        fargate_arch = None
                        fargate_duration = 0
                        fargate_vcpu = 0
                        fargate_tasks = 0
                        fargate_memory = 0
                        fargate_region = ''

                        if svc_code == 'awsFargate':
                            cc = service_data.get('calculationComponents', {})
                            fargate_os = cc.get('operatingSystem', {}).get('value', 'linux')
                            fargate_arch = cc.get('selectArchitecture', {}).get('value', 'x86')
                            fargate_duration = float(cc.get('taskDuration', {}).get('value', 730))
                            fargate_vcpu = float(cc.get('vcpuPerTask', {}).get('value', 1))
                            fargate_tasks = float(cc.get('numberOfTasks', {}).get('value', 1))
                            fargate_memory = float(cc.get('memoryStandardFargateOnDemand', {}).get('value', 2))
                            fargate_region = region

                        raw_services.append({
                            'service_name': svc_name,
                            'service_code': svc_code,
                            'monthly_cost': monthly,
                            'upfront_cost': upfront,
                            'region': region,
                            'group': path,
                            'modernization_pathway': pathway,
                            'map_qualified_mrr': monthly - excluded,
                            'monthly_always_excluded': excluded,
                            'exclusion_breakdown': exclusion_breakdown,
                            'config_summary': config,
                            'description': desc or svc_name,
                            '_ec2_instance_type': ec2_instance_type,
                            '_ec2_os': ec2_os,
                            '_ec2_quantity': ec2_quantity,
                            '_ec2_is_ondemand': ec2_is_ondemand,
                            '_ec2_full_util': ec2_full_util,
                            '_ec2_region': region,
                            '_ebs_storage_type': service_data.get('calculationComponents', {}).get('storageType', {}).get('value', ''),
                            '_ebs_storage_amount': float(service_data.get('calculationComponents', {}).get('storageAmount', {}).get('value', 0) or 0),
                            '_ebs_storage_iops': float(service_data.get('calculationComponents', {}).get('storageIOPS', {}).get('value', 0) or 0),
                            '_fargate_os': fargate_os,
                            '_fargate_arch': fargate_arch,
                            '_fargate_duration': fargate_duration,
                            '_fargate_vcpu': fargate_vcpu,
                            '_fargate_tasks': fargate_tasks,
                            '_fargate_memory': fargate_memory,
                            '_fargate_region': fargate_region,
                        })
                except Exception as e:
                    logging.warning(f"Error processing service {resource_id}: {e}")
                    continue

            for group_id, sub_group in node.get('groups', {}).items():
                process_node(sub_group, f"{path}{group_id}-")

        process_node(calc_data)

        # EC2 Savings Plans optimization (before aggregation)
        od_cache = {}
        sp_cache = {}
        ec2_tasks = []

        for idx, svc in enumerate(raw_services):
            if (svc['service_code'] == 'ec2Enhancement'
                and svc['_ec2_instance_type']
                and svc['_ec2_is_ondemand']
                and svc['_ec2_full_util']):
                region_code = svc['_ec2_region']
                if not REGION_CODE_TO_NAME.get(region_code):
                    continue
                ec2_tasks.append((idx, region_code, svc['_ec2_instance_type'], svc['_ec2_os'], svc['_ec2_quantity']))

        def _lookup_sp(task):
            idx, region_code, instance_type, os_type, quantity = task
            result = get_ec2_sp_savings(region_code, instance_type, os_type, quantity, od_cache, sp_cache)
            return idx, result

        if ec2_tasks:
            with ThreadPoolExecutor(max_workers=min(len(ec2_tasks), 10)) as executor:
                futures = {executor.submit(_lookup_sp, t): t for t in ec2_tasks}
                for future in as_completed(futures):
                    try:
                        idx, sp_result = future.result()
                        if sp_result:
                            raw_services[idx]['ec2_sp_annual_savings'] = sp_result['annual_savings']
                            raw_services[idx]['ec2_sp_hourly_rate'] = sp_result['sp_hourly_rate']
                            raw_services[idx]['ec2_sp_plan_type'] = sp_result['plan_type']
                    except Exception as e:
                        logging.warning(f"EC2 SP future failed: {e}")

        # RI optimization for RDS, Redshift, ElastiCache, OpenSearch
        _run_ri_optimization(raw_services, use_region_code=True)

        # EBS storage optimization (gp2→gp3, io1→io2)
        _run_ebs_optimization(raw_services)

        # Fargate and Graviton advisory notes
        _add_advisory_notes(raw_services, od_cache=od_cache, is_esc=is_esc)

        # Set defaults and clean up internal fields
        for svc in raw_services:
            svc.setdefault('ec2_sp_annual_savings', 0)
            svc.setdefault('ec2_sp_hourly_rate', 0)
            svc.setdefault('ec2_sp_plan_type', '')
            svc.setdefault('graviton_savings', 0)
            svc.setdefault('ebs_savings', 0)
            svc.setdefault('ebs_plan_type', '')
            svc.setdefault('ebs_detail', '')
            for key in list(svc.keys()):
                if key.startswith('_ec2_') or key.startswith('_fargate_') or key.startswith('_graviton_') or key.startswith('_ebs_'):
                    del svc[key]

        # Aggregate by service_code
        aggregated = {}
        for svc in raw_services:
            key = svc['service_code'].lower()
            if key not in aggregated:
                aggregated[key] = {k: v for k, v in svc.items()}
                aggregated[key]['line_item_count'] = 0
                aggregated[key]['monthly_cost'] = 0
                aggregated[key]['upfront_cost'] = 0
                aggregated[key]['map_qualified_mrr'] = 0
                aggregated[key]['monthly_always_excluded'] = 0
                aggregated[key]['ec2_sp_annual_savings'] = 0
                aggregated[key]['ec2_sp_hourly_rate'] = 0
                aggregated[key]['optimization_details'] = []
                aggregated[key]['graviton_savings'] = 0
                aggregated[key]['ebs_savings'] = 0
                aggregated[key]['ebs_plan_type'] = ''
                aggregated[key]['ebs_detail'] = ''
            agg = aggregated[key]
            agg['monthly_cost'] += svc['monthly_cost']
            agg['upfront_cost'] += svc['upfront_cost']
            agg['map_qualified_mrr'] += svc['map_qualified_mrr']
            agg['monthly_always_excluded'] += svc['monthly_always_excluded']
            agg['ec2_sp_annual_savings'] += svc['ec2_sp_annual_savings']
            agg['graviton_savings'] += svc.get('graviton_savings', 0)
            agg['ebs_savings'] = agg.get('ebs_savings', 0) + svc.get('ebs_savings', 0)
            if svc.get('ebs_detail') and svc.get('ebs_savings', 0) > 0:
                existing = agg.get('ebs_detail', '')
                agg['ebs_detail'] = (existing + '; ' + svc['ebs_detail']) if existing else svc['ebs_detail']
                if not agg.get('ebs_plan_type'):
                    agg['ebs_plan_type'] = svc.get('ebs_plan_type', '')
            if svc['ec2_sp_hourly_rate'] > agg['ec2_sp_hourly_rate']:
                agg['ec2_sp_hourly_rate'] = svc['ec2_sp_hourly_rate']
            if svc['ec2_sp_plan_type'] and not agg['ec2_sp_plan_type']:
                agg['ec2_sp_plan_type'] = svc['ec2_sp_plan_type']
            # Collect per-instance optimization details for the report
            if svc.get('ec2_sp_annual_savings', 0) > 0:
                agg['optimization_details'].append({
                    'service_name': svc['service_name'],
                    'description': svc.get('description', ''),
                    'region': svc.get('region', ''),
                    'config_summary': svc.get('config_summary', ''),
                    'monthly_cost': svc['monthly_cost'],
                    'ec2_sp_annual_savings': svc['ec2_sp_annual_savings'],
                    'ec2_sp_hourly_rate': svc.get('ec2_sp_hourly_rate', 0),
                    'ec2_sp_plan_type': svc.get('ec2_sp_plan_type', ''),
                })
            agg['line_item_count'] += 1
            if not agg.get('config_summary') and svc.get('config_summary'):
                agg['config_summary'] = svc['config_summary']
            if svc.get('optimization_note') and not agg.get('optimization_note'):
                agg['optimization_note'] = svc['optimization_note']
            if svc.get('graviton_note') and not agg.get('graviton_note'):
                agg['graviton_note'] = svc['graviton_note']

        services = list(aggregated.values())

        # Calculate modernization pathways (using map_qualified_mrr)
        pathway_breakdown = {}
        for svc in services:
            pw = svc['modernization_pathway']
            if pw not in pathway_breakdown:
                pathway_breakdown[pw] = {'services': [], 'total_arr': 0}
            arr = svc['map_qualified_mrr'] * 12
            pathway_breakdown[pw]['services'].append({
                'serviceCode': svc['service_code'],
                'serviceName': svc['service_name'],
                'arr': round(arr, 2),
            })
            pathway_breakdown[pw]['total_arr'] += arr

        total_arr = sum(s['monthly_cost'] * 12 + s.get('upfront_cost', 0) for s in services)
        qualified_arr = sum(s['map_qualified_mrr'] * 12 for s in services)
        non_modern_arr = pathway_breakdown.get('Non Modern', {}).get('total_arr', 0)
        modern_arr = qualified_arr - non_modern_arr
        modernization_index = (modern_arr / qualified_arr * 100) if qualified_arr > 0 else 0

        pathways_list = []
        for pw_name in sorted(pathway_breakdown.keys()):
            pw_data = pathway_breakdown[pw_name]
            pathways_list.append({
                'name': pw_name,
                'arr': round(pw_data['total_arr'], 2),
                'serviceCount': len(pw_data['services']),
                'services': pw_data['services'],
            })

        total_sp_savings = sum(s.get('ec2_sp_annual_savings', 0) for s in services)
        not_optimized_pct = (total_sp_savings / total_arr * 100) if total_arr > 0 else 0

        result = {
            'success': True,
            'services': services,
            'serviceCount': len(services),
            'calculatorUrl': calculator_url,
            'calculatorId': calculator_id,
            'is_esc': is_esc,
            'currency': 'EUR' if is_esc else 'USD',
            'modernizationPathways': {
                'totalARR': round(total_arr, 2),
                'modernARR': round(modern_arr, 2),
                'modernizationIndex': round(modernization_index, 2),
                'pathways': pathways_list,
            },
            'validation': {
                'calculator_total_arr': round(total_arr, 2),
                'not_optimized_percentage': round(not_optimized_pct, 2),
                'optimization_threshold_met': not_optimized_pct < 5,
                'status': 'validated'
            }
        }

        return jsonify(result)

    except Exception as e:
        logging.error(f"Calculator URL analysis failed: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500


# ============================================================================
# CALCULATOR REVIEW ENDPOINTS
# ============================================================================

@map_bp.route('/service-completeness/analyze-calculator', methods=['POST'])
def analyze_calculator_csv():
    """Parse AWS Calculator CSV and return structured service data for calculator review dashboard.

    Enhancements over basic version:
    1. Full pathway categorization using AWS modernization pathway mapping
    2. Service aggregation by service_code (case-insensitive)
    3. EC2 Savings Plans optimization via AWS Pricing API
    """
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400

        file = request.files['file']
        if not file or not allowed_file(file.filename):
            return jsonify({'success': False, 'message': 'Invalid file type'}), 400

        is_valid, error_msg = validate_file_size(file)
        if not is_valid:
            return jsonify({'success': False, 'message': error_msg}), 400

        csv_data = file.read().decode('utf-8')
        lines = csv_data.splitlines()

        # Find header row
        start_idx = 0
        header_patterns = [
            "Group hierarchy,Region,Description",
            "Gruppenhierarchie,Region,Beschreibung",
            "Group hierarchy",
            "Gruppenhierarchie"
        ]
        for i, line in enumerate(lines):
            if any(pattern in line for pattern in header_patterns):
                start_idx = i
                break

        try:
            calc_df = pd.read_csv(
                io.StringIO("\n".join(lines[start_idx:])),
                encoding="utf-8",
                on_bad_lines='skip',
                quoting=1
            )
        except Exception:
            try:
                calc_df = pd.read_csv(
                    io.StringIO("\n".join(lines[start_idx:])),
                    encoding="utf-8",
                    on_bad_lines='skip',
                    quoting=3
                )
            except Exception:
                return jsonify({'success': False, 'message': 'Failed to parse CSV file'}), 400

        # ----------------------------------------------------------------
        # Column detection
        # ----------------------------------------------------------------
        cost_col = None
        for col in calc_df.columns:
            cl = col.lower()
            if 'upfront' in cl:
                continue
            if 'monthly' in cl or 'cost' in cl or 'price' in cl or 'kosten' in cl:
                cost_col = col
                break

        service_col = None
        description_col = None
        for col in calc_df.columns:
            cl = col.lower().strip()
            # Exact match for 'service' column (the actual AWS service name)
            if cl == 'service':
                service_col = col
            # 'description' is the user-entered label, not the service name
            elif cl == 'description' or cl == 'beschreibung':
                description_col = col
        # Fallback: if no exact 'service' column, try partial match
        if not service_col:
            for col in calc_df.columns:
                cl = col.lower().strip()
                if 'service' in cl:
                    service_col = col
                    break
        # Last resort: use description column as service name
        if not service_col and description_col:
            service_col = description_col
            description_col = None

        region_col = None
        for col in calc_df.columns:
            if col.lower() == 'region':
                region_col = col
                break

        group_col = None
        for col in calc_df.columns:
            cl = col.lower()
            if 'group' in cl or 'hierarchy' in cl or 'gruppenhierarchie' in cl:
                group_col = col
                break

        upfront_col = None
        for col in calc_df.columns:
            cl = col.lower()
            if 'upfront' in cl:
                upfront_col = col
                break

        # Identify configuration summary column
        config_col = None
        for col in calc_df.columns:
            cl = col.lower()
            if 'configuration' in cl or 'config' in cl or 'konfiguration' in cl:
                config_col = col
                break

        # ----------------------------------------------------------------
        # Parse all rows into raw service list
        # ----------------------------------------------------------------
        raw_services = []
        for _, row in calc_df.iterrows():
            service_name = str(row.get(service_col, '')) if service_col else ''
            if not service_name or service_name == 'nan':
                continue

            # Parse monthly cost
            monthly_cost = 0
            if cost_col:
                try:
                    cost_str = str(row[cost_col]).replace(',', '').replace('$', '').replace('\u20ac', '').replace('USD', '').replace('EUR', '').strip()
                    monthly_cost = float(cost_str) if cost_str and cost_str != 'nan' else 0
                except (ValueError, TypeError):
                    monthly_cost = 0

            # Parse upfront cost
            upfront_cost = 0
            if upfront_col:
                try:
                    up_str = str(row[upfront_col]).replace(',', '').replace('$', '').replace('\u20ac', '').replace('USD', '').replace('EUR', '').strip()
                    upfront_cost = float(up_str) if up_str and up_str != 'nan' else 0
                except (ValueError, TypeError):
                    upfront_cost = 0

            region = str(row.get(region_col, '')) if region_col else ''
            if region == 'nan':
                region = ''
            group = str(row.get(group_col, '')) if group_col else ''
            if group == 'nan':
                group = ''
            config_summary = str(row.get(config_col, '')) if config_col else ''
            if config_summary == 'nan':
                config_summary = ''
            description = str(row.get(description_col, '')) if description_col else ''
            if description == 'nan':
                description = ''

            # Derive service_code (strip spaces but keep casing structure)
            service_code = service_name.replace(' ', '')

            # Classify pathway using modernization pathway mapping
            pathway = classify_service_pathway(service_name)

            # Check if excluded
            service_name_lower = service_name.lower()
            service_code_lower = service_code.lower()
            monthly_excluded = 0
            exclusion_type = None
            for pattern, exc_type in EXCLUDED_PATTERNS.items():
                if pattern in service_name_lower or pattern in service_code_lower:
                    monthly_excluded = monthly_cost
                    exclusion_type = exc_type
                    break

            map_qualified_mrr = monthly_cost if not exclusion_type else 0

            # Build exclusion breakdown
            exclusion_breakdown = None
            if exclusion_type:
                exclusion_breakdown = str({
                    'type': exclusion_type,
                    'reason': f'{service_name} is always excluded from MAP qualification',
                    'arr': monthly_excluded * 12
                })

            raw_services.append({
                'service_name': service_name,
                'service_code': service_code,
                'monthly_cost': monthly_cost,
                'upfront_cost': upfront_cost,
                'region': region,
                'group': group,
                'modernization_pathway': pathway,
                'map_qualified_mrr': map_qualified_mrr,
                'monthly_always_excluded': monthly_excluded,
                'exclusion_breakdown': exclusion_breakdown,
                'config_summary': config_summary,
                'description': description if description else (group if group else service_name),
            })

        # ----------------------------------------------------------------
        # EC2 Savings Plans optimization (BEFORE aggregation)
        # For EC2 On-Demand instances at 100% utilization, look up SP rates
        # Must run on raw_services to preserve per-instance config details
        # ----------------------------------------------------------------
        od_cache = {}
        sp_cache = {}

        ec2_tasks = []
        for idx, svc in enumerate(raw_services):
            svc_name_lower = svc['service_name'].lower()
            svc_code_lower = svc['service_code'].lower()
            is_ec2 = 'amazon ec2' in svc_name_lower or 'amazonec2' in svc_name_lower or 'ec2' in svc_code_lower
            if not is_ec2:
                continue

            cfg = svc.get('config_summary', '')
            if not cfg:
                continue

            inst_match = re.search(r'Advance EC2 instance \(([^)]+)\)', cfg)
            os_match = re.search(r'Operating system \(([^)]+)\)', cfg)
            pricing_match = re.search(r'Pricing strategy \(([^)]+)\)', cfg)
            qty_match = re.search(r'Number of instances:\s*(\d+)', cfg)
            util_match = re.search(r'Utilization:\s*(\d+)\s*%', cfg)

            if not inst_match:
                continue

            instance_type = inst_match.group(1).strip()
            os_type = os_match.group(1).strip() if os_match else 'Linux'
            pricing_strategy = pricing_match.group(1).strip() if pricing_match else ''
            quantity = int(qty_match.group(1)) if qty_match else 1
            utilization = int(util_match.group(1)) if util_match else 100

            if 'on-demand' not in pricing_strategy.lower() and 'ondemand' not in pricing_strategy.lower():
                continue
            if utilization != 100:
                continue

            region_display = svc.get('region', '')
            region_code = REGION_NAME_TO_CODE.get(region_display, '')
            if not region_code:
                for rname, rcode in REGION_NAME_TO_CODE.items():
                    if rname in region_display or region_display in rname:
                        region_code = rcode
                        break
            if not region_code:
                continue

            ec2_tasks.append((idx, region_code, instance_type, os_type, quantity))

        def _lookup_sp(task):
            idx, region_code, instance_type, os_type, quantity = task
            result = get_ec2_sp_savings(region_code, instance_type, os_type, quantity, od_cache, sp_cache)
            return idx, result

        if ec2_tasks:
            with ThreadPoolExecutor(max_workers=min(len(ec2_tasks), 10)) as executor:
                futures = {executor.submit(_lookup_sp, t): t for t in ec2_tasks}
                for future in as_completed(futures):
                    try:
                        idx, sp_result = future.result()
                        if sp_result:
                            raw_services[idx]['ec2_sp_annual_savings'] = sp_result['annual_savings']
                            raw_services[idx]['ec2_sp_hourly_rate'] = sp_result['sp_hourly_rate']
                            raw_services[idx]['ec2_sp_plan_type'] = sp_result['plan_type']
                    except Exception as e:
                        logging.warning(f"EC2 SP future failed: {e}")

        # RI optimization for RDS, Redshift, ElastiCache, OpenSearch
        _run_ri_optimization(raw_services, use_region_code=False)

        # EBS storage optimization (gp2→gp3, io1→io2)
        _run_ebs_optimization(raw_services)

        # Fargate and Graviton advisory notes
        _add_advisory_notes(raw_services, od_cache=od_cache)

        # Ensure all raw services have SP fields and clean up internal fields
        for svc in raw_services:
            svc.setdefault('ec2_sp_annual_savings', 0)
            svc.setdefault('ec2_sp_hourly_rate', 0)
            svc.setdefault('ec2_sp_plan_type', '')
            svc.setdefault('graviton_savings', 0)
            svc.setdefault('ebs_savings', 0)
            svc.setdefault('ebs_plan_type', '')
            svc.setdefault('ebs_detail', '')
            for key in list(svc.keys()):
                if key.startswith('_ec2_') or key.startswith('_fargate_') or key.startswith('_graviton_') or key.startswith('_ebs_'):
                    del svc[key]

        # ----------------------------------------------------------------
        # Aggregate services by service_code (case-insensitive)
        # Matches aggregateServicesByCode in PricingCalculatorTab.js
        # ----------------------------------------------------------------
        aggregated = {}
        for svc in raw_services:
            key = svc['service_code'].lower()
            if key not in aggregated:
                aggregated[key] = {
                    'service_name': svc['service_name'],
                    'service_code': svc['service_code'],
                    'monthly_cost': 0,
                    'upfront_cost': 0,
                    'map_qualified_mrr': 0,
                    'monthly_always_excluded': 0,
                    'ec2_sp_annual_savings': 0,
                    'ec2_sp_hourly_rate': 0,
                    'ec2_sp_plan_type': '',
                    'graviton_savings': 0,
                    'ebs_savings': 0,
                    'ebs_plan_type': '',
                    'ebs_detail': '',
                    'region': svc['region'],
                    'group': svc['group'],
                    'modernization_pathway': svc['modernization_pathway'],
                    'exclusion_breakdown': svc['exclusion_breakdown'],
                    'config_summary': svc['config_summary'],
                    'description': svc['description'],
                    'line_item_count': 0,
                    'optimization_details': [],
                }
            agg = aggregated[key]
            agg['monthly_cost'] += svc['monthly_cost']
            agg['upfront_cost'] += svc['upfront_cost']
            agg['map_qualified_mrr'] += svc['map_qualified_mrr']
            agg['monthly_always_excluded'] += svc['monthly_always_excluded']
            agg['ec2_sp_annual_savings'] += svc['ec2_sp_annual_savings']
            agg['graviton_savings'] += svc.get('graviton_savings', 0)
            agg['ebs_savings'] = agg.get('ebs_savings', 0) + svc.get('ebs_savings', 0)
            if svc.get('ebs_detail') and svc.get('ebs_savings', 0) > 0:
                existing = agg.get('ebs_detail', '')
                agg['ebs_detail'] = (existing + '; ' + svc['ebs_detail']) if existing else svc['ebs_detail']
                if not agg.get('ebs_plan_type'):
                    agg['ebs_plan_type'] = svc.get('ebs_plan_type', '')
            # Keep highest SP hourly rate for display
            if svc['ec2_sp_hourly_rate'] > agg['ec2_sp_hourly_rate']:
                agg['ec2_sp_hourly_rate'] = svc['ec2_sp_hourly_rate']
            if svc['ec2_sp_plan_type'] and not agg['ec2_sp_plan_type']:
                agg['ec2_sp_plan_type'] = svc['ec2_sp_plan_type']
            if svc.get('ec2_sp_annual_savings', 0) > 0:
                agg['optimization_details'].append({
                    'service_name': svc['service_name'],
                    'description': svc.get('description', ''),
                    'region': svc.get('region', ''),
                    'config_summary': svc.get('config_summary', ''),
                    'monthly_cost': svc['monthly_cost'],
                    'ec2_sp_annual_savings': svc['ec2_sp_annual_savings'],
                    'ec2_sp_hourly_rate': svc.get('ec2_sp_hourly_rate', 0),
                    'ec2_sp_plan_type': svc.get('ec2_sp_plan_type', ''),
                })
            agg['line_item_count'] += 1
            if not agg['config_summary'] and svc['config_summary']:
                agg['config_summary'] = svc['config_summary']
            if svc.get('optimization_note') and not agg.get('optimization_note'):
                agg['optimization_note'] = svc['optimization_note']
            if svc.get('graviton_note') and not agg.get('graviton_note'):
                agg['graviton_note'] = svc['graviton_note']

        services = list(aggregated.values())
        # ----------------------------------------------------------------
        # Calculate modernization pathways summary (per-pathway breakdown)
        # Uses map_qualified_mrr (excludes excluded services) for index calculation
        # ----------------------------------------------------------------
        pathway_breakdown = {}
        for svc in services:
            pw = svc['modernization_pathway']
            if pw not in pathway_breakdown:
                pathway_breakdown[pw] = {'services': [], 'total_arr': 0}
            # Use map_qualified_mrr for pathway ARR (excludes excluded services)
            arr = svc['map_qualified_mrr'] * 12
            pathway_breakdown[pw]['services'].append({
                'serviceCode': svc['service_code'],
                'serviceName': svc['service_name'],
                'arr': round(arr, 2),
            })
            pathway_breakdown[pw]['total_arr'] += arr

        # Total ARR includes all services (for display)
        total_arr = sum(s['monthly_cost'] * 12 + s.get('upfront_cost', 0) for s in services)
        # Qualified ARR excludes excluded services (for modernization index)
        qualified_arr = sum(s['map_qualified_mrr'] * 12 for s in services)
        non_modern_arr = pathway_breakdown.get('Non Modern', {}).get('total_arr', 0)
        modern_arr = qualified_arr - non_modern_arr
        modernization_index = (modern_arr / qualified_arr * 100) if qualified_arr > 0 else 0

        pathways_list = []
        for pw_name in sorted(pathway_breakdown.keys()):
            pw_data = pathway_breakdown[pw_name]
            pathways_list.append({
                'name': pw_name,
                'arr': round(pw_data['total_arr'], 2),
                'serviceCount': len(pw_data['services']),
                'services': pw_data['services'],
            })

        modernization_pathways = {
            'totalARR': round(total_arr, 2),
            'modernARR': round(modern_arr, 2),
            'modernizationIndex': round(modernization_index, 2),
            'pathways': pathways_list,
        }

        # ----------------------------------------------------------------
        # Build validation summary
        # ----------------------------------------------------------------
        total_sp_savings = sum(s.get('ec2_sp_annual_savings', 0) for s in services)
        not_optimized_pct = (total_sp_savings / total_arr * 100) if total_arr > 0 else 0

        is_esc = any(
            REGION_NAME_TO_CODE.get(s.get('region', ''), '') == ESC_REGION_CODE
            for s in services
        )

        result = {
            'success': True,
            'services': services,
            'serviceCount': len(services),
            'modernizationPathways': modernization_pathways,
            'is_esc': is_esc,
            'currency': ESC_CURRENCY if is_esc else 'USD',
            'validation': {
                'calculator_total_arr': round(total_arr, 2),
                'not_optimized_percentage': round(not_optimized_pct, 2),
                'optimization_threshold_met': not_optimized_pct < 5,
                'status': 'validated'
            }
        }

        return jsonify(result)

    except Exception as e:
        logging.error(f"Calculator CSV analysis failed: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred'}), 500


# ============================================================================
# Health check endpoint
@map_bp.route('/health', methods=['GET'])
def health_check():
    """Health check for MAP routes"""
    return jsonify({
        'success': True,
        'message': 'MAP Assessment API is running',
        'endpoints': {
            'modernization': 3,
            'migration': 1,
            'resource_planning': 1,
            'learning_pathway': 1,
            'business_validation': 1,
            'architecture_diagram': 1,
            'chat': 1,
            'service_analysis': 1,
            'ola_analysis': 1
        }
    })
