#!/bin/bash
#
# Cleanup/Rollback Script for Business Case Generator - Option 4
# Removes all AWS resources created by CDK deployment
#

set +e  # Don't exit on error - we want to try deleting all resources

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

echo_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo ""
echo "=========================================="
echo "Business Case Generator - Cleanup/Rollback"
echo "Option 4: Simple ALB Architecture"
echo "=========================================="
echo ""

# Get AWS info
echo_info "Checking AWS credentials..."
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>&1)
AWS_CLI_EXIT_CODE=$?

if [ $AWS_CLI_EXIT_CODE -ne 0 ]; then
    echo_error "Cannot get AWS account ID. AWS CLI error:"
    echo_error "$AWS_ACCOUNT_ID"
    echo_error "Please ensure AWS credentials are configured."
    exit 1
fi

if [ -z "$AWS_ACCOUNT_ID" ]; then
    echo_error "AWS account ID is empty. Please configure AWS CLI."
    exit 1
fi

export AWS_ACCOUNT_ID
export AWS_REGION=${AWS_REGION:-us-east-1}

echo_info "AWS Account ID: $AWS_ACCOUNT_ID"
echo_info "AWS Region: $AWS_REGION"
echo ""

echo_warn "This will DELETE all resources created by the deployment:"
echo_warn "  - CloudFormation stack (VPC, ECS, ALB, etc.)"
echo_warn "  - S3 bucket contents (input and output files)"
echo_warn "  - DynamoDB table data (all saved cases)"
echo_warn "  - ECR repository and Docker images"
echo ""
echo_error "This action CANNOT be undone!"
echo ""

read -p "Are you sure you want to proceed? Type 'yes' to confirm: " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo_info "Cleanup cancelled"
    exit 0
fi

echo ""
echo_info "Starting cleanup..."

# ============================================================================
# Step 1: Empty S3 Buckets (required before stack deletion)
# ============================================================================
echo ""
echo_info "Step 1: Emptying S3 buckets..."

for bucket in "business-case-input-${AWS_ACCOUNT_ID}-${AWS_REGION}" \
              "business-case-output-${AWS_ACCOUNT_ID}-${AWS_REGION}"; do
    if aws s3 ls "s3://$bucket" 2>/dev/null; then
        echo_info "  Emptying bucket: $bucket"
        if aws s3 rm "s3://$bucket" --recursive 2>/dev/null; then
            echo_info "  ✓ Bucket $bucket emptied"
        else
            echo_error "  Failed to empty bucket $bucket"
        fi
    else
        echo_warn "  Bucket $bucket not found, skipping"
    fi
done

# ============================================================================
# Step 2: Delete ECR Repository images (required before stack deletion)
# ============================================================================
echo ""
echo_info "Step 2: Deleting ECR repository images..."

# Find all ECR repositories created by CDK (both simple and full stack)
for pattern in "businesscasegeneratorstack" "businesscasegeneratorsimplestack"; do
    ECR_REPOS=$(aws ecr describe-repositories --region $AWS_REGION --query "repositories[?contains(repositoryName, '$pattern')].repositoryName" --output text 2>/dev/null)
    
    for ECR_REPO in $ECR_REPOS; do
        if [ -n "$ECR_REPO" ]; then
            echo_info "  Found ECR repository: $ECR_REPO"
            # Delete all images first
            IMAGE_IDS=$(aws ecr list-images --repository-name "$ECR_REPO" --region $AWS_REGION --query 'imageIds[*]' --output json 2>/dev/null)
            if [ "$IMAGE_IDS" != "[]" ] && [ -n "$IMAGE_IDS" ]; then
                echo_info "  Deleting images from $ECR_REPO..."
                aws ecr batch-delete-image --repository-name "$ECR_REPO" --region $AWS_REGION --image-ids "$IMAGE_IDS" >/dev/null 2>&1
                echo_info "  ✓ Images deleted from $ECR_REPO"
            fi
            # Now delete the repository
            if aws ecr delete-repository --repository-name "$ECR_REPO" --region $AWS_REGION --force 2>/dev/null; then
                echo_info "  ✓ ECR repository $ECR_REPO deleted"
            else
                echo_error "  Failed to delete ECR repository $ECR_REPO"
            fi
        fi
    done
done

# ============================================================================
# Step 3: Delete CloudFormation Stack (using CloudFormation directly)
# ============================================================================
echo ""
echo_info "Step 3: Deleting CloudFormation stack..."

