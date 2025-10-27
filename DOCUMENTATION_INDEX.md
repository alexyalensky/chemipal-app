# ChemiPal Documentation - Master Index

## 📚 Complete Documentation Suite

This project includes **six comprehensive documentation files**, each serving a specific purpose:

---

## 1. 📖 README.md - Quick Start Guide

**Purpose**: Get started in 5 minutes

**Best For**:
- First-time setup
- Quick reference
- Understanding what the system does
- Finding the right documentation

**Contents**:
- 5-minute installation guide
- System overview
- Quick troubleshooting
- Documentation roadmap

**When to Use**: 
→ Starting fresh or need quick orientation

---

## 2. 🔧 agent.md - Technical Reference (593 lines)

**Purpose**: Complete technical documentation for developers and AI agents

**Best For**:
- Understanding code architecture
- API reference
- Entity mappings
- Function signatures
- Code examples

**Key Sections**:
- System architecture (9 threaded processes)
- HitoAPI and PulseemAPI reference
- Entity mappings (20+ entities)
- Helper functions documentation
- Data flow diagrams
- Parameter ID patterns
- Development guidelines

**When to Use**:
→ Developing features, debugging code, understanding system internals

---

## 3. 🛠️ INSTRUCTIONS.md - Operations & Development Guide (1000+ lines)

**Purpose**: Step-by-step instructions for everything

**Best For**:
- Installation and setup
- Running and monitoring
- Troubleshooting issues
- Making code improvements
- Testing and deployment

**Key Sections**:

### Part 1: Code Analysis & Improvements
- **10 Critical Issues** with fixes:
  1. Security vulnerabilities (SSL, input validation)
  2. Reliability issues (retry logic, error handling)
  3. Code quality (hard-coded values, logging)
  4. Architecture recommendations
- Each with current code, recommended fix, and priority

### Part 2: Installation & Setup
- Prerequisites and system requirements
- Virtual environment setup
- Configuration (.env file)
- Directory creation
- API connectivity testing
- Entity access verification

### Part 3: Running the Application
- Manual start (development)
- Windows Service deployment
- Task Scheduler alternative
- Service monitoring

### Part 4: Monitoring & Maintenance
- Real-time log monitoring
- Performance monitoring scripts
- Log rotation procedures
- Health check automation

### Part 5: Troubleshooting Guide
- 7 common issues with solutions:
  1. Application won't start
  2. API connection failures
  3. File processing stuck
  4. Validation failures
  5. Thread deaths
  6. High memory usage
  7. Duplicate records

### Part 6: Development Workflow
- Making code changes
- Adding new file types
- Adding new customers
- Code standards and testing

### Part 7: Testing Procedures
- Unit testing examples
- Integration testing
- Manual testing checklist

### Part 8: Deployment Guide
- Pre-deployment checklist
- Deployment steps
- Rollback procedure
- Post-deployment monitoring

**When to Use**:
→ Setting up system, fixing issues, improving code, deploying changes

---

## 4. 💼 CHEMIPAL_BUSINESS_PROCESS.md - Business Documentation (NEW!)

**Purpose**: Understand the business processes and workflows

**Best For**:
- Understanding what ChemiPal does (business-wise)
- Learning the order of operations
- Business rules and validations
- Training new users/developers
- Business analysis

**Key Sections**:

### Executive Summary
- What ChemiPal does (warehouse management hub)
- Business model (supplier → warehouse → customer)
- Key entities and real-world meaning

### Master Data Structure
- Entity relationship diagram
- Suppliers, Contracts, Items, Inventory, Orders
- Critical master data explained

### Complete Process Flow
- Daily operations timeline
- High-level business cycle
- File import → validation → export

### Inventory Receiving Process (INV)
- **7 phases** from file import to ERP export
- All validation rules explained
- Business reasons for each rule
- Data enrichment steps
- Status lifecycle

### Item Definition Process (FITEM)
- Product catalog management
- **6 phases** from import to production
- Validation rules
- Master data linking

