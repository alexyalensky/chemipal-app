# ChemiPal Integration System - Agent Instructions

## Project Overview

This is a **multi-threaded data synchronization and processing system** built in Python that integrates multiple HitoAPI instances with file-based data import/export capabilities. The system manages inventory (INV), orders (ORD), items (FITEM), suppliers (SPK), documents (DOC), and volunteer records across multiple customer domains.

### Primary Purpose
- **Data Synchronization**: Transfer and synchronize data between different HitoAPI entities
- **File Processing**: Import CSV files from FTP locations and validate them
- **Validation**: Comprehensive data validation before processing
- **Export**: Generate CSV files for external systems
- **Multi-Tenant**: Support multiple customer instances (Chemipal, RLZ, Delek, Netanya, Holon, Namal, Ashdod, G1)

---

## Architecture and Structure

### Core Components

```
├── main.py                    # Application entry point with 9 threaded processes
├── HitoAPI.py                # Main API wrapper class for Hito REST API
├── helpers.py                # Utility functions for data transfer and transformation
├── g1_functions.py           # G1-specific user creation from entity rows
├── PreNames.py               # CSV file import handler (SPK, ITM, CTR, DOC, RINV, INV, FITEM)
├── OrdFunctions.py           # Order (ORD) processing and validation
├── InvFunctions.py           # Inventory (INV) processing and validation
├── FitemFunctions.py         # Item (FITEM) processing and validation
├── INVORD.py                 # Export handler for INV and ORD entities
├── OrderNumbering.py         # Sequential numbering for orders
├── PulseemAPI.py             # SMS API integration
└── check_volunteer_exists.py # Volunteer validation
```

---

## API Classes

### 1. **HitoAPI** (`HitoAPI.py`)
Main wrapper for Hito REST API interactions.

**Key Methods:**
- `get_users()` - Retrieve all users
- `get_entity_records(entity_num)` - Get all records from an entity
- `get_records_by_search_criteria_and_params(entity_id, params, searchCriterias)` - Query with filters
- `create_or_update_multi_records(body)` - Bulk create/update records
- `add_update_users(users)` - Create or update users
- `get_entity_params(entity_num)` - Get entity parameter definitions

**Constructor:**
```python
HitoAPI(domain, api_key)
```

**Connection Instances in main.py:**
- `chemipal` - Main ChemiPal instance
- `rlz`, `delek`, `netanya`, `holon`, `namal`, `ashdod` - Customer instances
- `g1` - G1 system instance

---

### 2. **PulseemAPI** (`PulseemAPI.py`)
SMS notification service integration.

**Key Methods:**
- `send_sms(send_id, from_number, to_number, message)` - Send SMS notifications

---

## Main Components

### **main.py - Threading Model**

The application runs **9 concurrent threads**, each handling different processes:

| Thread | Function | Interval | Description |
|--------|----------|----------|-------------|
| 1 | `main_processes()` | 7 minutes | Core file import (INV, FITEM) + validation + data transfer |
| 2 | `thirty_min()` | 30 minutes | Import SPK, ITM, CTR files |
| 3 | `one_hour()` | 1 hour | Export INV files |
| 4 | `fifteen_min()` | 15 minutes | Import DOC, RINV + export ORD files |
| 5 | `volunteer_processes()` | 1 hour | Transfer volunteers (RLZ, Netanya, Holon) |
| 6 | `delek_processes()` | 2 hours | Convert Delek entities to users |
| 7 | `namal_proccesses()` | 1 minute | Transfer Namal records |
| 8 | `ashdod_betihut()` | 10 minutes | Transfer Ashdod safety records |
| 9 | `g1_processes()` | 1 minute | Create users from G1 entity rows |

---

## Data Flow

### **Main Process Flow (main_processes)**

```
1. Import INV files (PreNames) → Validate → Transfer to Entity 8
2. Import FITEM files (PreNames) → Validate → Transfer to Entity 1
3. Check new FITEM rows (Entity 28) → Validate → Transfer to Entity 1
4. Check new INV rows (Entity 33) → Validate → Order numbering → Transfer to Entity 8
5. Check new ORD rows (Entity 34) → Validate → Order numbering → Transfer to Entity 10
6. Data enrichment via entity_param_2_entity_param transfers
```

### **Key Entity Transfers**

The system uses several helper functions to transfer data between entities:

**`entity2entity()`** - Transfer entire records from one entity to another
- Used for moving validated records to production entities
- Updates status params after successful transfer

**`entity_param_2_entity_param()`** - Transfer specific parameter values based on matching criteria
- Links related data across entities (e.g., supplier codes, item codes)
- Example: Transfer supplier name from Entity 4 to Entity 1 based on supplier code

