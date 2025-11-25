from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import subprocess
import json
from werkzeug.utils import secure_filename
import tempfile
import shutil
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = tempfile.mkdtemp()
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv', 'pdf', 'pptx', 'ppt', 'md', 'docx', 'doc'}
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Path to the agents directory
AGENTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../agents'))
INPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../input'))
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../output'))

# DynamoDB configuration
DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME', 'aws-migration-business-cases')
DYNAMODB_REGION = os.environ.get('AWS_REGION', 'us-east-1')

# S3 configuration (optional)
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', None)
S3_ENABLED = S3_BUCKET_NAME is not None

# Initialize DynamoDB client (will be None if credentials not available)
dynamodb_client = None
dynamodb_table = None
try:
    dynamodb_client = boto3.resource('dynamodb', region_name=DYNAMODB_REGION)
    dynamodb_table = dynamodb_client.Table(DYNAMODB_TABLE_NAME)
except Exception as e:
    print(f"Warning: DynamoDB not available: {str(e)}")

# Initialize S3 client (will be None if not configured)
s3_client = None
if S3_ENABLED:
    try:
        s3_client = boto3.client('s3', region_name=DYNAMODB_REGION)
        # Verify bucket exists
        s3_client.head_bucket(Bucket=S3_BUCKET_NAME)
        print(f"✓ S3 bucket '{S3_BUCKET_NAME}' is accessible")
    except Exception as e:
        print(f"Warning: S3 not available: {str(e)}")
        s3_client = None
        S3_ENABLED = False

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_dynamodb_enabled():
    """Check if DynamoDB is available and configured"""
    return dynamodb_table is not None

def is_s3_enabled():
    """Check if S3 is available and configured"""
    return s3_client is not None and S3_ENABLED

def upload_file_to_s3(file_path, case_id, file_key):
    """Upload a file to S3 and return the S3 key"""
    if not is_s3_enabled():
        return None
    
    try:
        s3_key = f"{case_id}/{file_key}"
        s3_client.upload_file(file_path, S3_BUCKET_NAME, s3_key)
        return s3_key
    except Exception as e:
        print(f"Error uploading to S3: {str(e)}")
        return None

def download_file_from_s3(s3_key, local_path):
    """Download a file from S3 to local path"""
    if not is_s3_enabled():
        return False
    
    try:
        s3_client.download_file(S3_BUCKET_NAME, s3_key, local_path)
        return True
    except Exception as e:
        print(f"Error downloading from S3: {str(e)}")
        return False

def delete_files_from_s3(case_id):
    """Delete all files for a case from S3"""
    if not is_s3_enabled():
        return True
    
    try:
        # List all objects with the case_id prefix
        response = s3_client.list_objects_v2(
            Bucket=S3_BUCKET_NAME,
            Prefix=f"{case_id}/"
        )
        
        if 'Contents' in response:
            objects = [{'Key': obj['Key']} for obj in response['Contents']]
            if objects:
                s3_client.delete_objects(
                    Bucket=S3_BUCKET_NAME,
                    Delete={'Objects': objects}
                )
        return True
    except Exception as e:
        print(f"Error deleting from S3: {str(e)}")
        return False

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'API is running'})

@app.route('/api/storage/status', methods=['GET'])
def storage_status():
    """Check storage options status"""
    return jsonify({
        'dynamodb': {
            'enabled': is_dynamodb_enabled(),
            'tableName': DYNAMODB_TABLE_NAME if is_dynamodb_enabled() else None,
            'region': DYNAMODB_REGION if is_dynamodb_enabled() else None
        },
        's3': {
            'enabled': is_s3_enabled(),
            'bucketName': S3_BUCKET_NAME if is_s3_enabled() else None,
            'region': DYNAMODB_REGION if is_s3_enabled() else None
        }
    })