### Order Fulfillment Process (ORD)
- Customer order processing
- **9 phases** including manual reference assignment
- Extensive validation (6 rules)
- Inventory reservation
- Shipping documentation

### Supporting Processes
- Supplier master (SPK)
- Item codes (ITM)
- Contracts (CTR)
- Delivery documents (DOC)
- Return inventory (RINV)

### Business Rules & Validations
- Contract-based receiving
- Item catalog compliance
- Inventory availability
- No double shipping
- Reference uniqueness

### Integration Points
- Inbound file integrations (8 file types)
- Outbound file exports (2 types)
- ERP integration architecture

### Exception Handling
- 5 common business scenarios
- System responses
- Required business actions
- Error resolution workflow

**When to Use**:
→ Understanding the business, training, explaining to stakeholders, business analysis

### 5. **NAMAL_BUSINESS_PROCESS.md** - Namal System Documentation 🔄
**NEW!** Comprehensive Namal data transfer system documentation:
- What Namal does (real-time data synchronization)
- Dual-pipeline transfer processes (Entity 105→62, 106→102)
- Validation logic and error handling
- Performance characteristics and business rules
- Block-based data processing
- Real-world examples and use cases

**When to Use**:
→ Understanding Namal's data transfer processes, troubleshooting synchronization issues

---

## 📊 Documentation Comparison Matrix

| Feature | README | agent.md | INSTRUCTIONS.md | CHEMIPAL_BUSINESS_PROCESS.md | NAMAL_BUSINESS_PROCESS.md |
|---------|--------|----------|-----------------|------------------------------|---------------------------|
| **Target Audience** | Everyone | Developers | Operators/Devs | Business Users | System Analysts |
| **Technical Depth** | Low | High | Medium | Low | Medium |
| **Length** | Short | Long | Very Long | Long | Medium |
| **Focus** | Overview | Code | How-to | Business | Process |
| **Best For** | First look | Development | Operations | Understanding | Data Flow |
| **Code Examples** | Minimal | Many | Some | None | Some |
| **Business Rules** | No | Some | No | Extensive | Moderate |
| **Step-by-Step** | Yes | No | Yes | Yes | Yes |

---

## 🎯 Use Case Guide: Which Document to Read?

### "I'm new to this project"
1. Start: **README.md** (5 minutes)
2. Then: **CHEMIPAL_BUSINESS_PROCESS.md** (30 minutes)
3. Finally: **agent.md** (1 hour)

### "I need to install/setup the system"
→ **INSTRUCTIONS.md** - Installation & Setup section

### "The system is broken"
1. **INSTRUCTIONS.md** - Troubleshooting Guide
2. **agent.md** - Technical Reference (for deeper debugging)

### "I need to add a new feature"
1. **agent.md** - Understand current architecture
2. **CHEMIPAL_BUSINESS_PROCESS.md** - Understand business impact
3. **INSTRUCTIONS.md** - Development Workflow

### "I want to improve the code"
→ **INSTRUCTIONS.md** - Code Analysis section (10 improvements)

### "I need to explain this to management"
→ **CHEMIPAL_BUSINESS_PROCESS.md** - Executive Summary

### "I need to train a new developer"
1. **README.md** - System overview
2. **CHEMIPAL_BUSINESS_PROCESS.md** - Business context
3. **agent.md** - Technical details
4. **INSTRUCTIONS.md** - Development practices

### "I need to understand a specific entity/function"
→ **agent.md** - Entity Mapping and Function Reference

### "I need to know why a validation fails"
→ **CHEMIPAL_BUSINESS_PROCESS.md** - Business Rules section

### "I need to understand Namal data transfers"
→ **NAMAL_BUSINESS_PROCESS.md** - Complete Namal process documentation

### "I need to deploy to production"
→ **INSTRUCTIONS.md** - Deployment Guide

---

## 📋 Quick Reference Cards

### Common Entities Quick Reference