**`transfer_volunteers()`** - Specialized volunteer data transfer with ID validation
- Validates Israeli ID numbers (Teudat Zehut)
- Prevents duplicate volunteers
- Marks records with validation status

**`transfer_records()`** - Generic record transfer with ID-based creation
- Creates records in destination with custom IDs from source data

---

## Entity Mapping

### **Core Entities**

| Entity ID | Name | Purpose |
|-----------|------|---------|
| 1 | FITEM | Item master data (products, SKUs) |
| 4 | SPK | Supplier master |
| 5 | ITM | Item codes |
| 6 | --- | Pallet types |
| 7 | CTR | Contracts |
| 8 | INV | Inventory transactions |
| 9 | RINV | Return inventory |
| 10 | ORD | Orders |
| 19 | DOC | Delivery documents |
| 21 | --- | Batches/Lots |
| 28 | FITEMCHECK | FITEM validation staging |
| 33 | INVFILE | INV import staging |
| 34 | ORDFILE | ORD import staging |
| 35 | --- | Warehouse locations 1 |
| 36 | --- | Warehouse locations 2 |
| 44 | TEMPORDDATES | Temporary order date tracking |

---

## File Processing

### **PreNames Class** (`PreNames.py`)

Handles CSV file import from FTP locations.

**File Types Processed:**
- `INV` - Inventory transactions
- `FITEM` - Item definitions
- `SPK` - Suppliers
- `ITM` - Item codes
- `CTR` - Contracts
- `DOC` - Documents
- `RINV` - Return inventory

**Key Methods:**
- `creating_body_to_update()` - Standard import (uses record ID from file)
- `creating_body_to_update_with_new_id()` - Import with auto-generated IDs
- `creating_body_to_update_with_new_id_INV_FITEM()` - Special INV/FITEM import with duplicate checking

**Process Flow:**
1. Extract CSV files from source folder matching file prefix
2. Check for duplicates in destination folder
3. Parse CSV and map to entity parameters
4. Handle date formatting (YYYYMMDD → YYYY-MM-DD)
5. Create/update records via API
6. Move processed files to backup folder

---

## Validation and Error Handling

### **OrdFunctions** (`OrdFunctions.py`)

Order processing with comprehensive validation.

**Validation Steps:**
1. Check if reference number exists (param 472)
2. Validate pallet number exists in inventory (Entity 8)
3. Check pallet hasn't already been shipped (Entity 19)
4. Verify reference number doesn't already exist for same supplier (Entity 10)
5. Validate reference number length (≤10 characters)
6. Check for existing order with same reference

**Status Values:**
- `1` - New request
- `2` - Waiting for reference / Request sent to ChemiPal
- `3` - Ready for validation
- `4` - Ready for numbering
- `5` - Ready for transfer
- `6` - Waiting for reference (no reference number)
- `7` - Closed - didn't pass validation
- `8` - Reference request sent
- `9` - Passed validation, waiting for INV update

### **InvFunctions** (`InvFunctions.py`)

Inventory processing with validation.

**Validation Steps:**
1. Verify reference number exists and ≤10 characters
2. Check reference isn't duplicate in Entity 8
3. Validate supplier code exists in Entity 4
4. Verify item code (makat) exists in Entity 1
5. Check pallet type matches item definition
6. Validate quantity doesn't exceed item max quantity
7. Verify expiry date/batch is provided if required
8. Check active contract exists for supplier/item/pallet combination

**Status Values:**
- `Empty` - New record
- `1` - Ready for validation
- `4` - Ready for numbering
- `5` - Ready for transfer
- `7` - Closed - didn't pass validation

### **FitemFunctions** (`FitemFunctions.py`)

Item definition validation.

**Validation Steps:**
1. Verify required fields are present (supplier code, item code, pallet type, size)
2. Check contract exists for supplier (Entity 7)
3. Validate pallet type and size combination exists in contracts
4. Check item code doesn't already exist in FITEM (Entity 1)
5. Detect duplicate entries in same import batch

---

## Order Numbering

### **OrderNumbering Class** (`OrderNumbering.py`)

Generates sequential row numbers for orders grouped by supplier + date + reference.

**Process:**
1. Query records needing numbering
2. Group by: `sapak_name + date_pickup + order_num`
3. Assign sequential numbers within each group (1, 2, 3...)
4. Update status to "Ready for transfer"

**Used for:**
- Entity 33 (INVFILE) - Inventory order numbering
- Entity 34 (ORDFILE) - Order numbering

---

## G1 User Creation

### **g1_functions.py**

Creates users in the system from G1 entity records.