# Try both stack names (simple and full)
for STACK_NAME in "BusinessCaseGeneratorStack" "BusinessCaseGeneratorSimpleStack"; do
    if aws cloudformation describe-stacks --stack-name $STACK_NAME --region $AWS_REGION &>/dev/null; then
        echo_info "  Deleting stack $STACK_NAME..."
        echo_warn "  This may take 5-10 minutes..."
        
        if aws cloudformation delete-stack --stack-name $STACK_NAME --region $AWS_REGION; then
            echo_info "  ✓ Stack deletion initiated"
            echo_info "  Waiting for stack deletion to complete..."
            aws cloudformation wait stack-delete-complete --stack-name $STACK_NAME --region $AWS_REGION 2>/dev/null
            echo_info "  ✓ Stack $STACK_NAME deleted"
        else
            echo_error "  Failed to delete stack $STACK_NAME"
        fi
    else
        echo_warn "  Stack $STACK_NAME not found, skipping"
    fi
done

# ============================================================================
# Step 4: Delete S3 Buckets (now that they're empty)
# ============================================================================
echo ""
echo_info "Step 4: Deleting S3 buckets..."

for bucket in "business-case-input-${AWS_ACCOUNT_ID}-${AWS_REGION}" \
              "business-case-output-${AWS_ACCOUNT_ID}-${AWS_REGION}"; do
    if aws s3 ls "s3://$bucket" 2>/dev/null; then
        echo_info "  Deleting bucket: $bucket"
        if aws s3 rb "s3://$bucket" 2>/dev/null; then
            echo_info "  ✓ Bucket $bucket deleted"
        else
            echo_error "  Failed to delete bucket $bucket (may still have objects)"
        fi
    else
        echo_warn "  Bucket $bucket not found, skipping"
    fi
done

# ============================================================================
# Step 5: Delete DynamoDB Table (optional - has RETAIN policy)
# ============================================================================
echo ""
echo_info "Step 5: Checking DynamoDB table..."

if aws dynamodb describe-table --table-name business-case-cases --region $AWS_REGION &>/dev/null; then
    echo_warn "  DynamoDB table 'business-case-cases' still exists"
    echo_warn "  This table has a RETAIN policy and contains all your saved cases"
    echo ""
    read -p "  Delete DynamoDB table? This will delete ALL saved cases. (y/N): " DELETE_TABLE
    if [[ $DELETE_TABLE =~ ^[Yy]$ ]]; then
        if aws dynamodb delete-table --table-name business-case-cases --region $AWS_REGION; then
            echo_info "  ✓ DynamoDB table deletion initiated"
        else
            echo_error "  Failed to delete DynamoDB table"
        fi
    else
        echo_info "  DynamoDB table kept (you can delete it manually later)"
    fi
else
    echo_info "  ✓ DynamoDB table already deleted"
fi

# ============================================================================
# Step 6: Clean up CDK bootstrap (optional)
# ============================================================================
echo ""
echo_info "Step 6: CDK Bootstrap cleanup..."
echo_warn "  CDK bootstrap stack (CDKToolkit) is shared across deployments"
echo_warn "  Only delete it if you're not using CDK for other projects"
echo ""
read -p "  Delete CDK bootstrap stack? (y/N): " DELETE_BOOTSTRAP
if [[ $DELETE_BOOTSTRAP =~ ^[Yy]$ ]]; then
    if aws cloudformation delete-stack --stack-name CDKToolkit --region $AWS_REGION; then
        echo_info "  ✓ CDK bootstrap stack deletion initiated"
    else
        echo_error "  Failed to delete CDK bootstrap stack"
    fi
else
    echo_info "  CDK bootstrap stack kept"
fi

# ============================================================================
# Summary
# ============================================================================
echo ""
echo "=========================================="
echo_info "✓ Cleanup Complete!"
echo "=========================================="
echo ""
echo_info "Resources deleted:"
echo_info "  ✓ ECR repository (images deleted first)"
echo_info "  ✓ CloudFormation stack (VPC, ECS, ALB, etc.)"
echo_info "  ✓ S3 buckets (emptied and deleted)"
if [[ $DELETE_TABLE =~ ^[Yy]$ ]]; then
    echo_info "  ✓ DynamoDB table"
else
    echo_warn "  ⊘ DynamoDB table (kept)"
fi
echo ""
echo_info "Note: Some resources may take a few minutes to fully delete."
echo ""
echo_info "To verify cleanup:"
echo_info "  aws cloudformation list-stacks --region $AWS_REGION"
echo_info "  aws s3 ls | grep business-case"
echo_info "  aws dynamodb list-tables --region $AWS_REGION"
echo ""