| Entity | Name | Purpose | Document Reference |
|--------|------|---------|-------------------|
| 1 | FITEM | Product catalog | agent.md §3, BUSINESS §5 |
| 4 | SPK | Suppliers | agent.md §3, BUSINESS §7 |
| 7 | CTR | Contracts | agent.md §3, BUSINESS §7 |
| 8 | INV | Inventory | agent.md §3, BUSINESS §4 |
| 10 | ORD | Orders | agent.md §3, BUSINESS §6 |
| 19 | DOC | Delivery Docs | agent.md §3, BUSINESS §7 |
| 28 | FITEMCHECK | Item Validation | agent.md §3, BUSINESS §5 |
| 33 | INVFILE | INV Validation | agent.md §3, BUSINESS §4 |
| 34 | ORDFILE | ORD Validation | agent.md §3, BUSINESS §6 |

### Common Operations Quick Reference

| Task | Command/Location | Document |
|------|------------------|----------|
| Start system | `python main.py` | INSTRUCTIONS §4 |
| Check logs | `Get-Content log\log.txt -Wait` | INSTRUCTIONS §5 |
| Test API | `python test_connection.py` | INSTRUCTIONS §2 |
| Health check | `python healthcheck.py` | INSTRUCTIONS §5 |
| Add file type | Edit `main.py` thread | INSTRUCTIONS §7 |
| Deploy | Follow checklist | INSTRUCTIONS §9 |

### Validation Failure Quick Reference

| Error Message (Hebrew) | Meaning | Fix | Document |
|------------------------|---------|-----|----------|
| "לא תקין - קוד ספק לא תואם" | Invalid supplier code | Add to SPK | BUSINESS §8, INSTRUCTIONS §6.4 |
| "לא תקין - אין חוזה בתוקף" | No valid contract | Update CTR | BUSINESS §8 |
| "לא תקין - לא קיים מק\"ט כמיפל" | Item doesn't exist | Add to FITEM | BUSINESS §8 |
| "נבדק - תז לא תקין" | Invalid ID number | Fix ID format | agent.md §9 |

---

## 🔄 Process Flow Quick Links

