# Quick Reference - New Features

## 🎯 What's New

Four major features added to the AWS Migration Business Case Generator UI:

### 1️⃣ Complete AWS Regions (Feature A)
**Location:** Project Info Step → Target AWS Region dropdown

**What:** All 29 AWS commercial regions now available (excluding GovCloud)

**How to use:**
1. Go to Project Info step
2. Click "Target AWS Region" dropdown
3. Select from 29 regions across all continents

### 2️⃣ AI Description Enhancement (Feature B)
**Location:** Project Info Step → Project Description field

**What:** AI-powered description enhancement that improves your text

**How to use:**
1. Enter Project Name and Customer Name (required)
2. Optionally type initial description
3. Click "Generate with AI" button
4. AI enhances your text (or generates new if empty)

**Key Feature:** Preserves and enhances your input, doesn't replace it!

### 3️⃣ DynamoDB Persistence (Feature C)
**Location:** Header toggle + Top navigation + Results step

**What:** Optional save/load functionality for business cases

**How to use:**

**Setup (one-time):**
```bash
cd ui
./setup-dynamodb.sh
```

**Enable:**
1. Toggle "DynamoDB Persistence" in header (turns green)

**Save:**
1. Generate business case
2. Click "Save to Database" in Results step
3. Case saved with unique ID and timestamp

**Load:**
1. Click "Load Saved Cases" in top navigation
2. Browse, search, filter cases
3. Select and click "Load Selected"

**Edit & Update:**
1. Load a saved case
2. Make changes
3. Regenerate
4. Click "Update in Database"

### 4️⃣ S3 File Storage (Feature D - NEW!)
**Location:** Automatic when enabled

**What:** Optional S3 integration for persistent file storage

**How to use:**

**Setup (one-time):**
```bash
cd ui/backend
export S3_BUCKET_NAME=your-bucket-name
python setup_s3.py
```

**Or use combined setup:**
```bash
cd ui
./setup-storage.sh
```

**Benefits:**
- ✅ Files automatically uploaded to S3 when saving
- ✅ Files automatically restored when loading
- ✅ Files persist permanently
- ✅ Versioning enabled
- ✅ Encrypted at rest

**Visual Indicator:**
- See "Enhanced Storage: DynamoDB + S3 enabled" alert in UI
- "Files backed up to S3" shown when saving

---

## 📋 Quick Commands

### Start Application (Basic)
```bash
# Terminal 1 - Backend
cd ui/backend
python app.py

# Terminal 2 - Frontend
cd ui
npm start
```

### Setup Storage (Optional)
```bash
# Complete setup (DynamoDB + S3)
cd ui
./setup-storage.sh

# Or individual setup
./setup-dynamodb.sh  # DynamoDB only
cd backend && python setup_s3.py  # S3 only
```

### Manual Storage Setup
```bash
# Configure AWS
aws configure

# Create DynamoDB table
cd backend
python setup_dynamodb.py

# Create S3 bucket (optional)
export S3_BUCKET_NAME=your-bucket-name
python setup_s3.py

# Install dependencies
pip install -r requirements.txt
```

---

## 🔍 Feature Locations

| Feature | Location | Button/Control |
|---------|----------|----------------|
| AWS Regions | Project Info Step | "Target AWS Region" dropdown |
| AI Enhancement | Project Info Step | "Generate with AI" button |
| DynamoDB Toggle | Header (top right) | Toggle switch |
| S3 Status | Below header | Success alert (when enabled) |
| Save Case | Results Step | "Save to Database" button |
| Load Cases | Top Navigation | "Load Saved Cases" button |
| Last Updated | Below header | Info alert (when saved) |

---

## 🎨 Visual Indicators

**DynamoDB Status:**
- 🟢 Green "success" = Enabled and working
- ⚫ Gray "stopped" = Disabled or unavailable

**S3 Status:**
- 🟢 "Enhanced Storage: DynamoDB + S3 enabled" = Both active
- 📦 "Files backed up to S3" = Files uploaded successfully

**AI Enhancement:**
- 🔄 Loading spinner = Generating
- ✅ Text updated = Complete

**Save Status:**
- ✅ Green alert = Saved successfully
- ❌ Red alert = Save failed

---

## 📊 Data Storage

### DynamoDB (Metadata)
Each business case includes:
- ✅ Unique Case ID
- ✅ Project information
- ✅ Customer details
- ✅ AWS region
- ✅ Full business case content
- ✅ Selected agents
- ✅ Uploaded files list
- ✅ S3 file keys (if S3 enabled)
- ✅ Execution statistics
- ✅ Created timestamp
- ✅ Last updated timestamp

