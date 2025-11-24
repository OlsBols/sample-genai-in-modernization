# Documentation Index

## Quick Navigation

### 🎯 Start Here
1. **[README.md](README.md)** - Main project documentation, features, and installation
2. **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Project layout and architecture

### 💻 Web UI
3. **[ui/README.md](ui/README.md)** - Complete UI documentation
4. **[ui/QUICK_REFERENCE.md](ui/QUICK_REFERENCE.md)** - Quick start guide for UI features

### 🗄️ Optional Storage (DynamoDB + S3)
5. **[ui/DYNAMODB_SETUP.md](ui/DYNAMODB_SETUP.md)** - Save/load business cases
6. **[ui/S3_STORAGE_SETUP.md](ui/S3_STORAGE_SETUP.md)** - Automatic file backup

### 📋 Framework References (Used by Agents)
7. `input/aws-migration-strategy-6rs-framework.md` - 6Rs framework
8. `input/aws-migration-plan-framework.md` - MAP phases
9. `input/aws-customer-migration-readiness-assessment.md` - MRA template

---

## Documentation Purpose

| Document | Purpose | Audience |
|----------|---------|----------|
| **README.md** | Main documentation, installation, usage | Everyone |
| **PROJECT_STRUCTURE.md** | Architecture, file layout, data flow | Developers |
| **ui/README.md** | Web UI setup and usage | UI users |
| **ui/QUICK_REFERENCE.md** | Quick tips and troubleshooting | UI users |
| **ui/DYNAMODB_SETUP.md** | DynamoDB persistence setup | Advanced users |
| **ui/S3_STORAGE_SETUP.md** | S3 file storage setup | Advanced users |

---

## What Was Removed (v1 Cleanup)

The following redundant documentation was removed to simplify the project:

- ❌ `EXECUTIVE_SUMMARY.md` - Outdated, info now in README
- ❌ `agents/WORKFLOW.md` - Info now in PROJECT_STRUCTURE
- ❌ `ui/UI_SUMMARY.md` - Redundant with ui/README
- ❌ `ui/CHANGELOG.md` - Not needed for v1
- ❌ `ui/FEATURES_SUMMARY.md` - Info now in ui/README
- ❌ `ui/IMPLEMENTATION_NOTES.md` - Too technical, not needed
- ❌ `ui/S3_INTEGRATION_SUMMARY.md` - Redundant with S3_STORAGE_SETUP
- ❌ `test/README.md` - Not needed

---

## Quick Start Paths

### Path 1: Command Line (Fastest)
1. Read [README.md](README.md) - Installation section
2. Install dependencies
3. Run `python agents/aws_business_case.py`

### Path 2: Web UI (Recommended)
1. Read [README.md](README.md) - Installation section
2. Read [ui/README.md](ui/README.md) - UI setup
3. Start backend and frontend
4. Access http://localhost:3000

### Path 3: With Persistence (Advanced)
1. Follow Path 2
2. Read [ui/DYNAMODB_SETUP.md](ui/DYNAMODB_SETUP.md)
3. Read [ui/S3_STORAGE_SETUP.md](ui/S3_STORAGE_SETUP.md)
4. Run setup scripts

---

## File Count Summary

**Total Essential Documentation: 6 files**
- 2 main docs (README, PROJECT_STRUCTURE)
- 2 UI docs (README, QUICK_REFERENCE)
- 2 optional setup guides (DynamoDB, S3)

**Plus 3 framework files** (used by agents, not user docs)

**Total: 9 documentation files** (down from 17+)

---

## Need Help?

1. **Getting Started?** → [README.md](README.md)
2. **Understanding Architecture?** → [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
3. **Using the UI?** → [ui/README.md](ui/README.md)
4. **Quick Tips?** → [ui/QUICK_REFERENCE.md](ui/QUICK_REFERENCE.md)
5. **Setting up Storage?** → [ui/DYNAMODB_SETUP.md](ui/DYNAMODB_SETUP.md) or [ui/S3_STORAGE_SETUP.md](ui/S3_STORAGE_SETUP.md)