### Inventory Process
- Overview: [BUSINESS_PROCESS.md §4](#)
- Validation Rules: [BUSINESS_PROCESS.md §4.3](#)
- Technical Details: [agent.md - Data Flow](#)
- Troubleshooting: [INSTRUCTIONS.md §6.3](#)

### Order Process
- Overview: [BUSINESS_PROCESS.md §6](#)
- Reference Assignment: [BUSINESS_PROCESS.md §6.1](#)
- Validation Rules: [BUSINESS_PROCESS.md §6.4](#)
- Technical Details: [agent.md - OrdFunctions](#)

### Item Process
- Overview: [BUSINESS_PROCESS.md §5](#)
- Validation: [BUSINESS_PROCESS.md §5.4](#)
- Technical Details: [agent.md - FitemFunctions](#)

---

## 🔍 Search Guide

### Finding Information

**Looking for**: Business rule/validation  
**Search in**: CHEMIPAL_BUSINESS_PROCESS.md - Section §8 (Business Rules)

**Looking for**: Entity purpose/mapping  
**Search in**: agent.md - Section §3 (Entity Mapping) or BUSINESS_PROCESS.md - Section §2

**Looking for**: Function signature/parameters  
**Search in**: agent.md - Section §4 (Helper Functions)

**Looking for**: Installation steps  
**Search in**: INSTRUCTIONS.md - Section §2 (Installation & Setup)

**Looking for**: Error message explanation  
**Search in**: BUSINESS_PROCESS.md - Section §10 (Exception Handling)

**Looking for**: Code improvement  
**Search in**: INSTRUCTIONS.md - Section §1 (Code Analysis)

**Looking for**: Thread/process info  
**Search in**: agent.md - Section §2 (Threading Model)

---

## 📈 Reading Order by Role

### **New Developer**
```
Day 1: README.md → CHEMIPAL_BUSINESS_PROCESS.md (Executive Summary)
Day 2: CHEMIPAL_BUSINESS_PROCESS.md (Complete)
Day 3: agent.md (Architecture & Entities)
Day 4: INSTRUCTIONS.md (Development Workflow)
Week 2: Deep dive into specific modules
```

### **Operations/DevOps**
```
Day 1: README.md → INSTRUCTIONS.md (Installation)
Day 2: INSTRUCTIONS.md (Monitoring & Troubleshooting)
Day 3: CHEMIPAL_BUSINESS_PROCESS.md (Overview)
Ongoing: INSTRUCTIONS.md as reference
```

### **Business Analyst**
```
Day 1: README.md → CHEMIPAL_BUSINESS_PROCESS.md
Day 2: Deep dive into specific processes
Reference: CHEMIPAL_BUSINESS_PROCESS.md §8 (Business Rules)
```

### **System Administrator**
```
Day 1: README.md → INSTRUCTIONS.md (Installation & Setup)
Day 2: INSTRUCTIONS.md (Monitoring, Deployment)
Day 3: CHEMIPAL_BUSINESS_PROCESS.md (System Overview)
Reference: INSTRUCTIONS.md (Troubleshooting)
```

---

## 📞 Support Resources

### Internal Documentation
1. **README.md** - Start here
2. **CHEMIPAL_BUSINESS_PROCESS.md** - Business questions
3. **NAMAL_BUSINESS_PROCESS.md** - Namal data transfer questions
4. **agent.md** - Technical questions
5. **INSTRUCTIONS.md** - How-to questions

### Log Files
- Main log: `log/log.txt`
- Error output: `log/stderr.txt`
- Standard output: `log/stdout.txt`

### Diagnostic Tools
- Connection test: `test_connection.py`
- Entity verification: `verify_entities.py`
- Health check: `healthcheck.py`
- Process monitor: `monitor.py`

---

## 🎓 Learning Path

### **Beginner** (Week 1)
- [ ] Read README.md
- [ ] Understand BUSINESS_PROCESS.md Executive Summary
- [ ] Review Entity Relationship Diagram
- [ ] Follow INSTRUCTIONS.md Installation

### **Intermediate** (Week 2-3)
- [ ] Study complete BUSINESS_PROCESS.md
- [ ] Review agent.md Architecture section
- [ ] Understand all validation rules
- [ ] Practice troubleshooting scenarios

### **Advanced** (Month 1+)
- [ ] Complete agent.md technical reference
- [ ] Study all helper functions
- [ ] Review code improvement recommendations
- [ ] Understand threading model
- [ ] Practice code modifications

---

## 📝 Documentation Maintenance

### When to Update Each Document

**README.md**: 
- System requirements change
- Installation steps change
- Quick start broken

**agent.md**:
- New entity added
- New function created
- API changes
- Architecture changes

**INSTRUCTIONS.md**:
- New installation steps
- New troubleshooting scenarios
- Code improvements implemented
- Deployment process changes

**CHEMIPAL_BUSINESS_PROCESS.md**:
- Business rules change
- New process added
- Validation rules change
- Integration points change

---

## 🎯 Document Version Control

| Document | Version | Last Updated | Lines | Status |
|----------|---------|--------------|-------|--------|
| README.md | 1.0 | 2024-10-22 | ~300 | ✅ Complete |
| agent.md | 1.0 | 2024-10-22 | 593 | ✅ Complete |
| INSTRUCTIONS.md | 1.0 | 2024-10-22 | ~1000 | ✅ Complete |
| CHEMIPAL_BUSINESS_PROCESS.md | 1.0 | 2024-10-22 | ~1200 | ✅ Complete |
| NAMAL_BUSINESS_PROCESS.md | 1.0 | 2024-10-22 | ~800 | ✅ Complete |
| DOCUMENTATION_INDEX.md | 1.0 | 2024-10-22 | ~400 | ✅ Complete |

---

## 🔗 External References

- **Hito API Documentation**: Contact Hito support
- **Python 3.8+ Documentation**: https://docs.python.org/3/
- **Windows Service Management**: NSSM documentation
- **CSV File Format**: RFC 4180

---

**This Index Last Updated**: 2024-10-22  
**Total Documentation**: ~4,100+ lines across 6 files  
**Maintenance**: Review quarterly or on major changes


