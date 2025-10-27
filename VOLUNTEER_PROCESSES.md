# Volunteer Transfer System - Complete Documentation

## Executive Summary

The volunteer transfer system manages **automated volunteer data migration** across three customer instances: RLZ, Netanya, and Holon. This system validates Israeli ID numbers (Teudat Zehut), prevents duplicate volunteers, and transfers volunteer records from staging entities to production volunteer entities.

**Core Business Model**: Volunteers register in a volunteering entity, the system validates their ID number, checks for duplicates, and transfers complete volunteer profiles to a dedicated volunteers entity.

---

## Table of Contents

1. [Business Context](#business-context)
2. [System Architecture](#system-architecture)
3. [Order of Actions](#order-of-actions)
4. [RLZ Volunteer Process](#rlz-volunteer-process)
5. [Netanya Volunteer Process](#netanya-volunteer-process)
6. [Holon Volunteer Process](#holon-volunteer-process)
7. [ID Number Validation Logic](#id-number-validation-logic)
8. [Duplicate Prevention](#duplicate-prevention)
9. [Error Handling](#error-handling)
10. [Status Management](#status-management)

---

# Business Context

## What the System Does

**Purpose**: Automatically transfer volunteer records from volunteering entities to dedicated volunteer databases

**Why**: 
- Centralize volunteer management
- Prevent duplicate volunteers using ID validation
- Ensure data integrity through Israeli ID number verification
- Maintain synchronized volunteer databases
- Track volunteer status across organizations

## Business Entities

### Real-World Mapping

| System Entity | Business Meaning | Purpose |
|---------------|------------------|---------|
| **Volunteering Entity** | Registration/Application | Where volunteers first register |
| **Volunteers Entity** | Master Database | Centralized volunteer directory |
| **Israeli ID (Teudat Zehut)** | Unique Identifier | Prevents duplicates |
| **Status Parameters** | Processing State | Tracks transfer progress |

### Data Flow Pattern

```
Volunteer Registers
        │
        │ Application Completed
        ▼
┌─────────────────┐
│ Volunteering    │ (Entity 31, 223, or 137)
│ Entity          │ Status = 1 (Ready)
└────────┬────────┘
         │
         │ Every 1 Hour: volunteer_processes()
         ▼
┌─────────────────┐
│  ID Validation  │ Check ID is numeric and ≠ 0
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Duplicate Check │ Query Volunteers Entity
└────────┬────────┘
         │
         │ New Volunteer → Continue
         │ Existing Volunteer → Skip
         ▼
┌─────────────────┐
│ Create Record   │ In Volunteers Entity
│ Update Status   │ In Volunteering Entity
└─────────────────┘
```

---

# System Architecture

## Threading Model

**Volunteer Process**: Runs in dedicated thread `volunteer_processes()`

```python
def volunteer_processes():
    while True:
        # 1. Transfer RLZ volunteers
        transfer_volunteers(...)  # Entity 31 → 187
        
        # 2. Transfer Netanya volunteers
        transfer_volunteers(...)  # Entity 223 → 222
        
        # 3. Transfer Holon volunteers
        transfer_volunteers(...)  # Entity 137 → 142
        
        time.sleep(3601)  # Wait 1 hour
```

**Execution Frequency**: Every 1 hour (3601 seconds)

**Sequence**: Sequential execution for each customer:
1. RLZ first
2. Netanya second
3. Holon third

---

# Order of Actions

## Complete Process Flow - Every Hour

```
┌─────────────────────────────────────────────────────────────┐
│              VOLUNTEER PROCESS CYCLE                         │
│                   (Every 1 Hour)                             │
└─────────────────────────────────────────────────────────────┘

STEP 1: START PROCESS
  └─> Log: "START Initialize volunteer_processes() one1 every one hour"

STEP 2: RLZ VOLUNTEER TRANSFER
  ├─> Query Entity 31 (RLZ volunteering) for status = 1
  ├─> Validate Israeli ID numbers
  ├─> Check for duplicates in Entity 187 (RLZ volunteers)
  ├─> Transfer valid new volunteers to Entity 187
  └─> Update Entity 31 status

STEP 3: NETANYA VOLUNTEER TRANSFER
  ├─> Query Entity 223 (Netanya volunteering) for status = 1
  ├─> Validate Israeli ID numbers
  ├─> Check for duplicates in Entity 222 (Netanya volunteers)
  ├─> Transfer valid new volunteers to Entity 222
  └─> Update Entity 223 status

STEP 4: HOLON VOLUNTEER TRANSFER
  ├─> Query Entity 137 (Holon volunteering) for status = 1
  ├─> Validate Israeli ID numbers
  ├─> Check for duplicates in Entity 142 (Holon volunteers)
  ├─> Transfer valid new volunteers to Entity 142
  └─> Update Entity 137 status

STEP 5: END PROCESS
  └─> Log: "END Initialize volunteer_processes() one1 every one hour"

STEP 6: SLEEP
  └─> Wait 3601 seconds (1 hour, 1 second)

REPEAT: Loop continues indefinitely
```

---

# RLZ Volunteer Process

## Configuration

**API**: `rlz` HitoAPI instance  
**Origin Entity**: 31 (RLZ volunteering/registration)  
**Destination Entity**: 187 (RLZ volunteers master)  
**Status Parameter**: 4592 (program status)  
**Update Parameter**: 4421 (stores destination record ID)

## Parameter Mapping (16 Fields)

| Source Param (Entity 31) | Destination Param (Entity 187) | Field Purpose |
|---------------------------|-------------------------------|---------------|
| 532 | 4238 | Field 1 (ID number) |
| 524 | 4229 | Field 2 |
| 529 | 4235 | Field 3 |
| 530 | 4236 | Field 4 |
| 535 | 4242 | Field 5 |
| 536 | 4243 | Field 6 |
| 537 | 4244 | Field 7 |
| 538 | 4245 | Field 8 |
| 539 | 4246 | Field 9 |
| 531 | 4237 | Field 10 |
| 903 | 4239 | Field 11 |
| 533 | 4240 | Field 12 |
| 534 | 4241 | Field 13 |
| 540 | 4247 | Field 14 |
| 3648 | 4248 | Field 15 |
| 2765 | 4510 | Field 16 |

## Process Steps

### Step 1: Query Volunteering Entity
```python
results = api.get_records_by_search_criteria_and_params(
    entity_id=31,  # RLZ volunteering
    params=param_ids_to_transfer,
    searchCriterias=[{"paramId": 4592, "operator": "EQ", "values": [1]}]
)
```

**Purpose**: Find all records with status = 1 (Ready for transfer)

### Step 2: Validate Each Record

For each record found:

#### A. Check ID Field (First Parameter)
```python
if "value" in record["paramValues"][0]:  # Parameter 532
    if record["paramValues"][0]["value"].isnumeric():
        if int(record["paramValues"][0]["value"]) != 0:
            # Valid ID, continue processing
        else:
            # ID is zero - invalid
            status = "נבדק - תז לא תקין"
    else:
        # ID is not numeric - invalid
        status = "נבדק - תז לא תקין"
else:
    # No ID value - invalid
    status = "נבדק - תז לא תקין"
```

**Validation Rules**:
1. ID field must exist
2. ID must be numeric
3. ID must not be zero

### Step 3: Check for Duplicate

```python
is_vol_exists = api.get_records_by_search_criteria_and_params(
    entity_id=187,  # RLZ volunteers
    params=[4238],  # ID field
    searchCriterias=[{
        "paramId": 4238,
        "operator": "EQ",
        "values": [int(id_number)]
    }]
)
```

**Purpose**: Prevent duplicate volunteers

**Business Rule**: Same ID number cannot exist in volunteers entity

### Step 4: Decision Logic

```python
if "records" in is_vol_exists:
    # Volunteer already exists
    status = "נבדק - תקין"  # Checked - Valid (already processed)
else:
    # New volunteer - transfer to Entity 187
    create_record_in_volunteers_entity()
```

**Two Scenarios**:

**Scenario A - Duplicate Found**:
```
Volunteer ID 123456789 already exists in Entity 187
  → Update status to "נבדק - תקין" (Checked - Valid)
  → Do NOT create new record
  → Prevents duplicate volunteers
```

**Scenario B - New Volunteer**:
```
Volunteer ID 987654321 does NOT exist in Entity 187
  → Create new record in Entity 187
  → Update status to "נבדק - תקין"
  → Store destination record ID back in Entity 31
```

### Step 5: Create Volunteer Record

```python
dest_record = {
    "recordId": int(id_number),  # Use ID as record ID
    "paramValues": [
        {
            "id": destination_param_id,
            "value": source_value,
            "valueId": source_valueId  # If exists
        }
        # ... for all 16 parameters
    ]
}
```

**Key Feature**: Record ID is the Israeli ID number

### Step 6: Update Volunteering Entity Status

```python
origin_entity_body["records"].append({
    "recordId": record["recordId"],
    "paramValues": [
        {
            "id": 4592,  # Program status
            "valueId": 2  # "נבדק - תקין"
        },
        {
            "id": 4421,  # Store destination record ID
            "value": dest_record["recordId"]
        }
    ]
})
```

**Purpose**: Mark record as transferred and store link to destination

### Step 7: Batch Update

```python
# Update origin entity first
api.create_or_update_multi_records(origin_entity_body)

# Then create volunteers in destination
api.create_or_update_multi_records(dest_entity_body)
```

**Order**: Origin first, then destination (ensures status updates even if creation fails)

---

# Netanya Volunteer Process

## Configuration

**API**: `netanya` HitoAPI instance  
**Origin Entity**: 223 (Netanya volunteering)  
**Destination Entity**: 222 (Netanya volunteers master)  
**Status Parameter**: 5294 (program status)  
**Update Parameter**: 5270 (stores destination record ID)

## Parameter Mapping (14 Fields)

| Source Param | Destination Param | Notes |
|--------------|-------------------|-------|
| 5263 → 5063 | First parameter (ID) |
| 5262 → 5064 | |
| 5271 → 5065 | |
| 5264 → 5060 | |
| ... (14 total) | |

**Process Steps**: Same as RLZ (validate ID, check duplicates, transfer, update status)

---

# Holon Volunteer Process

## Configuration

**API**: `holon` HitoAPI instance  
**Origin Entity**: 137 (Holon volunteering)  
**Destination Entity**: 142 (Holon volunteers master)  
**Status Parameter**: 2687 (program status)  
**Update Parameter**: 2457 (stores destination record ID)

## Parameter Mapping (24 Fields)

| Source Param | Destination Param | Notes |
|--------------|-------------------|-------|
| 2248 → 2688 | First parameter (ID) |
| 2246 → 2358 | |
| 2247 → 2359 | |
| ... (24 total) | |

**Process Steps**: Same as RLZ and Netanya

---

# ID Number Validation Logic

## Israeli ID Number (Teudat Zehut)

### Requirements

1. **Presence**: ID field must have a value
2. **Numeric**: Must be numeric digits only
3. **Non-Zero**: Cannot be 0
4. **Length**: Typically 9 digits (enforced by validation)

### Validation Code Breakdown

```python
# Step 1: Check if value exists
if "value" in record["paramValues"][0]:
    
    # Step 2: Check if numeric
    if record["paramValues"][0]["value"].isnumeric():
        
        # Step 3: Convert to integer
        id_number = int(record["paramValues"][0]["value"])
        
        # Step 4: Check not zero
        if id_number != 0:
            # ✓ VALID ID
            # Continue with duplicate check and transfer
        else:
            # ✗ ID is zero
            status = "נבדק - תז לא תקין"
    else:
        # ✗ ID contains non-numeric characters
        status = "נבדק - תז לא תקין"
else:
    # ✗ No ID value provided
    status = "נבדק - תז לא תקין"
```

## Error Messages

| Status | Hebrew | English | Meaning |
|--------|--------|---------|---------|
| `valueId: 3` | נבדק - תז לא תקין | Checked - ID invalid | ID validation failed |
| `valueId: 2` | נבדק - תקין | Checked - Valid | Successfully transferred |

---

# Duplicate Prevention

## How Duplicate Prevention Works

### Business Problem

**Issue**: Same volunteer could register multiple times in volunteering entity

**Solution**: Check if volunteer already exists in volunteers entity before creating

### Technical Implementation

```python
# 1. Extract ID from volunteering record
id_number = int(record["paramValues"][0]["value"])

# 2. Search for existing volunteer
is_vol_exists = api.get_records_by_search_criteria_and_params(
    entity_id=dest_entity_id,
    params=[dest_param_ids[0]],
    searchCriterias=[{
        "paramId": dest_param_ids[0],
        "operator": "EQ",
        "values": [id_number]
    }]
)

# 3. Check results
if "records" in is_vol_exists:
    # Volunteer already exists
    # Mark as processed but don't create again
    status = "נבדק - תקין"
else:
    # New volunteer - create record
    create_in_volunteers_entity()
```

## Duplicate Scenarios

### Scenario 1: First Time Registration
```
Volunteering Entity (31):
  Record: ID = 123456789 (NEW)
  
Query Volunteers Entity (187):
  Result: No record found
  
Action: Create new volunteer in Entity 187
Status: "נבדק - תקין"
```

### Scenario 2: Duplicate Registration
```
Volunteering Entity (31):
  Record 1: ID = 123456789 (already processed)
  Record 2: ID = 123456789 (DUPLICATE)
  
Query Volunteers Entity (187):
  Result: Record with ID 123456789 EXISTS
  
Action: Skip duplicate, mark as processed
Status: "נבדק - תקין"
```

**Business Benefit**: Prevents creating duplicate volunteer records, maintains data integrity

---

# Error Handling

## Error Scenarios

### Scenario 1: API Connection Failure

**Trigger**: Cannot connect to HitoAPI

**Code**:
```python
except Exception as e:
    logging.info(f'ERROR MESSAGE {e}')
    return False
```

**Business Impact**: Process stops, no volunteers transferred this cycle

**Recovery**: Process retries in next cycle (1 hour later)

### Scenario 2: Invalid ID Number

**Trigger**: ID is non-numeric, zero, or missing

**Code**:
```python
origin_entity_body["records"].append({
    "recordId": record["recordId"],
    "paramValues": [{
        "id": program_status_param_id,
        "valueId": 3,
        "value": "נבדק - תז לא תקין"
    }]
})
```

**Business Impact**: Record marked as invalid, not transferred

**Recovery**: Manual intervention to correct ID number

### Scenario 3: Duplicate Check Failure

**Trigger**: Error checking for duplicates

**Code**:
```python
except Exception as e:
    last_record_error = True
    break
```

**Business Impact**: Record skipped, no transfer attempted

**Recovery**: Process retries in next cycle

### Scenario 4: Destination Entity Update Failure

**Trigger**: Cannot create records in volunteers entity

**Code**:
```python
except Exception as e:
    logging.info(f'ERROR MESSAGE {e}')
    return False
```

**Business Impact**: Status updated in volunteering entity, but volunteer not created

**Recovery**: Manually fix volunteers entity issue, re-run process

---

# Status Management

## Status Lifecycle

```
┌─────────────────┐
│ Volunteering    │ Status = 1 (Ready for Transfer)
│ Entity (New)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ID Validation   │
└────────┬────────┘
         │
         ├─> Valid ID → Continue
         └─> Invalid ID → Status = 3 (נבדק - תז לא תקין)
         │
         ▼
┌─────────────────┐
│ Duplicate Check │
└────────┬────────┘
         │
         ├─> New Volunteer → Create in Volunteers Entity
         └─> Existing → Skip Creation
         │
         ▼
┌─────────────────┐
│ Status Update   │ Status = 2 (נבדק - תקין)
│ Store Link      │ Store destination record ID
└─────────────────┘
```

## Status Values

| Value ID | Hebrew | English | Meaning |
|----------|--------|---------|---------|
| `1` | - | Ready | Record ready for processing |
| `2` | נבדק - תקין | Checked - Valid | Successfully processed |
| `3` | נבדק - תז לא תקין | Checked - ID Invalid | ID validation failed |

## Status Parameter Locations

| Customer | Status Param ID | Entity | Location |
|----------|-----------------|--------|----------|
| **RLZ** | 4592 | 31 (origin) | Volunteering entity |
| **Netanya** | 5294 | 223 (origin) | Volunteering entity |
| **Holon** | 2687 | 137 (origin) | Volunteering entity |

---

# Summary

## Volunteer Transfer in One Page

**What It Does**:
- Transfers volunteers from registration (volunteering) to master database (volunteers)
- Validates Israeli ID numbers to ensure data quality
- Prevents duplicate volunteers
- Operates automatically every hour

**Key Business Processes**:
1. **RLZ**: Entity 31 → 187 (16 fields)
2. **Netanya**: Entity 223 → 222 (14 fields)
3. **Holon**: Entity 137 → 142 (24 fields)

**Critical Success Factors**:
- ✅ **Valid Israeli ID**: Must be numeric and non-zero
- ✅ **No Duplicates**: Check before creating
- ✅ **ID-Based Records**: Record ID is the Israeli ID number
- ✅ **Status Tracking**: Track processing state

**System Characteristics**:
- **Frequency**: Every 1 hour
- **Validation**: Israeli ID number validation
- **Error Handling**: Mark invalid records, prevent duplicates
- **Performance**: Handles multiple customers sequentially

**Value Delivered**:
- Automated volunteer management
- Data integrity through ID validation
- Duplicate prevention
- Synchronized volunteer databases
- Status tracking and auditing

**Business Model**:
Volunteer transfer system ensures that volunteers who register are automatically validated, deduplicated, and transferred to centralized volunteer databases, maintaining data quality and preventing duplicates across RLZ, Netanya, and Holon organizations.

---

**Document Version**: 1.0  
**Last Updated**: 2024-10-22  
**Business Domain**: Volunteer Management / Data Synchronization  
**System**: Volunteer Transfer Pipeline