### S3 (Files - Optional)
Each case folder contains:
- ✅ IT Infrastructure Inventory (Excel)
- ✅ RVTool VMware Assessment (CSV)
- ✅ ATX Analysis Data (Excel)
- ✅ ATX Technical Report (PDF)
- ✅ ATX Business Case (PowerPoint)
- ✅ MRA Document (Markdown)
- ✅ Application Portfolio (CSV - optional)

**Structure:**
```
s3://bucket-name/
├── case-20241124-143022/
│   ├── Test-Data-Set-Demo-Excel-V2.xlsx
│   ├── rvtool.csv
│   └── ...
└── case-20241124-150530/
    └── ...
```

---

## 💡 Pro Tips

### AWS Regions
- Use search in dropdown to find regions quickly
- Region selection affects AI description generation
- Selected region appears in generated business case

### AI Enhancement
- Fill in Project Name and Customer Name first
- Can start with empty description or existing text
- AI adds AWS-specific details and best practices
- Mentions 6Rs framework and MAP methodology
- Falls back to template if API unavailable

### DynamoDB
- Toggle can be turned on/off anytime
- Cases persist even if toggle is off
- Search/filter in saved cases modal
- Delete old cases to save storage
- Costs < $0.01/month for typical usage

### S3 File Storage
- Automatically uploads files when saving
- Automatically restores files when loading
- Files versioned for history
- Old versions cleaned up after 90 days
- Costs ~$0.13/month for 100 cases
- Files encrypted at rest (AES256)

---

## 🚨 Troubleshooting

### DynamoDB Toggle Not Showing
```bash
# Check AWS credentials
aws sts get-caller-identity

# Verify table exists
aws dynamodb describe-table --table-name aws-migration-business-cases

# Check backend logs
```

### AI Enhancement Not Working
- Ensure backend is running on port 5000
- Check Project Name and Customer Name are filled
- Look for errors in browser console
- Feature falls back to template if API fails

### Save Operation Fails
- Verify DynamoDB toggle is enabled (green)
- Check AWS credentials are valid
- Ensure IAM permissions are correct
- Review backend console for errors

### S3 Not Showing as Enabled
```bash
# Check environment variable
echo $S3_BUCKET_NAME

# Verify bucket exists
aws s3 ls s3://your-bucket-name

# Check backend logs for "S3 bucket accessible" message
```

### Files Not Restoring from S3
- Verify S3 is enabled (see success alert)
- Check files exist in S3: `aws s3 ls s3://bucket/case-id/`
- Ensure IAM has s3:GetObject permission
- Review backend logs for download errors

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| `README.md` | Main documentation |
| `DYNAMODB_SETUP.md` | Detailed DynamoDB setup |
| `S3_STORAGE_SETUP.md` | Detailed S3 setup |
| `FEATURES_SUMMARY.md` | Complete feature list |
| `IMPLEMENTATION_NOTES.md` | Technical details |
| `CHANGELOG.md` | Version history |
| `QUICK_REFERENCE.md` | This file |

---

## 🔐 Security Checklist

- [ ] AWS credentials configured (not in code)
- [ ] IAM permissions set correctly
- [ ] DynamoDB encryption enabled (optional)
- [ ] HTTPS in production
- [ ] Regular credential rotation

---

## 💰 Cost Estimate

**Features A & B:** $0 (no AWS services)

**Feature C (DynamoDB):**
- 100 business cases ≈ 10 MB storage = $0.0025/month
- 1000 operations/month = $0.002/month
- **Total: < $0.01/month**

**Feature D (S3 - Optional):**
- 100 cases × 50 MB = 5 GB storage = $0.12/month
- Upload/download operations = $0.01/month
- **Total: ~$0.13/month**

**Combined (DynamoDB + S3):**
- **Total: ~$0.14/month for 100 cases**

---

## ✅ Feature Status

| Feature | Status | Required Setup |
|---------|--------|----------------|
| AWS Regions | ✅ Ready | None |
| AI Enhancement | ✅ Ready | None |
| DynamoDB Persistence | ✅ Ready | AWS credentials + table |
| S3 File Storage | ✅ Ready | AWS credentials + bucket |

---

## 🎓 Learning Resources

**AWS Regions:**
- [AWS Global Infrastructure](https://aws.amazon.com/about-aws/global-infrastructure/)

**DynamoDB:**
- [DynamoDB Documentation](https://docs.aws.amazon.com/dynamodb/)
- [IAM Permissions](https://docs.aws.amazon.com/IAM/latest/UserGuide/)

**AWS Migration:**
- [AWS Migration Hub](https://aws.amazon.com/migration-hub/)
- [AWS MAP Program](https://aws.amazon.com/migration-acceleration-program/)

---

**Need Help?** Check the troubleshooting sections in the documentation files!