**Process:**
1. Search Entity 34 for records with status = "Waiting for user creation" (param 989 = 2)
2. Validate mandatory fields (ID, name, license info)
3. Transform entity record to user format
4. Create user via `add_update_users()`
5. Update source record status to "Created as user" (param 989 = 3)

**Mandatory Fields:**
- Param 574 - ID/Username
- Param 627 - First name
- Param 628 - Last name
- Param 570 - License company code

---

## Helper Functions

### **helpers.py - Key Functions**

**`entity2entity()`**
Transfer records from one entity to another based on search criteria.
```python
entity2entity(api, origin_entity_id, dest_entity_id, search_criteria, 
              param_ids_to_transfer, param_ids_to_receive, program_status_param_id)
```

**`entity_param_2_entity_param()`**
Transfer parameter values between entities based on matching field values.
```python
entity_param_2_entity_param(api, origin_entity_id, dest_entity_id,
                            origin_param_id_to_find, dest_param_id_to_find,
                            origin_param_id_to_transfer, dest_param_id_to_recieve)
```

**`transfer_volunteers()`**
Transfer volunteer records with ID validation.
```python
transfer_volunteers(customer_name, api, origin_entity_id, dest_entity_id,
                    search_criteria, param_ids_to_transfer, param_ids_to_receive,
                    program_status_param_id, update_origin_entity_with_tz_without_zero_param)
```

**`transfer_records()`**
Transfer records with custom ID generation.
```python
transfer_records(customer_name, api, origin_entity_id, dest_entity_id,
                 search_criteria, param_ids_to_transfer, param_ids_to_receive,
                 program_status_param_id, new_id_pos)
```

**`transfer_records_based_on_blocks()`**
Transfer records with composite ID (base ID + block ID).
```python
transfer_records_based_on_blocks(customer_name, api, origin_entity_id, dest_entity_id,
                                 search_criteria, param_ids_to_transfer, param_ids_to_receive,
                                 program_status_param_id, block_param_pos, new_id_pos)
```

**`entity_2_users_delek()`**
Special function to convert Delek entity records to system users.

**`change_param_value_based_on_another_param_is_not_empty()`**
Update a parameter value if another parameter has a value.

---

## Environment Variables

Required in `.env` file:

```bash
# ChemiPal API
CHEMIPAL_DOMAIN=https://...
CHEMIPAL_API_KEY=...

# Customer APIs
RLZ_DOMAIN=...
RLZ_API_KEY=...
DELEK_DOMAIN=...
DELEK_API_KEY=...
NETANYA_DOMAIN=...
NETANYA_API_KEY=...
HOLON_DOMAIN=...
HOLON_API_KEY=...
NAMAL_DOMAIN=...
NAMAL_API_KEY=...
ASHDOD_DOMAIN=...
ASHDOD_API_KEY=...
G1_DOMAIN=...
G1_API_KEY=...

# File Paths
SOURCE_FOLDER=C:\FTP_Clients\chemipal\In
DESTINATION_FOLDER=C:\FTP_Clients\chemipal\In\backlog
CHEMIPAL_EXPORT_PATH=C:\FTP_Clients\chemipal\Out
CHEMIPAL_EXPORT_BACKUP=C:\FTP_Clients\chemipal\Out\backup
```

---

## Logging

All operations are logged to `log/log.txt` with DEBUG level.

**Log Format:**
```
YYYY-MM-DD HH:MM:SS | !----------------- [Function Name] - [Status] -----------------!
```

**Key Logging Points:**
- Function entry/exit
- API requests and responses
- Validation failures with reasons
- Error messages with stack traces
- Record counts and IDs processed

---

## Development Guidelines

### Adding New File Import

1. Add file type to `PreNames` class
2. Define entity ID and parameter mapping
3. Add to appropriate thread in `main.py`
4. Implement validation if needed
5. Add data enrichment transfers using `entity_param_2_entity_param`

### Adding New Customer Integration

1. Add domain and API key to `.env`
2. Create `HitoAPI` instance in `main.py`
3. Create new thread function
4. Define entity mappings and parameter IDs
5. Add appropriate validation

### Modifying Validation Rules

1. Locate appropriate Functions class (`OrdFunctions`, `InvFunctions`, `FitemFunctions`)
2. Update validation logic in `validate_*_rows()` method
3. Add appropriate status values
4. Update logging

### Error Handling Best Practices

- Always wrap API calls in try/except
- Log errors with context (entity ID, record ID, parameter values)
- Update status parameters to indicate error state
- Never leave records in intermediate states

---

## Common Operations