@app.route('/api/generate', methods=['POST'])
def generate_business_case():
    try:
        # Get project info
        project_info = json.loads(request.form.get('projectInfo', '{}'))
        selected_agents = json.loads(request.form.get('selectedAgents', '[]'))
        case_id = request.form.get('caseId', None)
        
        # Generate case ID if not provided
        if not case_id:
            case_id = f"case-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        
        # Create temporary input directory for this request
        temp_input_dir = os.path.join(UPLOAD_FOLDER, 'input')
        os.makedirs(temp_input_dir, exist_ok=True)
        
        # Save uploaded files
        file_mapping = {
            'itInventory': 'it-infrastructure-inventory.xlsx',
            'atxExcel': 'atx_analysis.xlsx',
            'atxPdf': 'atx_report.pdf',
            'atxPptx': 'atx_business_case.pptx',
            'mra': 'aws-customer-migration-readiness-assessment.md',
            'portfolio': 'application-portfolio.csv'
        }
        
        uploaded_files = {}
        s3_file_keys = {}
        
        # Handle single files
        for key, target_filename in file_mapping.items():
            if key in request.files:
                file = request.files[key]
                if file and allowed_file(file.filename):
                    # Save to input directory with expected filename
                    filepath = os.path.join(INPUT_DIR, target_filename)
                    file.save(filepath)
                    uploaded_files[key] = filepath
                    
                    # Upload to S3 if enabled
                    if is_s3_enabled():
                        s3_key = upload_file_to_s3(filepath, case_id, target_filename)
                        if s3_key:
                            s3_file_keys[key] = s3_key
        
        # Handle multiple RVTools files
        if 'rvTool' in request.files:
            rv_files = request.files.getlist('rvTool')
            print(f"DEBUG: Received {len(rv_files)} RVTools file(s)")
            rv_file_paths = []
            rv_s3_keys = []
            
            for idx, file in enumerate(rv_files):
                print(f"DEBUG: Processing RVTools file {idx}: {file.filename if file else 'None'}")
                if file and allowed_file(file.filename):
                    # Preserve original filename or use index
                    safe_filename = secure_filename(file.filename)
                    filepath = os.path.join(INPUT_DIR, safe_filename)
                    print(f"DEBUG: Saving RVTools file to: {filepath}")
                    file.save(filepath)
                    rv_file_paths.append(filepath)
                    print(f"DEBUG: RVTools file saved successfully: {safe_filename}")
                    
                    # Upload to S3 if enabled
                    if is_s3_enabled():
                        s3_key = upload_file_to_s3(filepath, case_id, safe_filename)
                        if s3_key:
                            rv_s3_keys.append(s3_key)
                else:
                    print(f"DEBUG: RVTools file rejected - file: {file}, allowed: {allowed_file(file.filename) if file else 'N/A'}")
            
            if rv_file_paths:
                uploaded_files['rvTool'] = rv_file_paths
                print(f"DEBUG: Total RVTools files uploaded: {len(rv_file_paths)}")
                if rv_s3_keys:
                    s3_file_keys['rvTool'] = rv_s3_keys
        else:
            print("DEBUG: No 'rvTool' field found in request.files")
        
        # Save project info and uploaded filenames to a file for agents to access
        project_info_with_files = project_info.copy()
        project_info_with_files['uploadedFiles'] = {
            key: [os.path.basename(f) for f in files] if isinstance(files, list) else os.path.basename(files)
            for key, files in uploaded_files.items()
        }
        
        project_info_file = os.path.join(INPUT_DIR, 'project_info.json')
        with open(project_info_file, 'w', encoding='utf-8') as f:
            json.dump(project_info_with_files, f, indent=2)
        
        # Run the business case generator
        result = run_business_case_generator(project_info, selected_agents)
        
        # Read the generated business case
        output_file = os.path.join(OUTPUT_DIR, 'aws_business_case.md')
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return jsonify({
                'success': True,
                'content': content,
                'projectInfo': project_info,
                'agentsExecuted': len(selected_agents),
                'executionTime': result.get('execution_time', 'N/A'),
                'tokenUsage': result.get('token_usage', 'N/A'),
                'caseId': case_id,
                'uploadedFiles': list(uploaded_files.keys()),
                's3FileKeys': s3_file_keys if is_s3_enabled() else None,
                's3BucketName': S3_BUCKET_NAME if is_s3_enabled() else None
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Business case file not generated'
            }), 500
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

def run_business_case_generator(project_info, selected_agents):
    """Run the Python business case generator"""
    try:
        # Change to agents directory
        os.chdir(AGENTS_DIR)
        
        # Run the business case generator
        result = subprocess.run(
            [sys.executable, 'aws_business_case.py'],
            capture_output=True,
            text=True,
            timeout=1800  # 30 minutes timeout
        )
        
        if result.returncode != 0:
            raise Exception(f"Generator failed: {result.stderr}")
        
        # Parse output for execution stats
        output_lines = result.stdout.split('\n')
        execution_time = 'N/A'
        token_usage = 'N/A'
        
        for line in output_lines:
            if 'Execution Time:' in line:
                execution_time = line.split('Execution Time:')[1].strip()
            if 'Token Usage:' in line:
                token_usage = line.split('Token Usage:')[1].strip()
        
        return {
            'execution_time': execution_time,
            'token_usage': token_usage,
            'stdout': result.stdout
        }
        
    except subprocess.TimeoutExpired:
        raise Exception('Business case generation timed out (30 minutes)')
    except Exception as e:
        raise Exception(f'Failed to run generator: {str(e)}')

