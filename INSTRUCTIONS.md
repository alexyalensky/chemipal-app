# ChemiPal Integration System - Complete Instructions & Best Practices

## Table of Contents
1. [Code Analysis & Improvement Recommendations](#code-analysis--improvement-recommendations)
2. [Installation & Setup](#installation--setup)
3. [Configuration](#configuration)
4. [Running the Application](#running-the-application)
5. [Monitoring & Maintenance](#monitoring--maintenance)
6. [Troubleshooting Guide](#troubleshooting-guide)
7. [Development Workflow](#development-workflow)
8. [Testing Procedures](#testing-procedures)
9. [Deployment Guide](#deployment-guide)

---

# Code Analysis & Improvement Recommendations

## 🔴 Critical Issues to Address

### 1. **Security Vulnerabilities**

**Issue**: API requests disable SSL verification
```python
# Current code in HitoAPI.py and PulseemAPI.py
requests.post(url=url, headers=self.HEADERS, json=body, verify=False)
```

**Recommendation**:
- **Enable SSL verification** for production
- If self-signed certificates are required, use certificate bundle path:
  ```python
  requests.post(url=url, headers=self.HEADERS, json=body, verify='/path/to/cert.pem')
  ```
- Add SSL warning suppression only if absolutely necessary:
  ```python
  import urllib3
  urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
  ```

**Priority**: HIGH - Security risk

---

### 2. **Error Handling & Resilience**

**Issue**: No retry logic for network failures
```python
# Current pattern
try:
    response = api.get_records(...)
except Exception as e:
    logging.info(f"Error: {e}")
    return
```

**Recommendation**:
```python
# Implement exponential backoff retry
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def create_retry_session():
    session = requests.Session()
    retry = Retry(
        total=3,
        read=3,
        connect=3,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 504)
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session
```

**Priority**: HIGH - Production stability

---

### 3. **Hard-Coded Values**

**Issue**: Entity IDs and parameter IDs are hard-coded throughout
```python
# Examples from main.py
origin_entity_id=1, dest_entity_id=8
origin_param_id_to_find=250, dest_param_id_to_find=609
```

**Recommendation**:
```python
# Create configuration file: config.py
class EntityConfig:
    FITEM = 1
    INV = 8
    ORD = 10
    # ... etc

class ParamConfig:
    FITEM_BARCODE = 250
    INV_BARCODE = 609
    # ... etc

# Usage:
entity2entity(
    api=chemipal,
    origin_entity_id=EntityConfig.FITEM,
    dest_entity_id=EntityConfig.INV,
    origin_param_id_to_find=ParamConfig.FITEM_BARCODE,
    dest_param_id_to_find=ParamConfig.INV_BARCODE,
    ...
)
```

**Priority**: MEDIUM - Maintainability

---

### 4. **Resource Management**

**Issue**: File handles and HTTP connections not properly closed
```python
# PreNames.py - no explicit file closing
with open(f'{self.path}/{file}', encoding='UTF8') as data_file:
    data = csv.reader(data_file)
    # ... processing
```

**Recommendation**:
```python
# Add explicit cleanup and use context managers
try:
    with open(f'{self.path}/{file}', encoding='UTF8') as data_file:
        data = csv.reader(data_file)
        # ... processing
except IOError as e:
    logging.error(f"File I/O error: {e}")
finally:
    # Cleanup if needed
    pass
```

**Priority**: MEDIUM - Stability

---

### 5. **Logging Issues**

**Issue**: 
- Logging uses `.info()` for errors
- Excessive string concatenation
- No structured logging
- Log rotation not configured in code

```python
logging.info(f'{str(datetime.today()).split(".")[0]} | ERROR MESSAGE {e}')
```

**Recommendation**:
```python
# Use appropriate log levels
logging.error(f"Error in entity transfer: {e}", exc_info=True)
logging.warning(f"Validation failed for record {record_id}")
logging.debug(f"Processing record {record_id}")

# Configure log rotation
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'log/log.txt',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logging.getLogger().addHandler(handler)

# Add structured logging for critical operations
import json
logging.info(json.dumps({
    'event': 'entity_transfer',
    'origin': origin_entity_id,
    'destination': dest_entity_id,
    'record_count': len(records),
    'timestamp': datetime.utcnow().isoformat()
}))
```

**Priority**: MEDIUM - Operations/Debugging

---

### 6. **Thread Safety**

**Issue**: No thread coordination or shared state management
```python
# main.py - multiple threads accessing same API instances
thread_all = threading.Thread(target=main_processes)
thread_thirty_min = threading.Thread(target=thirty_min)
# No locking mechanisms
```

**Recommendation**:
```python
import threading
from queue import Queue

# Add thread-safe logging
log_lock = threading.Lock()

def safe_log(message):
    with log_lock:
        logging.info(message)

# Add rate limiting for API calls
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=10, period=1)  # 10 calls per second
def rate_limited_api_call(api_method, *args, **kwargs):
    return api_method(*args, **kwargs)

# Monitor thread health
def thread_monitor():
    threads = {
        'main': thread_all,
        'thirty_min': thread_thirty_min,
        # ... etc
    }
    while True:
        for name, thread in threads.items():
            if not thread.is_alive():
                logging.critical(f"Thread {name} has died!")
        time.sleep(60)
```

**Priority**: HIGH - Production reliability

---

### 7. **Performance Issues**

**Issue**: Sequential processing of records
```python
for record in records:
    api.create_or_update_one_record(...)  # One at a time
```

**Recommendation**:
```python
# Already using batch updates - good!
# But add batch size control:

def chunked(iterable, size):
    """Split iterable into chunks of size"""
    for i in range(0, len(iterable), size):
        yield iterable[i:i + size]

# Process in batches of 100
for batch in chunked(records, 100):
    body = {"entityId": entity_id, "records": batch}
    api.create_or_update_multi_records(body)
    time.sleep(0.1)  # Rate limiting between batches
```

**Priority**: LOW - Optimization

---

### 8. **Duplicate Code**

**Issue**: Repetitive patterns across multiple files
```python
# Pattern repeated 50+ times in main.py
entity_param_2_entity_param(
    api=chemipal,
    origin_entity_id=X,
    dest_entity_id=Y,
    origin_param_id_to_find=A,
    dest_param_id_to_find=B,
    origin_param_id_to_transfer=C,
    dest_param_id_to_recieve=D
)
```

**Recommendation**:
```python
# Create configuration-driven approach
class TransferRule:
    def __init__(self, origin, dest, find_orig, find_dest, transfer, receive):
        self.origin_entity_id = origin
        self.dest_entity_id = dest
        self.origin_param_id_to_find = find_orig
        self.dest_param_id_to_find = find_dest
        self.origin_param_id_to_transfer = transfer
        self.dest_param_id_to_recieve = receive

# Define rules in config
FITEM_TRANSFER_RULES = [
    TransferRule(1, 8, 250, 609, 3, 707),
    TransferRule(5, 1, 47, 1, 48, 49),
    # ... etc
]

# Execute all rules
for rule in FITEM_TRANSFER_RULES:
    entity_param_2_entity_param(api=chemipal, **vars(rule))
```

**Priority**: MEDIUM - Maintainability

---

### 9. **Input Validation**

**Issue**: Insufficient validation of user input and file data
```python
# PreNames.py - minimal validation
value = row[param].strip()
param_values_for_body.append({'id': param_id, 'value': value})
```

**Recommendation**:
```python
import re
from typing import Optional

def validate_israeli_id(id_str: str) -> Optional[str]:
    """Validate Israeli ID number with checksum"""
    if not id_str.isdigit() or len(id_str) > 9:
        return None
    
    # Pad to 9 digits
    id_str = id_str.zfill(9)
    
    # Luhn algorithm for Israeli ID
    total = 0
    for i, digit in enumerate(id_str[:-1]):
        num = int(digit) * ((i % 2) + 1)
        total += num if num < 10 else num - 9
    
    checksum = (10 - (total % 10)) % 10
    return id_str if int(id_str[-1]) == checksum else None

def validate_date(date_str: str) -> bool:
    """Validate date format YYYYMMDD"""
    if not re.match(r'^\d{8}$', date_str):
        return False
    try:
        datetime.strptime(date_str, '%Y%m%d')
        return True
    except ValueError:
        return False

def sanitize_input(value: str, max_length: int = 255) -> str:
    """Sanitize input string"""
    # Remove control characters
    value = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)
    # Trim to max length
    return value[:max_length].strip()
```

**Priority**: HIGH - Data integrity

---

### 10. **Error Messages - Hebrew Strings**

**Issue**: Hard-coded Hebrew strings make internationalization difficult
```python
"value": "נבדק - תז לא תקין"
```

**Recommendation**:
```python
# Create messages.py
class Messages:
    VALIDATION_MESSAGES = {
        'invalid_id': {
            'he': 'נבדק - תז לא תקין',
            'en': 'Checked - Invalid ID'
        },
        'duplicate_ref': {
            'he': 'לא תקין - מספר תעודת משלוח קיים כבר',
            'en': 'Invalid - Delivery note number already exists'
        }
    }
    
    @staticmethod
    def get(key, lang='he'):
        return Messages.VALIDATION_MESSAGES.get(key, {}).get(lang, key)

# Usage
"value": Messages.get('invalid_id')
```

**Priority**: LOW - Future-proofing

---

## 🟡 Code Quality Improvements

### 1. **Type Hints**

**Current**:
```python
def entity2entity(api, origin_entity_id, dest_entity_id, search_criteria, ...):
```

**Recommended**:
```python
from typing import List, Dict, Any, Optional
from HitoAPI import HitoAPI

def entity2entity(
    api: HitoAPI,
    origin_entity_id: int,
    dest_entity_id: int,
    search_criteria: List[Dict[str, Any]],
    param_ids_to_transfer: List[int],
    param_ids_to_receive: List[int],
    program_status_param_id: int
) -> bool:
    """
    Transfer records from one entity to another.
    
    Args:
        api: Authenticated HitoAPI instance
        origin_entity_id: Source entity ID
        dest_entity_id: Destination entity ID
        search_criteria: List of search criteria dicts
        param_ids_to_transfer: Parameter IDs to copy from source
        param_ids_to_receive: Parameter IDs to write to destination
        program_status_param_id: Status parameter to update
        
    Returns:
        True if successful, False otherwise
    """
```

---

### 2. **Code Documentation**

**Add module-level docstrings**:
```python
"""
OrdFunctions.py - Order Processing and Validation

This module handles the complete lifecycle of order processing:
1. New order detection (Entity 34 - ORDFILE)
2. Reference number assignment via Entity 44
3. Multi-stage validation
4. Transfer to production Entity 10

Author: [Team Name]
Last Modified: 2024-10-21
Dependencies: HitoAPI, helpers
"""
```

---

### 3. **Constants vs Magic Numbers**

**Current**:
```python
if record["paramValues"][5].get("valueId") == 4:
```

**Recommended**:
```python
# constants.py
class SupplierStatus:
    ACTIVE = 1
    INACTIVE = 4
    OUT_OF_STOCK = 2

# Usage
if record["paramValues"][5].get("valueId") == SupplierStatus.INACTIVE:
```

---

### 4. **Exception Handling Specificity**

**Current**:
```python
except Exception as e:
```

**Recommended**:
```python
except requests.RequestException as e:
    logging.error(f"Network error: {e}")
except ValueError as e:
    logging.error(f"Data validation error: {e}")
except KeyError as e:
    logging.error(f"Missing expected field: {e}")
except Exception as e:
    logging.critical(f"Unexpected error: {e}", exc_info=True)
    # Re-raise or handle appropriately
```

---

### 5. **Testing Support**

**Add test infrastructure**:
```python
# tests/test_helpers.py
import unittest
from unittest.mock import Mock, patch
from helpers import entity2entity

class TestEntity2Entity(unittest.TestCase):
    def setUp(self):
        self.mock_api = Mock()
        
    def test_successful_transfer(self):
        # Arrange
        self.mock_api.get_records_by_search_criteria_and_params.return_value = {
            "records": [{"recordId": 1, "paramValues": [{"id": 1, "value": "test"}]}]
        }
        
        # Act
        result = entity2entity(
            api=self.mock_api,
            origin_entity_id=1,
            dest_entity_id=2,
            search_criteria=[],
            param_ids_to_transfer=[1],
            param_ids_to_receive=[2],
            program_status_param_id=100
        )
        
        # Assert
        self.assertTrue(result)
        self.mock_api.create_or_update_multi_records.assert_called()
```

---

## 🟢 Architecture Recommendations

### 1. **Separation of Concerns**

**Create layered architecture**:
```
├── api/
│   ├── hito_client.py      # API wrapper
│   └── pulseem_client.py   # SMS API wrapper
├── models/
│   ├── entity.py           # Entity models
│   └── transfer_rule.py    # Transfer configuration
├── services/
│   ├── file_service.py     # File I/O operations
│   ├── validation_service.py  # Validation logic
│   └── transfer_service.py # Entity transfer logic
├── workers/
│   ├── base_worker.py      # Base thread worker
│   └── file_worker.py      # File processing worker
├── config/
│   ├── settings.py         # Application settings
│   └── entity_config.py    # Entity mappings
└── utils/
    ├── logger.py           # Logging configuration
    └── decorators.py       # Retry, rate limit decorators
```

---

### 2. **Dependency Injection**

**Current**: Direct instantiation
```python
chemipal = HitoAPI(os.environ.get("CHEMIPAL_DOMAIN"), os.environ.get("CHEMIPAL_API_KEY"))
```

**Recommended**:
```python
# config/settings.py
from dataclasses import dataclass
from typing import Dict

@dataclass
class APIConfig:
    domain: str
    api_key: str

class AppConfig:
    def __init__(self):
        self.apis: Dict[str, APIConfig] = {
            'chemipal': APIConfig(
                domain=os.getenv('CHEMIPAL_DOMAIN'),
                api_key=os.getenv('CHEMIPAL_API_KEY')
            ),
            # ... other APIs
        }

# main.py
config = AppConfig()
api_factory = APIFactory(config)
chemipal = api_factory.create('chemipal')
```

---

### 3. **Configuration Management**

**Use configuration files instead of environment variables for complex settings**:
```yaml
# config/production.yaml
apis:
  chemipal:
    domain: https://chemipal.hito.com
    timeout: 30
    retry_attempts: 3
    
workers:
  main_process:
    interval: 420  # 7 minutes
    enabled: true
  volunteer_process:
    interval: 3600
    enabled: true
    
file_processing:
  source_folder: C:\FTP_Clients\chemipal\In
  batch_size: 100
  max_file_size_mb: 50
```

---

### 4. **Health Monitoring**

**Add health check endpoint**:
```python
# monitoring/health.py
from datetime import datetime
from typing import Dict

class HealthMonitor:
    def __init__(self):
        self.thread_health = {}
        self.last_api_success = {}
        
    def check_thread(self, thread_name: str) -> bool:
        """Check if thread is alive and processing"""
        return self.thread_health.get(thread_name, {}).get('alive', False)
    
    def update_api_status(self, api_name: str, success: bool):
        """Record API call result"""
        self.last_api_success[api_name] = {
            'success': success,
            'timestamp': datetime.utcnow()
        }
    
    def get_health_status(self) -> Dict:
        """Get overall system health"""
        return {
            'threads': self.thread_health,
            'apis': self.last_api_success,
            'timestamp': datetime.utcnow().isoformat()
        }
```

---

### 5. **Database for State Management**

**Consider adding SQLite for tracking**:
```python
# models/processing_state.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class ProcessingLog(Base):
    __tablename__ = 'processing_log'
    
    id = Column(Integer, primary_key=True)
    file_name = Column(String)
    entity_id = Column(Integer)
    status = Column(String)
    records_processed = Column(Integer)
    errors = Column(String)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
# Track file processing history
# Prevent duplicate processing
# Enable audit trail
```

---

# Installation & Setup

## Prerequisites

### System Requirements
- **Operating System**: Windows 10/11 or Windows Server 2016+
- **Python**: 3.8 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Disk Space**: 10GB free space for logs and temporary files
- **Network**: Stable internet connection with access to Hito API endpoints

### Software Dependencies
1. Python 3.8+
2. pip (Python package manager)
3. Virtual environment support
4. Access to FTP/network folders

---

## Step 1: Environment Setup

### 1.1 Clone/Download Project
```bash
# If using Git
git clone <repository-url>
cd "chemipal new app"

# Or extract from ZIP
# Navigate to project folder
```

### 1.2 Create Virtual Environment
```bash
# Create virtual environment
python -m venv ..\chemipal-env

# Activate virtual environment (Windows)
..\chemipal-env\Scripts\activate.bat

# Verify Python version
python --version
# Should show Python 3.8 or higher
```

### 1.3 Install Dependencies
```bash
# Install required packages
pip install requests python-dotenv

# Optional but recommended
pip install requests[security]  # For improved SSL support

# For development
pip install pytest pytest-mock black flake8

# Verify installations
pip list
```

---

## Step 2: Configuration

### 2.1 Create Environment File

Create `.env` file in project root:

```bash
# API Endpoints - ChemiPal
CHEMIPAL_DOMAIN=https://your-domain.hito.com
CHEMIPAL_API_KEY=your_api_key_here

# Customer APIs
RLZ_DOMAIN=https://rlz-domain.hito.com
RLZ_API_KEY=rlz_api_key_here

DELEK_DOMAIN=https://delek-domain.hito.com
DELEK_API_KEY=delek_api_key_here

NETANYA_DOMAIN=https://netanya-domain.hito.com
NETANYA_API_KEY=netanya_api_key_here

HOLON_DOMAIN=https://holon-domain.hito.com
HOLON_API_KEY=holon_api_key_here

NAMAL_DOMAIN=https://namal-domain.hito.com
NAMAL_API_KEY=namal_api_key_here

ASHDOD_DOMAIN=https://ashdod-domain.hito.com
ASHDOD_API_KEY=ashdod_api_key_here

G1_DOMAIN=https://g1-domain.hito.com
G1_API_KEY=g1_api_key_here

# File Paths (Adjust for your system)
SOURCE_FOLDER=C:\FTP_Clients\chemipal\In
DESTINATION_FOLDER=C:\FTP_Clients\chemipal\In\backlog
CHEMIPAL_EXPORT_PATH=C:\FTP_Clients\chemipal\Out
CHEMIPAL_EXPORT_BACKUP=C:\FTP_Clients\chemipal\Out\backup

# Optional: SMS API
PULSEEM_API_KEY=your_pulseem_key_here
```

**⚠️ Security Note**: 
- Never commit `.env` file to version control
- Add `.env` to `.gitignore`
- Use proper access controls on the file

### 2.2 Create Required Directories

```bash
# Create directory structure
mkdir log
mkdir "C:\FTP_Clients\chemipal\In"
mkdir "C:\FTP_Clients\chemipal\In\backlog"
mkdir "C:\FTP_Clients\chemipal\In\duplicates"
mkdir "C:\FTP_Clients\chemipal\Out"
mkdir "C:\FTP_Clients\chemipal\Out\backup"
```

### 2.3 Set Directory Permissions

```bash
# Windows - Set permissions for service account
icacls "C:\FTP_Clients\chemipal" /grant "YourServiceAccount:(OI)(CI)F"
```

---

## Step 3: Verify API Connectivity

Create test script `test_connection.py`:

```python
import os
from dotenv import load_dotenv
from HitoAPI import HitoAPI

load_dotenv()

def test_api_connection():
    """Test connection to ChemiPal API"""
    print("Testing API connection...")
    
    try:
        api = HitoAPI(
            os.environ.get("CHEMIPAL_DOMAIN"),
            os.environ.get("CHEMIPAL_API_KEY")
        )
        
        # Test getting users
        users = api.get_users()
        print(f"✓ Successfully connected to API")
        print(f"✓ Retrieved {len(users)} users")
        
        # Test getting entity
        entity = api.get_entity_records(1)
        print(f"✓ Successfully accessed Entity 1")
        
        return True
        
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_api_connection()
```

Run test:
```bash
python test_connection.py
```

---

## Step 4: Initial Configuration Validation

### 4.1 Verify Entity Access

Create `verify_entities.py`:

```python
from dotenv import load_dotenv
import os
from HitoAPI import HitoAPI

load_dotenv()

api = HitoAPI(os.environ.get("CHEMIPAL_DOMAIN"), os.environ.get("CHEMIPAL_API_KEY"))

# Critical entities to verify
CRITICAL_ENTITIES = {
    1: "FITEM",
    4: "SPK (Suppliers)",
    5: "ITM (Items)",
    7: "CTR (Contracts)",
    8: "INV (Inventory)",
    10: "ORD (Orders)",
    19: "DOC (Documents)",
    28: "FITEMCHECK",
    33: "INVFILE",
    34: "ORDFILE"
}

print("Verifying entity access...\n")

for entity_id, entity_name in CRITICAL_ENTITIES.items():
    try:
        params = api.get_entity_params(entity_id)
        print(f"✓ Entity {entity_id} ({entity_name}): {len(params)} parameters")
    except Exception as e:
        print(f"✗ Entity {entity_id} ({entity_name}): FAILED - {e}")
```

Run:
```bash
python verify_entities.py
```

---

# Running the Application

## Manual Start (Development/Testing)

### Option 1: Direct Python Execution

```bash
# Activate virtual environment
..\chemipal-env\Scripts\activate.bat

# Run application
python main.py

# Monitor logs in real-time (separate terminal)
tail -f log\log.txt  # Linux/Git Bash
Get-Content log\log.txt -Wait  # PowerShell
```

### Option 2: Using Batch File

```bash
# Run using provided batch file
main.bat

# The batch file automatically:
# 1. Activates virtual environment
# 2. Starts Python application
# 3. Logs output
```

---

## Production Deployment - Windows Service

### Step 1: Install NSSM (Non-Sucking Service Manager)

```bash
# Download NSSM from https://nssm.cc/download
# Extract to C:\nssm\

# Add to PATH or use full path
```

### Step 2: Create Service

```bash
# Run as Administrator
cd "C:\Work\Satelites\chemipal new app"

# Install service
C:\nssm\nssm.exe install ChemiPalIntegration "C:\Work\Satelites\chemipal-env\Scripts\python.exe" "C:\Work\Satelites\chemipal new app\main.py"

# Configure service
C:\nssm\nssm.exe set ChemiPalIntegration AppDirectory "C:\Work\Satelites\chemipal new app"
C:\nssm\nssm.exe set ChemiPalIntegration AppStdout "C:\Work\Satelites\chemipal new app\log\stdout.txt"
C:\nssm\nssm.exe set ChemiPalIntegration AppStderr "C:\Work\Satelites\chemipal new app\log\stderr.txt"

# Set service to auto-start
C:\nssm\nssm.exe set ChemiPalIntegration Start SERVICE_AUTO_START

# Start service
C:\nssm\nssm.exe start ChemiPalIntegration
```

### Step 3: Verify Service

```bash
# Check service status
C:\nssm\nssm.exe status ChemiPalIntegration

# View service in Services Manager
services.msc
# Look for "ChemiPalIntegration"
```

---

## Alternative: Task Scheduler

### Create Scheduled Task

```bash
# Create task that runs at startup
# Run as Administrator

# Create Basic Task
# Name: ChemiPal Integration
# Trigger: When computer starts
# Action: Start a program
# Program: C:\Work\Satelites\chemipal-env\Scripts\python.exe
# Arguments: "C:\Work\Satelites\chemipal new app\main.py"
# Start in: C:\Work\Satelites\chemipal new app
```

Via Command Line:
```powershell
schtasks /create /tn "ChemiPalIntegration" /tr "C:\Work\Satelites\chemipal new app\main.bat" /sc onstart /ru "SYSTEM" /rl HIGHEST
```

---

# Monitoring & Maintenance

## Log Monitoring

### Real-Time Monitoring

**PowerShell**:
```powershell
# Monitor main log
Get-Content "log\log.txt" -Wait -Tail 50

# Filter for errors
Get-Content "log\log.txt" -Wait | Select-String -Pattern "ERROR|EXCEPTION"

# Monitor specific process
Get-Content "log\log.txt" -Wait | Select-String -Pattern "volunteer_processes"
```

**Linux/Git Bash**:
```bash
# Monitor all logs
tail -f log/log.txt

# Filter errors
tail -f log/log.txt | grep "ERROR\|EXCEPTION"

# Multiple logs
tail -f log/*.txt
```

### Log Analysis

```powershell
# Count errors in last 24 hours
Get-Content "log\log.txt" | Select-String -Pattern "ERROR" | Measure-Object

# Find specific entity processing
Get-Content "log\log.txt" | Select-String -Pattern "entity_id=8"

# Check thread activity
Get-Content "log\log.txt" | Select-String -Pattern "START Initialize"
```

---

## Performance Monitoring

### Create Monitoring Script

`monitor.py`:
```python
import psutil
import os
import time
from datetime import datetime

def monitor_process():
    """Monitor ChemiPal process"""
    
    # Find Python process running main.py
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'python' in proc.info['name'].lower():
                cmdline = ' '.join(proc.info['cmdline'])
                if 'main.py' in cmdline:
                    pid = proc.info['pid']
                    process = psutil.Process(pid)
                    
                    print(f"Process ID: {pid}")
                    print(f"CPU Usage: {process.cpu_percent(interval=1)}%")
                    print(f"Memory Usage: {process.memory_info().rss / 1024 / 1024:.2f} MB")
                    print(f"Threads: {process.num_threads()}")
                    print(f"Running since: {datetime.fromtimestamp(process.create_time())}")
                    
                    # Check thread count (should be 9 worker threads + main)
                    if process.num_threads() < 9:
                        print("⚠️  WARNING: Some threads may have died!")
                    
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    print("Process not found!")
    return False

if __name__ == "__main__":
    while True:
        print(f"\n=== {datetime.now()} ===")
        monitor_process()
        time.sleep(60)
```

---

## Log Rotation

### Manual Rotation

```bash
# Create rotation script: rotate_logs.bat
@echo off
cd "C:\Work\Satelites\chemipal new app\log"

# Archive current log
set timestamp=%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%
copy log.txt log_%timestamp%.txt

# Clear current log (or truncate)
echo. > log.txt

# Delete logs older than 30 days
forfiles /p "." /m log_*.txt /d -30 /c "cmd /c del @path"
```

Add to Task Scheduler (daily at midnight):
```powershell
schtasks /create /tn "ChemiPal Log Rotation" /tr "C:\Work\Satelites\chemipal new app\log\rotate_logs.bat" /sc daily /st 00:00
```

---

## Health Checks

### Create Health Check Script

`healthcheck.py`:
```python
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

def check_log_activity():
    """Check if logs are being written (process is alive)"""
    log_file = Path("log/log.txt")
    
    if not log_file.exists():
        return False, "Log file not found"
    
    # Check last modification time
    last_modified = datetime.fromtimestamp(log_file.stat().st_mtime)
    age = datetime.now() - last_modified
    
    if age > timedelta(minutes=10):
        return False, f"No log activity for {age.total_seconds()/60:.1f} minutes"
    
    return True, f"Last activity: {age.total_seconds():.0f} seconds ago"

def check_file_folders():
    """Check if required folders are accessible"""
    folders = [
        os.getenv("SOURCE_FOLDER"),
        os.getenv("DESTINATION_FOLDER"),
        os.getenv("CHEMIPAL_EXPORT_PATH")
    ]
    
    for folder in folders:
        if not folder or not Path(folder).exists():
            return False, f"Folder not accessible: {folder}"
    
    return True, "All folders accessible"

def check_pending_files():
    """Check for stuck files"""
    source = Path(os.getenv("SOURCE_FOLDER", ""))
    if not source.exists():
        return True, "Source folder not configured"
    
    old_files = []
    cutoff = datetime.now() - timedelta(hours=2)
    
    for file in source.glob("*.csv"):
        if datetime.fromtimestamp(file.stat().st_mtime) < cutoff:
            old_files.append(file.name)
    
    if old_files:
        return False, f"Files stuck for >2 hours: {', '.join(old_files)}"
    
    return True, "No stuck files"

def main():
    checks = [
        ("Log Activity", check_log_activity),
        ("File Folders", check_file_folders),
        ("Pending Files", check_pending_files)
    ]
    
    print(f"=== Health Check: {datetime.now()} ===\n")
    
    all_ok = True
    for name, check_func in checks:
        status, message = check_func()
        symbol = "✓" if status else "✗"
        print(f"{symbol} {name}: {message}")
        all_ok = all_ok and status
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
```

Schedule health check:
```powershell
schtasks /create /tn "ChemiPal Health Check" /tr "python C:\Work\Satelites\chemipal new app\healthcheck.py" /sc minute /mo 5
```

---

## Backup Procedures

### Database/State Backup

```bash
# Backup .env file
copy .env .env.backup.%date:~-4,4%%date:~-7,2%%date:~-10,2%

# Backup configuration
xcopy /E /I /Y *.py backup\%date:~-4,4%%date:~-7,2%%date:~-10,2%

# Backup logs (weekly)
xcopy /E /I /Y log backup\logs\%date:~-4,4%%date:~-7,2%%date:~-10,2%
```

---

# Troubleshooting Guide

## Common Issues

### 1. Application Won't Start

**Symptoms**: 
- main.py exits immediately
- No log file created
- Service won't start

**Diagnosis**:
```bash
# Run in console to see errors
python main.py

# Check Python version
python --version

# Check dependencies
pip list | findstr requests
pip list | findstr dotenv
```

**Solutions**:
1. Verify virtual environment is activated
2. Install missing dependencies: `pip install -r requirements.txt`
3. Check `.env` file exists and has correct values
4. Verify Python path in service configuration

---

### 2. API Connection Failures

**Symptoms**:
- Logs show "END WITH ERRORS COULD NOT GET RECORDS"
- Timeout errors
- SSL certificate errors

**Diagnosis**:
```python
# Test API connection
python test_connection.py

# Check network connectivity
ping your-domain.hito.com

# Test SSL
curl -v https://your-domain.hito.com
```

**Solutions**:
1. Verify API domain and key in `.env`
2. Check firewall rules
3. If SSL error: Review SSL verification setting
4. Check API rate limits
5. Verify API credentials haven't expired

---

### 3. File Processing Stuck

**Symptoms**:
- Files remain in source folder
- No files being imported
- Duplicate file errors

**Diagnosis**:
```bash
# Check file permissions
icacls "C:\FTP_Clients\chemipal\In"

# List files
dir "C:\FTP_Clients\chemipal\In\*.csv"

# Check log for file-related errors
findstr /i "prenames" log\log.txt
```

**Solutions**:
1. Verify folder permissions
2. Check file encoding (must be UTF-8)
3. Verify CSV format
4. Check for duplicate files in backlog
5. Clear duplicate folder if needed
6. Manually move stuck files

---

### 4. Validation Failures

**Symptoms**:
- Records showing "נסגר ולא עבר ולידציה"
- Orders not transferring
- Inventory not being created

**Diagnosis**:
```bash
# Check validation logs
findstr /i "validate" log\log.txt

# Look for specific error messages
findstr /i "לא תקין" log\log.txt
```

**Solutions**:
Based on error message:
- "לא תקין - קוד ספק לא תואם" → Check supplier exists in Entity 4
- "לא תקין - לא קיים מק\"ט כמיפל" → Check item exists in Entity 1
- "לא תקין - אין חוזה בתוקף" → Verify contract in Entity 7
- "לא תקין - מספר תעודת משלוח קיים כבר" → Duplicate reference number

---

### 5. Thread Deaths

**Symptoms**:
- Some processes stop running
- Fewer than 9 threads active
- Specific customer data not updating

**Diagnosis**:
```python
# Check thread count
python monitor.py

# Review logs for specific thread
findstr /i "volunteer_processes" log\log.txt
findstr /i "main_processes" log\log.txt
```

**Solutions**:
1. Check for unhandled exceptions in logs
2. Restart application
3. Review specific thread code for errors
4. Check API connectivity for specific customer

---

### 6. High Memory Usage

**Symptoms**:
- Application using >1GB RAM
- Slowdown over time
- Out of memory errors

**Diagnosis**:
```python
# Monitor memory
python monitor.py

# Check for memory leaks in logs
findstr /i "memory\|resource" log\log.txt
```

**Solutions**:
1. Restart application daily via scheduled task
2. Reduce batch sizes in code
3. Clear log files regularly
4. Check for circular references
5. Review file handle cleanup

---

### 7. Duplicate Records

**Symptoms**:
- Same data imported multiple times
- "Duplicate" errors
- Files reprocessed

**Diagnosis**:
```bash
# Check duplicate folder
dir "C:\FTP_Clients\chemipal\In\duplicates"

# Check backlog
dir "C:\FTP_Clients\chemipal\In\backlog"

# Search for duplicate-related logs
findstr /i "duplicate" log\log.txt
```

**Solutions**:
1. Check file moved to backlog after processing
2. Verify duplicate detection working
3. Clear and reorganize folders if needed
4. Check file timestamps

---

# Development Workflow

## Making Code Changes

### Step 1: Create Development Branch

```bash
git checkout -b feature/your-feature-name
```

### Step 2: Set Up Development Environment

```bash
# Use separate virtual environment
python -m venv dev-env
dev-env\Scripts\activate

# Install dev dependencies
pip install pytest pytest-mock black flake8 mypy

# Install application dependencies
pip install -r requirements.txt
```

### Step 3: Make Changes

1. **Modify code** with your editor
2. **Follow coding standards**:
   ```bash
   # Format code
   black your_file.py
   
   # Check style
   flake8 your_file.py
   
   # Type checking
   mypy your_file.py
   ```

### Step 4: Test Changes

```bash
# Run unit tests
pytest tests/

# Test specific module
pytest tests/test_helpers.py

# Run with coverage
pytest --cov=. tests/
```

### Step 5: Test Integration

```bash
# Test with development configuration
cp .env .env.dev
# Modify .env.dev with test API keys

# Run specific process
python -c "from main import thirty_min; thirty_min()"
```

### Step 6: Commit Changes

```bash
git add .
git commit -m "feat: add new validation for inventory"
git push origin feature/your-feature-name
```

---

## Adding New File Type

### Step-by-Step Guide

**Example: Adding "NEWFILE" CSV import**

1. **Define file format** (document first!)
   - Column mapping
   - Required fields
   - Validation rules

2. **Update PreNames usage**:
```python
# In appropriate thread function (e.g., thirty_min)
def thirty_min():
    while True:
        # ... existing code ...
        
        # Add new file import
        new_file_import = PreNames(
            "NEWFILE",                    # File prefix
            99,                            # Destination entity ID
            chemipal,                      # API instance
            os.environ.get("SOURCE_FOLDER"),
            os.environ.get("DESTINATION_FOLDER")
        )
        result = new_file_import.creating_body_to_update()
        
        if result:
            # Add data enrichment if needed
            entity_param_2_entity_param(
                api=chemipal,
                origin_entity_id=99,
                dest_entity_id=1,
                origin_param_id_to_find=100,
                dest_param_id_to_find=200,
                origin_param_id_to_transfer=101,
                dest_param_id_to_recieve=201
            )
        
        time.sleep(1800)  # 30 minutes
```

3. **Test file import**:
```python
# Create test file: NEWFILE_test.csv
# Place in source folder
# Monitor logs
```

4. **Document** in agent.md and this file

---

## Adding New Customer Integration

1. **Get API credentials** from customer
2. **Add to .env**:
```bash
NEWCUSTOMER_DOMAIN=https://...
NEWCUSTOMER_API_KEY=...
```

3. **Create API instance** in main.py:
```python
newcustomer = HitoAPI(
    os.environ.get("NEWCUSTOMER_DOMAIN"),
    os.environ.get("NEWCUSTOMER_API_KEY")
)
```

4. **Create processing function**:
```python
def newcustomer_processes():
    while True:
        logging.info(f'START newcustomer_processes()')
        
        transfer_records(
            customer_name="NewCustomer",
            api=newcustomer,
            origin_entity_id=10,
            dest_entity_id=20,
            search_criteria=[{"paramId": 100, "operator": "EQ", "values": [1]}],
            param_ids_to_transfer=[1, 2, 3],
            param_ids_to_receive=[10, 20, 30],
            program_status_param_id=100,
            new_id_pos=0
        )
        
        logging.info(f'END newcustomer_processes()')
        time.sleep(600)  # 10 minutes
```

5. **Create and start thread**:
```python
thread_newcustomer = threading.Thread(target=newcustomer_processes)
thread_newcustomer.start()
# ... at end of main.py
thread_newcustomer.join()
```

6. **Test thoroughly** before production

---

# Testing Procedures

## Unit Testing

### Example Test File

`tests/test_entity_transfer.py`:
```python
import unittest
from unittest.mock import Mock, patch
from helpers import entity2entity

class TestEntity2Entity(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_api = Mock()
        self.search_criteria = [
            {"paramId": 702, "operator": "EQ", "values": ["5"]}
        ]
        
    def test_successful_transfer(self):
        """Test successful record transfer"""
        # Mock API responses
        self.mock_api.get_records_by_search_criteria_and_params.return_value = {
            "records": [
                {
                    "recordId": 123,
                    "paramValues": [
                        {"id": 1, "value": "test", "valueId": 1}
                    ]
                }
            ]
        }
        
        # Execute
        result = entity2entity(
            api=self.mock_api,
            origin_entity_id=28,
            dest_entity_id=1,
            search_criteria=self.search_criteria,
            param_ids_to_transfer=[1],
            param_ids_to_receive=[2],
            program_status_param_id=702
        )
        
        # Assert
        self.assertTrue(result)
        self.assertEqual(self.mock_api.create_or_update_multi_records.call_count, 2)
        
    def test_no_records_found(self):
        """Test when no records match criteria"""
        self.mock_api.get_records_by_search_criteria_and_params.return_value = {}
        
        result = entity2entity(
            api=self.mock_api,
            origin_entity_id=28,
            dest_entity_id=1,
            search_criteria=self.search_criteria,
            param_ids_to_transfer=[1],
            param_ids_to_receive=[2],
            program_status_param_id=702
        )
        
        self.assertFalse(result)
        
    def test_api_error_handling(self):
        """Test API error handling"""
        self.mock_api.get_records_by_search_criteria_and_params.side_effect = Exception("API Error")
        
        result = entity2entity(
            api=self.mock_api,
            origin_entity_id=28,
            dest_entity_id=1,
            search_criteria=self.search_criteria,
            param_ids_to_transfer=[1],
            param_ids_to_receive=[2],
            program_status_param_id=702
        )
        
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
```

Run tests:
```bash
python -m pytest tests/ -v
```

---

## Integration Testing

### Test Complete File Processing

`tests/test_file_integration.py`:
```python
import os
import tempfile
import shutil
from PreNames import PreNames
from unittest.mock import Mock

def test_file_import_integration():
    """Test complete file import process"""
    
    # Create temporary directories
    source = tempfile.mkdtemp()
    dest = tempfile.mkdtemp()
    
    try:
        # Create test CSV file
        test_file = os.path.join(source, "SPK_test.csv")
        with open(test_file, 'w', encoding='UTF-8') as f:
            f.write("ID,Name,Code\n")
            f.write("1,Test Supplier,ABC123\n")
        
        # Mock API
        mock_api = Mock()
        mock_api.get_entity_params.return_value = [
            {"id": 1, "type": "NUMBER"},
            {"id": 2, "type": "TEXT"},
            {"id": 3, "type": "TEXT"}
        ]
        mock_api.get_specific_param_id.side_effect = [(1, "NUMBER"), (2, "TEXT"), (3, "TEXT")]
        
        # Test import
        importer = PreNames("SPK", 4, mock_api, source, dest)
        result = importer.creating_body_to_update()
        
        # Verify
        assert result == True
        assert mock_api.create_or_update_multi_records.called
        assert os.path.exists(os.path.join(dest, "SPK_test.csv"))
        
    finally:
        # Cleanup
        shutil.rmtree(source)
        shutil.rmtree(dest)
```

---

## Manual Testing Checklist

Before deploying changes:

- [ ] API connectivity test passed
- [ ] Entity access verified
- [ ] Test file import successful
- [ ] Validation rules working
- [ ] Error handling tested
- [ ] Logs are readable and informative
- [ ] No memory leaks detected
- [ ] Performance acceptable
- [ ] All threads starting correctly
- [ ] Service installation works
- [ ] Health check passes

---

# Deployment Guide

## Pre-Deployment Checklist

### Code Quality
- [ ] All tests passing
- [ ] Code reviewed
- [ ] Documentation updated
- [ ] No debug code or print statements
- [ ] Logging appropriate level

### Configuration
- [ ] Production `.env` configured
- [ ] API keys validated
- [ ] Folder paths correct
- [ ] Permissions verified
- [ ] Backup configured

### Testing
- [ ] Tested in staging environment
- [ ] Integration tests passed
- [ ] Performance tested
- [ ] Error scenarios tested

---

## Deployment Steps

### 1. Backup Current Version

```bash
# Stop service
net stop ChemiPalIntegration

# Backup current version
xcopy /E /I "C:\Work\Satelites\chemipal new app" "C:\Backups\chemipal_backup_%date:~-4,4%%date:~-7,2%%date:~-10,2%"

# Backup .env
copy .env .env.backup
```

### 2. Deploy New Code

```bash
# Pull latest code
git pull origin main

# Or copy files
xcopy /E /I /Y "\\deployment\source\*" "C:\Work\Satelites\chemipal new app"

# Restore .env if needed
copy .env.backup .env
```

### 3. Update Dependencies

```bash
# Activate virtual environment
..\chemipal-env\Scripts\activate

# Update packages
pip install --upgrade -r requirements.txt
```

### 4. Run Validation

```bash
# Test API connection
python test_connection.py

# Run health check
python healthcheck.py

# Verify entities
python verify_entities.py
```

### 5. Start Service

```bash
# Start service
net start ChemiPalIntegration

# Verify running
sc query ChemiPalIntegration

# Monitor logs
Get-Content log\log.txt -Wait -Tail 50
```

### 6. Post-Deployment Verification

```bash
# Wait 5 minutes, then check:

# 1. All threads active
python monitor.py

# 2. No errors in logs
findstr /i "ERROR\|EXCEPTION" log\log.txt

# 3. Files being processed
dir "C:\FTP_Clients\chemipal\In"

# 4. Data flowing to API
# Check recent records in Hito admin panel
```

---

## Rollback Procedure

If issues occur:

```bash
# 1. Stop service
net stop ChemiPalIntegration

# 2. Restore backup
xcopy /E /I /Y "C:\Backups\chemipal_backup_YYYYMMDD\*" "C:\Work\Satelites\chemipal new app"

# 3. Restore .env
copy .env.backup .env

# 4. Start service
net start ChemiPalIntegration

# 5. Verify
python healthcheck.py
```

---

## Monitoring Post-Deployment

Monitor for 24 hours:
- Check logs every 2 hours
- Run health check every hour
- Monitor memory usage
- Verify data accuracy in Hito
- Check with end users

---

## Emergency Contacts

**Priority 1 Issues** (System down):
- Contact: [IT Manager]
- Phone: [Phone Number]
- Email: [Email]

**Priority 2 Issues** (Degraded performance):
- Contact: [Developer]
- Email: [Email]

**API Issues**:
- Hito Support: [Support Contact]

---

## Summary of Improvement Priorities

### Immediate (Do Now)
1. Enable SSL verification
2. Add retry logic for API calls
3. Fix logging levels (use `.error()` for errors)
4. Add basic health monitoring

### Short Term (Next Sprint)
1. Create configuration file for entity/param IDs
2. Add input validation
3. Implement log rotation
4. Add unit tests for critical functions
5. Create constants for magic numbers

### Medium Term (Next Quarter)
1. Refactor to use dependency injection
2. Add comprehensive error handling
3. Implement monitoring dashboard
4. Add database for state tracking
5. Create layered architecture

### Long Term (Future)
1. Microservices architecture
2. API rate limiting
3. Internationalization
4. Performance optimization
5. Automated testing pipeline

---

**Document Version**: 1.0  
**Last Updated**: 2024-10-21  
**Maintained By**: Development Team







