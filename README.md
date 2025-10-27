# ChemiPal Integration System

A multi-threaded Python application that synchronizes data between Hito API instances and processes CSV file imports/exports for inventory, orders, and supplier management.

## 📚 Documentation

This project has **six comprehensive documentation files**:

### 1. **DOCUMENTATION_INDEX.md** - Master Guide 📋
**START HERE!** Complete navigation guide to all documentation:
- Which document to read for your needs
- Quick reference cards
- Learning paths by role
- Search guide

**Use this for**: Finding the right information quickly

### 2. **agent.md** - Technical Reference 🔧
Complete technical documentation for developers and AI agents:
- System architecture and threading model
- Entity mappings and data flows
- API reference and function signatures
- Business logic and validation rules
- Code examples and patterns

**Use this for**: Understanding the codebase, debugging, adding features

### 3. **INSTRUCTIONS.md** - Operations & Development Guide 🛠️
Step-by-step instructions for all aspects of the system:
- **Code Analysis**: 10 critical improvement recommendations with code examples
- **Installation**: Complete setup from scratch
- **Configuration**: Environment variables and validation
- **Running**: Manual and production deployment
- **Monitoring**: Log analysis, health checks, performance monitoring
- **Troubleshooting**: 7 common issues with solutions
- **Development**: How to make changes and add features
- **Testing**: Unit and integration testing procedures
- **Deployment**: Production deployment and rollback

**Use this for**: Setting up, operating, maintaining, and improving the system

### 4. **CHEMIPAL_BUSINESS_PROCESS.md** - Business Documentation 💼
**NEW!** Comprehensive business process documentation:
- What ChemiPal does (warehouse management)
- Complete process flows (Inventory, Orders, Items)
- Business rules and validations explained
- Real-world examples and use cases
- Exception handling scenarios
- Integration architecture

**Use this for**: Understanding the business, training, explaining to stakeholders

### 5. **NAMAL_BUSINESS_PROCESS.md** - Namal System Documentation 🔄
**NEW!** Comprehensive Namal data transfer system documentation:
- What Namal does (real-time data synchronization)
- Dual-pipeline transfer processes (Entity 105→62, 106→102)
- Validation logic and error handling
- Performance characteristics and business rules
- Block-based data processing

**Use this for**: Understanding Namal's data transfer processes, troubleshooting synchronization issues

### 6. **This README** - Quick Start Guide 🚀

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Windows 10/11 or Windows Server 2016+
- Access to Hito API endpoints
- Network folders for file processing

### Installation (5 minutes)

1. **Set up virtual environment**:
```bash
python -m venv ..\chemipal-env
..\chemipal-env\Scripts\activate.bat
pip install requests python-dotenv
```

2. **Create `.env` file** with your credentials:
```bash
CHEMIPAL_DOMAIN=https://your-domain.hito.com
CHEMIPAL_API_KEY=your_api_key_here
# ... (see INSTRUCTIONS.md for full template)
```

3. **Create required folders**:
```bash
mkdir log
mkdir C:\FTP_Clients\chemipal\In
mkdir C:\FTP_Clients\chemipal\In\backlog
```

4. **Test connection**:
```bash
python test_connection.py
```

5. **Run**:
```bash
python main.py
```

## 📊 System Overview

### What It Does
- **File Import**: Processes CSV files (INV, ORD, FITEM, SPK, etc.) from FTP folder
- **Validation**: Multi-stage validation of all imported data
- **Data Transfer**: Synchronizes records between entities with enrichment
- **Export**: Generates CSV files for external systems
- **Multi-Tenant**: Manages 8+ customer integrations simultaneously

### Architecture
- **9 concurrent threads** running different processes
- **File-based input** via FTP/network folders
- **REST API** communication with Hito systems
- **Event-driven** validation and data flows

### Key Entities
| Entity | Purpose | Files |
|--------|---------|-------|
| 1 | FITEM - Item definitions | FITEM.csv |
| 4 | SPK - Suppliers | SPK.csv |
| 8 | INV - Inventory | INV.csv |
| 10 | ORD - Orders | ORD.csv |
| 19 | DOC - Documents | DOC.csv |

## 🔍 Code Quality Summary

### ✅ Strengths
- Multi-threaded architecture handles concurrent operations
- Comprehensive logging for all operations
- Batch processing for efficiency
- Extensive validation rules
- Handles multiple customer instances

### ⚠️ Areas for Improvement

**High Priority**:
1. **Security**: SSL verification disabled - needs fixing
2. **Reliability**: No retry logic for network failures
3. **Error Handling**: Using `.info()` for errors instead of `.error()`
4. **Thread Safety**: No coordination between threads

**Medium Priority**:
5. Hard-coded entity/parameter IDs
6. Duplicate code patterns
7. No structured logging
8. Missing input validation

**See INSTRUCTIONS.md Section "Code Analysis" for detailed recommendations and fixes**