@app.route('/api/status/<job_id>', methods=['GET'])
def check_status(job_id):
    """Check the status of a generation job"""
    # This is a placeholder for async job tracking
    return jsonify({
        'jobId': job_id,
        'status': 'completed',
        'progress': 100
    })

@app.route('/api/dynamodb/status', methods=['GET'])
def dynamodb_status():
    """Check if DynamoDB is enabled and available"""
    enabled = is_dynamodb_enabled()
    return jsonify({
        'enabled': enabled,
        'tableName': DYNAMODB_TABLE_NAME if enabled else None,
        'region': DYNAMODB_REGION if enabled else None
    })

@app.route('/api/dynamodb/save', methods=['POST'])
def save_to_dynamodb():
    """Save a business case to DynamoDB"""
    if not is_dynamodb_enabled():
        return jsonify({
            'success': False,
            'message': 'DynamoDB is not enabled or configured'
        }), 503
    
    try:
        data = request.json
        case_id = data.get('caseId')
        
        if not case_id:
            # Generate new ID if not provided
            case_id = f"case-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        
        item = {
            'caseId': case_id,
            'projectInfo': data.get('projectInfo', {}),
            'uploadedFiles': data.get('uploadedFiles', {}),
            'selectedAgents': data.get('selectedAgents', {}),
            'businessCaseContent': data.get('businessCaseContent', ''),
            'createdAt': data.get('createdAt', datetime.utcnow().isoformat()),
            'lastUpdated': datetime.utcnow().isoformat(),
            'executionStats': data.get('executionStats', {}),
            's3FileKeys': data.get('s3FileKeys', {}) if is_s3_enabled() else {},
            's3BucketName': S3_BUCKET_NAME if is_s3_enabled() else None,
            's3Enabled': is_s3_enabled()
        }
        
        dynamodb_table.put_item(Item=item)
        
        return jsonify({
            'success': True,
            'caseId': case_id,
            'lastUpdated': item['lastUpdated'],
            's3Enabled': is_s3_enabled()
        })
        
    except ClientError as e:
        return jsonify({
            'success': False,
            'message': f'DynamoDB error: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/dynamodb/list', methods=['GET'])
def list_business_cases():
    """List all saved business cases"""
    if not is_dynamodb_enabled():
        return jsonify({
            'success': False,
            'message': 'DynamoDB is not enabled or configured'
        }), 503
    
    try:
        response = dynamodb_table.scan(
            ProjectionExpression='caseId, projectInfo, createdAt, lastUpdated'
        )
        
        items = response.get('Items', [])
        
        # Sort by lastUpdated descending
        items.sort(key=lambda x: x.get('lastUpdated', ''), reverse=True)
        
        return jsonify({
            'success': True,
            'cases': items
        })
        
    except ClientError as e:
        return jsonify({
            'success': False,
            'message': f'DynamoDB error: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/dynamodb/load/<case_id>', methods=['GET'])
def load_business_case(case_id):
    """Load a specific business case from DynamoDB and restore files from S3"""
    if not is_dynamodb_enabled():
        return jsonify({
            'success': False,
            'message': 'DynamoDB is not enabled or configured'
        }), 503
    
    try:
        response = dynamodb_table.get_item(Key={'caseId': case_id})
        
        if 'Item' not in response:
            return jsonify({
                'success': False,
                'message': 'Business case not found'
            }), 404
        
        case_data = response['Item']
        
        # Restore files from S3 if available
        files_restored = {}
        if is_s3_enabled() and 's3FileKeys' in case_data:
            file_mapping = {
                'itInventory': 'it-infrastructure-inventory.xlsx',
                'atxExcel': 'atx_analysis.xlsx',
                'atxPdf': 'atx_report.pdf',
                'atxPptx': 'atx_business_case.pptx',
                'mra': 'aws-customer-migration-readiness-assessment.md',
                'portfolio': 'application-portfolio.csv'
            }
            
            for key, value in case_data.get('s3FileKeys', {}).items():
                if key == 'rvTool':
                    # Handle multiple RVTools files
                    if isinstance(value, list):
                        rv_restored = []
                        for s3_key in value:
                            filename = os.path.basename(s3_key)
                            local_path = os.path.join(INPUT_DIR, filename)
                            if download_file_from_s3(s3_key, local_path):
                                rv_restored.append(True)
                            else:
                                rv_restored.append(False)
                        files_restored[key] = all(rv_restored)
                    else:
                        # Single RVTools file (backward compatibility)
                        local_path = os.path.join(INPUT_DIR, os.path.basename(value))
                        files_restored[key] = download_file_from_s3(value, local_path)
                elif key in file_mapping:
                    local_path = os.path.join(INPUT_DIR, file_mapping[key])
                    if download_file_from_s3(value, local_path):
                        files_restored[key] = True
                    else:
                        files_restored[key] = False
        
        return jsonify({
            'success': True,
            'case': case_data,
            'filesRestored': files_restored if files_restored else None,
            's3Enabled': is_s3_enabled()
        })
        
    except ClientError as e:
        return jsonify({
            'success': False,
            'message': f'DynamoDB error: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/dynamodb/delete/<case_id>', methods=['DELETE'])
def delete_business_case(case_id):
    """Delete a business case from DynamoDB and S3"""
    if not is_dynamodb_enabled():
        return jsonify({
            'success': False,
            'message': 'DynamoDB is not enabled or configured'
        }), 503
    
    try:
        # Delete from S3 first if enabled
        if is_s3_enabled():
            delete_files_from_s3(case_id)
        
        # Delete from DynamoDB
        dynamodb_table.delete_item(Key={'caseId': case_id})
        
        return jsonify({
            'success': True,
            'message': 'Business case deleted successfully'
        })
        
    except ClientError as e:
        return jsonify({
            'success': False,
            'message': f'DynamoDB error: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/enhance-description', methods=['POST'])
def enhance_description():
    """Enhance project description using AI"""
    try:
        data = request.json
        project_name = data.get('projectName', '')
        customer_name = data.get('customerName', '')
        current_description = data.get('currentDescription', '')
        aws_region = data.get('awsRegion', 'us-east-1')
        
        # If there's existing description, enhance it using AI
        if current_description:
            # Use AWS Bedrock to enhance the description
            try:
                import boto3
                bedrock = boto3.client('bedrock-runtime', region_name=DYNAMODB_REGION)
                
                prompt = f"""You are an AWS migration expert. Create a concise project description for {customer_name}'s AWS migration project. 

User's input:
{current_description}

Instructions:
- Keep it concise and focused (maximum 100 words)
- Expand on the user's key points naturally
- Add relevant AWS migration details
- Keep the user's original requirements prominent
- Target region: {aws_region}
- Write in paragraph form, naturally flowing from the user's input
- Be brief and to the point

Concise description (max 100 words):"""

                response = bedrock.invoke_model(
                    modelId='anthropic.claude-3-haiku-20240307-v1:0',
                    body=json.dumps({
                        "anthropic_version": "bedrock-2023-05-31",
                        "max_tokens": 200,  # Limit tokens for concise output
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ]
                    })
                )
                
                response_body = json.loads(response['body'].read())
                enhanced = response_body['content'][0]['text'].strip()
                
                # Enforce 100-word limit
                words = enhanced.split()
                if len(words) > 100:
                    enhanced = ' '.join(words[:100])
                    print(f"Truncated AI response from {len(words)} to 100 words")
                
            except Exception as ai_error:
                print(f"AI enhancement failed: {str(ai_error)}")
                # Fallback: Concise template (under 100 words)
                enhanced = f"Assess and plan {customer_name}'s migration to AWS in {aws_region}. Analyze current IT environment, VMware workloads, and organizational readiness. Develop migration strategy using 6Rs framework and AWS MAP methodology. Deliver TCO comparison, migration roadmap, risk assessment, and technical recommendations for successful cloud transformation."
        else:
            # Generate new concise description from scratch (under 100 words)
            enhanced = f"Assess and plan {customer_name}'s on-premises infrastructure migration to AWS. Comprehensive analysis of IT environment, VMware workloads, and organizational readiness. Develop migration strategy using 6Rs framework and AWS MAP methodology. Target region: {aws_region}. Deliverables include TCO comparison, migration roadmap, risk assessment, and technical recommendations."
        
        # Final safety check - ensure it's under 100 words
        words = enhanced.split()
        if len(words) > 100:
            enhanced = ' '.join(words[:100])
            print(f"Final truncation: {len(words)} words to 100 words")
        
        return jsonify({
            'success': True,
            'enhancedDescription': enhanced
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

if __name__ == '__main__':
    print(f"Starting Flask API server...")
    print(f"Agents directory: {AGENTS_DIR}")
    print(f"Input directory: {INPUT_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    app.run(debug=True, host='0.0.0.0', port=5000)