### Manual Record Transfer
```python
from helpers import entity2entity
from HitoAPI import HitoAPI

api = HitoAPI("domain", "key")
result = entity2entity(
    api=api,
    origin_entity_id=28,
    dest_entity_id=1,
    search_criteria=[{"paramId": 702, "operator": "EQ", "values": ["5"]}],
    param_ids_to_transfer=[340, 341, 342],
    param_ids_to_receive=[3, 4, 16],
    program_status_param_id=702
)
```

### Manual File Import
```python
from PreNames import PreNames
from HitoAPI import HitoAPI

api = HitoAPI("domain", "key")
importer = PreNames("INV", 8, api, "C:/source", "C:/backup")
importer.creating_body_to_update_with_new_id_INV_FITEM()
```

### Export to CSV
```python
from INVORD import INVORD
from HitoAPI import HitoAPI

api = HitoAPI("domain", "key")
exporter = INVORD(api, 8)  # 8 for INV, 10 for ORD
exporter.start()
```

---

## Data Model Insights

### Status Parameter Patterns

Most entities use a "program status" parameter to track processing state:
- Entity 28 (FITEMCHECK): param 702
- Entity 33 (INVFILE): param 701
- Entity 34 (ORDFILE): param 691

Common status values:
- Empty/undefined = New record
- 1 = Ready for validation
- 2 = Waiting/In progress
- 3 = Validated/Ready for next step
- 4 = Ready for numbering
- 5 = Ready for transfer
- 6 = Error state
- 7 = Closed/Failed validation

### Parameter ID Patterns

Common parameter purposes:
- Low IDs (1-50): Core fields (ID, name, codes)
- 100-200: Reference numbers, dates
- 200-300: Quantities, measurements
- 400-500: Advanced fields
- 500-700: Status and tracking
- 700+: Program control and workflows

---

## Troubleshooting

### File Import Issues
- Check file format matches CSV with UTF8 encoding
- Verify file is in SOURCE_FOLDER
- Check for duplicate in DESTINATION_FOLDER
- Review log for parse errors
- Validate parameter mapping

### Validation Failures
- Check entity relationships (supplier exists, item exists, etc.)
- Verify contract dates and validity
- Confirm parameter value formats (dates, numbers)
- Review search criteria in validation functions

### API Errors
- Verify API key and domain are correct
- Check network connectivity
- Review request body format
- Ensure entity IDs and parameter IDs are correct

### Threading Issues
- Check if process is stuck (review log timestamps)
- Verify time.sleep() intervals
- Look for unhandled exceptions
- Check thread join() calls

---

## Critical Business Logic

### Volunteer Transfer Validation
- ID must be numeric and > 0
- Duplicate check before creation
- Updates source with cleaned ID (no hyphens)

### Order Reference Management
- Entity 44 (TEMPORDDATES) acts as staging for reference assignment
- Grouped by supplier + date + timestamp
- Manual reference entry triggers transfer to Entity 34

### Contract Validation
- Must check expiry date (param 11 in Entity 7)
- Links: Entity 7 ← Entity 1 ← Entity 33
- Fields: supplier code + item type + pallet size

### Inventory-Order Linking
- Entity 8 (INV) param 528 = "askord" flag
- Set to 1 when order exists for that pallet
- Links via param 513 (pallet number) and param 62 (supplier)

---

## Version Control Notes

- Copy files (`*- Copy.py`, `*- Copy (2).py`) suggest iterative development
- Current production versions have no suffix
- Log files are numbered (log30.txt - log37.txt) indicating rotation

---

## Future Enhancement Considerations

1. **Error Recovery**: Add retry logic for failed API calls
2. **Monitoring**: Implement health checks and alerting
3. **Performance**: Consider batch size optimization for large imports
4. **Testing**: Add unit tests for validation logic
5. **Documentation**: Generate entity relationship diagrams
6. **Audit Trail**: Track all data changes with user/timestamp
7. **Configuration**: Move hard-coded entity/param IDs to config files

---

## Quick Reference: Entity Flow Diagram

```
CSV Files (FTP) → PreNames → Staging Entities (28, 33, 34)
                                    ↓
                              Validation Functions
                                    ↓
                              OrderNumbering
                                    ↓
                          Production Entities (1, 8, 10)
                                    ↓
                         entity_param_2_entity_param
                         (Data enrichment/linking)
                                    ↓
                              INVORD Export → CSV Files
```

---

## Contact & Support

For issues or questions about this system:
1. Review logs in `log/log.txt`
2. Check entity definitions in Hito admin panel
3. Verify parameter IDs match current configuration
4. Review recent changes in version control

---

**Last Updated**: Generated based on codebase analysis  
**Application Version**: Production (as of current codebase state)







