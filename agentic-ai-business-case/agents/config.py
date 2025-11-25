input_folder_dir_path =  "/Users/arptsha/Downloads/map-genai-use-cases/agentic-ai-business-case/"

output_folder_dir_path = "/Users/arptsha/Downloads/map-genai-use-cases/agentic-ai-business-case/output/"

#Bedrock Model Configuration

# Option 1: Claude 3 Sonnet (4096 max tokens) - Works with on-demand, STABLE
model_id_claude3_7="anthropic.claude-3-sonnet-20240229-v1:0"
max_tokens_default = 4096

# Option 2: Claude 3.5 Sonnet with Cross-Region Inference (8192 max tokens)
# Requires model access enabled in Bedrock Console - see CLAUDE_35_SETUP.md
# Uncomment these lines after enabling model access:
# model_id_claude3_7="us.anthropic.claude-3-5-sonnet-20241022-v2:0"
# max_tokens_default = 8192

# Alternative models:
# model_id_claude3_7="anthropic.claude-3-haiku-20240307-v1:0"  # Faster, cheaper (4096 tokens)

model_id_nova_ite="us.amazon.nova-lite-v1:0"
model_temperature=0.3

# Multi-stage generation settings
ENABLE_MULTI_STAGE = True  # Generate business case in multiple stages
MAX_TOKENS_BUSINESS_CASE = max_tokens_default  # Will use 8192 if Claude 3.5

# Data limits to prevent context window overflow and max_tokens errors
# Reduced significantly to prevent agent output from exceeding token limits
MAX_ROWS_RVTOOLS = 2500  # Max VMs to analyze from RVTools (increased to 2500 to capture all VMs in typical datasets)
MAX_ROWS_IT_INVENTORY = 1500  # Max rows per sheet in IT inventory (reduced from 3000)
MAX_ROWS_PORTFOLIO = 1000  # Max applications in portfolio (reduced from 2000)