## 📈 Monitoring

### Check System Health
```bash
# View real-time logs
Get-Content log\log.txt -Wait -Tail 50

# Check for errors
findstr /i "ERROR\|EXCEPTION" log\log.txt

# Monitor process
python monitor.py
```

### Health Indicators
- ✅ 9-10 threads running
- ✅ Log activity within last 5 minutes
- ✅ No stuck files older than 2 hours
- ✅ Memory usage < 500MB

## 🐛 Common Issues

### Files Not Processing
**Solution**: Check folder permissions and file encoding (UTF-8)

### API Errors
**Solution**: Verify credentials in `.env`, test with `test_connection.py`

### Validation Failures
**Solution**: Check error message in logs (e.g., "לא תקין - קוד ספק לא תואם" means supplier code not found)

### Thread Deaths
**Solution**: Restart application, check logs for exceptions

**See INSTRUCTIONS.md "Troubleshooting Guide" for complete solutions**

## 🛠️ Development

### Making Changes

1. **Create branch**: `git checkout -b feature/your-feature`
2. **Make changes**: Edit Python files
3. **Test**: Run unit tests and integration tests
4. **Commit**: `git commit -m "feat: description"`
5. **Deploy**: Follow deployment guide

### Adding New File Type

```python
# Add to appropriate thread function
new_import = PreNames("NEWFILE", entity_id, api, source, dest)
result = new_import.creating_body_to_update()
```

### Adding New Customer

1. Add credentials to `.env`
2. Create API instance in `main.py`
3. Create processing function
4. Add thread

**See INSTRUCTIONS.md "Development Workflow" for detailed guides**

## 📦 File Structure

```
chemipal new app/
├── main.py                 # Entry point, 9 threaded processes
├── HitoAPI.py             # Hito REST API wrapper
├── helpers.py             # Data transfer utilities
├── PreNames.py            # CSV file import handler
├── OrdFunctions.py        # Order processing & validation
├── InvFunctions.py        # Inventory processing & validation
├── FitemFunctions.py      # Item processing & validation
├── INVORD.py              # CSV export handler
├── OrderNumbering.py      # Order numbering logic
├── g1_functions.py        # G1 user creation
├── PulseemAPI.py          # SMS API wrapper
├── check_volunteer_exists.py  # Volunteer validation
├── .env                   # Configuration (not in git)
├── log/                   # Log files
└── Documentation:
    ├── README.md          # This file - Quick start
    ├── agent.md           # Technical reference
    └── INSTRUCTIONS.md    # Complete operations guide
```

## 🎯 Next Steps

### For First-Time Setup
1. Read **INSTRUCTIONS.md "Installation & Setup"** section
2. Follow step-by-step installation
3. Run validation scripts
4. Monitor first 24 hours

### For Developers
1. Read **agent.md** for technical understanding
2. Review **INSTRUCTIONS.md "Code Analysis"** for improvements
3. Set up development environment
4. Run unit tests

### For Operations
1. Learn monitoring from **INSTRUCTIONS.md "Monitoring"** section
2. Set up health checks
3. Configure log rotation
4. Install as Windows Service

### For Troubleshooting
1. Go to **INSTRUCTIONS.md "Troubleshooting Guide"**
2. Find your issue
3. Follow diagnosis steps
4. Apply solution

## 📞 Support

### Issue Priority

**P1 - Critical (System Down)**:
- Application won't start
- All threads dead
- API completely unavailable

**P2 - High (Degraded Service)**:
- Some threads dying
- Validation failures
- File processing stuck

**P3 - Medium (Minor Issues)**:
- Single customer integration issue
- Non-critical validation errors
- Performance degradation

**P4 - Low (Enhancements)**:
- Feature requests
- Documentation updates
- Code quality improvements

### Getting Help

1. **Check logs**: `log\log.txt`
2. **Run health check**: `python healthcheck.py`
3. **Consult documentation**:
   - INSTRUCTIONS.md - Troubleshooting Guide
   - agent.md - Technical details
4. **Contact support** (see INSTRUCTIONS.md)

## 🔒 Security Notes

- **Never commit** `.env` file to version control
- **Rotate API keys** regularly
- **Use SSL** in production (currently disabled - see INSTRUCTIONS.md)
- **Restrict folder access** to service account only
- **Monitor logs** for unusual activity

## 📝 Contributing

1. Follow existing code style
2. Add tests for new features
3. Update documentation
4. Test thoroughly before deploying

See **INSTRUCTIONS.md "Development Workflow"** for complete guidelines.

## 📜 License

[Your License Here]

## 🙏 Acknowledgments

Built for ChemiPal using HitoAPI platform.

---

**Version**: 1.0  
**Last Updated**: 2024-10-21  
**Status**: Production

For detailed information, see:
- 📘 **agent.md** - Complete technical reference
- 📗 **INSTRUCTIONS.md** - Step-by-step operations guide


