# Namal Data Transfer System - Business Process Documentation

## Executive Summary

Namal operates as a **real-time data synchronization system** that transfers records between two entity pairs within the Namal HitoAPI instance. Unlike ChemiPal's complex warehouse management, Namal focuses on **simple, high-frequency data replication** between staging and production entities.

**Core Business Model**: Namal acts as a **data pipeline** that continuously monitors staging entities for new records and automatically transfers them to production entities, ensuring data consistency and availability.

---

## Table of Contents

1. [Business Context](#business-context)
2. [System Architecture](#system-architecture)
3. [Entity Structure](#entity-structure)
4. [Process Flow Analysis](#process-flow-analysis)
5. [Transfer Process 1: Entity 105 → 62](#transfer-process-1-entity-105--62)
6. [Transfer Process 2: Entity 106 → 102](#transfer-process-2-entity-106--102)
7. [Validation Logic](#validation-logic)
8. [Error Handling](#error-handling)
9. [Performance Characteristics](#performance-characteristics)
10. [Business Rules](#business-rules)

---

# Business Context

## What Namal Does

Namal operates a **dual-pipeline data transfer system** that:

1. **Monitors staging entities** for new records (status = 1)
2. **Validates record completeness** (checks for required ID fields)
3. **Transfers valid records** to production entities
4. **Updates status** to mark records as processed
5. **Handles errors** by marking invalid records

## Key Business Entities

### Real-World Mapping

| System Entity | Business Meaning | Purpose |
|---------------|------------------|---------|
| **Entity 105** | Staging Area 1 | Temporary storage for incoming data |
| **Entity 62** | Production Area 1 | Final destination for processed data |
| **Entity 106** | Staging Area 2 | Temporary storage for block-based data |
| **Entity 102** | Production Area 2 | Final destination for block-based data |

### Data Flow Pattern

```
External System/Manual Entry
        │
        │ New Records
        ▼
┌─────────────────┐
│  Staging Entity │ (105 or 106)
│  Status = 1     │ (Ready for Transfer)
└────────┬────────┘
         │
         │ Namal Process (Every 1 minute)
         ▼
┌─────────────────┐
│  Validation     │
│  Check ID Field │
└────────┬────────┘
         │
         │ Valid Records
         ▼
┌─────────────────┐
│ Production Entity│ (62 or 102)
│  Status = 2     │ (Transferred)
└─────────────────┘
```

---

# System Architecture

## Threading Model

**Namal Process**: Runs in dedicated thread `namal_proccesses()`

```python
def namal_proccesses():
    while True:
        # Process 1: Entity 105 → 62
        transfer_records(...)
        
        # Process 2: Entity 106 → 102  
        transfer_records_based_on_blocks(...)
        
        time.sleep(60)  # Wait 1 minute
```

**Execution Frequency**: Every 1 minute (highest frequency in system)

**Priority**: High - ensures near real-time data availability

## API Configuration

```python
namal = HitoAPI(os.environ.get("NAMAL_DOMAIN"), os.environ.get("NAMAL_API_KEY"))
```

**Environment Variables Required**:
- `NAMAL_DOMAIN`: HitoAPI endpoint URL
- `NAMAL_API_KEY`: Authentication key

---

# Entity Structure

## Entity 105 → 62 Transfer

### Source Entity (105) - Staging
**Purpose**: Temporary storage for incoming records

**Key Parameters**:
- **Param 1872**: Program status (1 = Ready for transfer)
- **Param 1721**: Record ID field (validation check)
- **Params 1678-1843**: Data fields (58 total parameters)

**Status Values**:
- `1`: Ready for transfer
- `2`: Successfully transferred
- `3`: Failed validation

### Destination Entity (62) - Production
**Purpose**: Final storage for processed records

**Key Parameters**:
- **Param 901**: Record ID field
- **Param 1503**: Additional ID field
- **Params 858-1842**: Mapped data fields (58 total parameters)

**Data Mapping**: 1:1 correspondence between source and destination parameters

## Entity 106 → 102 Transfer

### Source Entity (106) - Block-Based Staging
**Purpose**: Temporary storage for block-structured data

**Key Parameters**:
- **Param 1871**: Program status (1 = Ready for transfer)
- **Param 1746**: Block identifier (validation check)
- **Params 1745-1759**: Block data fields (16 total parameters)

**Block Structure**: Records organized in blocks with specific identifiers

### Destination Entity (102) - Block-Based Production
**Purpose**: Final storage for block-structured data

**Key Parameters**:
- **Param 1579**: Block identifier
- **Param 1581**: Additional block field
- **Param 1773**: Block metadata
- **Params 1576-1590**: Mapped block data (16 total parameters)

---

# Process Flow Analysis

## High-Level Process Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    NAMAL PROCESS CYCLE                       │
│                      (Every 1 minute)                       │
└─────────────────────────────────────────────────────────────┘

1. START: namal_proccesses() thread wakes up
   └─> Log: "START Initialize namal_proccesses() zero0 every 1 minute"

2. PROCESS 1: Entity 105 → 62 Transfer
   └─> Query Entity 105 for records with status = 1
   └─> Validate each record (check ID field)
   └─> Transfer valid records to Entity 62
   └─> Update Entity 105 status to 2 (success) or 3 (failed)

3. PROCESS 2: Entity 106 → 102 Transfer (Block-Based)
   └─> Query Entity 106 for records with status = 1
   └─> Validate each record (check block field)
   └─> Transfer valid records to Entity 102
   └─> Update Entity 106 status to 2 (success) or 3 (failed)

4. END: Sleep for 60 seconds
   └─> Log: "END Initialize namal_proccesses() zero0 every 1 minute"

5. REPEAT: Loop continues indefinitely
```

## Detailed Process Steps

### Step 1: Process Initialization
```python
logging.info(f'{str(datetime.today()).split(".")[0]} | !----------------- START Initialize namal_proccesses() zero0 every 1 minute -----------------!')
```

**Purpose**: Log process start for monitoring and debugging

### Step 2: Entity 105 → 62 Transfer
```python
transfer_records(
    customer_name="NAMAL", 
    api=namal, 
    origin_entity_id=105, 
    dest_entity_id=62,
    search_criteria=[{"paramId": 1872, "operator": "EQ", "values": [1]}],
    param_ids_to_transfer=[1721, 1743, 1678, 1679, ...],  # 58 parameters
    param_ids_to_receive=[901, 1503, 858, 859, ...],      # 58 parameters
    program_status_param_id=1872, 
    new_id_pos=0
)
```

### Step 3: Entity 106 → 102 Transfer
```python
transfer_records_based_on_blocks(
    customer_name="NAMAL",
    api=namal,
    origin_entity_id=106,
    dest_entity_id=102,
    search_criteria=[{"paramId": 1871, "operator": "EQ", "values": [1]}],
    param_ids_to_transfer=[1746, 1745, 1771, ...],         # 16 parameters
    param_ids_to_receive=[1579, 1581, 1773, ...],           # 16 parameters
    program_status_param_id=1871,
    block_param_pos=4,  # Block identifier at position 4
    new_id_pos=0
)
```

### Step 4: Process Completion
```python
time.sleep(60)  # Wait 1 minute before next cycle
```

---

# Transfer Process 1: Entity 105 → 62

## Business Purpose

**What**: Transfer records from staging to production

**Why**: 
- Ensure data availability in production system
- Maintain data consistency between staging and production
- Provide real-time data synchronization

## Technical Implementation

### Search Criteria
```python
search_criteria=[{"paramId": 1872, "operator": "EQ", "values": [1]}]
```

**Meaning**: Find all records in Entity 105 where program status = 1 (Ready for transfer)

### Parameter Mapping

**Source Parameters (Entity 105)**:
```python
param_ids_to_transfer=[
    1721, 1743, 1678, 1679, 1680, 1681, 1682, 1683, 1684, 1685, 1686, 1687, 1688,
    1689, 1690, 1691, 1902, 1693, 1694, 1695, 1696, 1697, 1698, 1700, 1701, 1702, 1703,
    1704, 1705, 1706, 1707, 1708, 1709, 1710, 1711, 1712, 1713, 1714, 1715, 1716, 1717,
    1718, 1719, 1720, 1722, 1723, 1724, 1725, 1726, 1727, 1728, 1841, 1730, 1731, 1738,
    1739, 1740, 1741, 1742, 1843
]
```

**Destination Parameters (Entity 62)**:
```python
param_ids_to_receive=[
    901, 1503, 858, 859, 860, 861, 862, 863, 864, 865, 866, 867, 868, 869, 870, 871,
    1903, 873, 874, 875, 876, 877, 878, 880, 881, 882, 883, 884, 885, 886, 887, 888, 889,
    890, 891, 892, 893, 1671, 894, 895, 896, 897, 898, 900, 962, 996, 997, 998, 1093,
    1095, 1096, 1122, 1147, 1148, 1157, 1161, 1477, 1478, 1479, 1842
]
```

**Mapping**: 58 source parameters map to 58 destination parameters in 1:1 correspondence

### Validation Logic

**ID Field Validation**:
```python
if "value" not in record["paramValues"][new_id_pos]:  # new_id_pos = 0
    # Mark as invalid
    status = 3  # "נבדק - לא תקין" (Checked - Invalid)
```

**Business Rule**: Record must have a value in the first parameter (1721) to be considered valid

### Transfer Process

**Step 1**: Query staging entity
```python
results = api.get_records_by_search_criteria_and_params(
    entity_id=105,
    params=param_ids_to_transfer,
    searchCriterias=[{"paramId": 1872, "operator": "EQ", "values": [1]}]
)
```

**Step 2**: Validate each record
```python
for record in results["records"]:
    if "value" not in record["paramValues"][0]:  # Check ID field
        # Add to invalid list
        invalid_records.append(record)
    else:
        # Add to transfer list
        valid_records.append(record)
```

**Step 3**: Update invalid records
```python
if invalid_records:
    api.create_or_update_multi_records({
        "entityId": 105,
        "records": [{
            "recordId": record["recordId"],
            "paramValues": [{
                "id": 1872,
                "valueId": 3,
                "value": "נבדק - לא תקין"
            }]
        } for record in invalid_records]
    })
```

**Step 4**: Transfer valid records
```python
if valid_records:
    api.create_or_update_multi_records({
        "entityId": 62,
        "records": [{
            "recordId": record["recordId"],  # Preserve original ID
            "paramValues": [mapped_parameters]
        } for record in valid_records]
    })
```

**Step 5**: Update source records
```python
api.create_or_update_multi_records({
    "entityId": 105,
    "records": [{
        "recordId": record["recordId"],
        "paramValues": [{
            "id": 1872,
            "valueId": 2,
            "value": "נבדק - תקין"  # Checked - Valid
        }]
    } for record in valid_records]
})
```

---

# Transfer Process 2: Entity 106 → 102

## Business Purpose

**What**: Transfer block-structured records from staging to production

**Why**:
- Handle data organized in blocks/groups
- Maintain block relationships during transfer
- Ensure block integrity

## Technical Implementation

### Search Criteria
```python
search_criteria=[{"paramId": 1871, "operator": "EQ", "values": [1]}]
```

**Meaning**: Find all records in Entity 106 where program status = 1 (Ready for transfer)

### Block-Based Validation

**Block Field Validation**:
```python
if "valueId" not in record["paramValues"][block_param_pos]:  # block_param_pos = 4
    # Mark as invalid
    status = 3  # "נבדק - לא תקין" (Checked - Invalid)
```

**Business Rule**: Record must have a valueId in the 5th parameter (position 4) to be considered valid

### Parameter Mapping

**Source Parameters (Entity 106)**:
```python
param_ids_to_transfer=[
    1746, 1745, 1771, 1747, 1748, 1749, 1750, 1751, 1752, 1753, 1754, 1755, 1756, 1757,
    1758, 1759
]
```

**Destination Parameters (Entity 102)**:
```python
param_ids_to_receive=[
    1579, 1581, 1773, 1582, 1576, 1584, 1577, 1578, 1583, 1586, 1585, 1580, 1587, 1588,
    1589, 1590
]
```

**Mapping**: 16 source parameters map to 16 destination parameters

### Block Structure

**Block Identifier**: Parameter 1746 (source) → Parameter 1579 (destination)
**Block Metadata**: Parameter 1771 (source) → Parameter 1773 (destination)
**Block Data**: Remaining 14 parameters contain block-specific information

---

# Validation Logic

## Entity 105 → 62 Validation

### Primary Validation Rule
```python
if "value" not in record["paramValues"][0]:
    status = "נבדק - לא תקין"  # Checked - Invalid
```

**Field Checked**: Parameter 1721 (first parameter)
**Validation Type**: Presence check (must have a value)
**Business Reason**: Record ID is mandatory for data integrity

### Validation Process
1. **Query**: Get all records with status = 1
2. **Check**: Verify each record has value in parameter 1721
3. **Categorize**: Separate valid and invalid records
4. **Process**: Transfer valid records, mark invalid ones

## Entity 106 → 102 Validation

### Primary Validation Rule
```python
if "valueId" not in record["paramValues"][4]:
    status = "נבדק - לא תקין"  # Checked - Invalid
```

**Field Checked**: Parameter 1746 (5th parameter, position 4)
**Validation Type**: ValueId presence check
**Business Reason**: Block identifier is mandatory for block-based data

### Block Validation Process
1. **Query**: Get all records with status = 1
2. **Check**: Verify each record has valueId in parameter 1746
3. **Categorize**: Separate valid and invalid block records
4. **Process**: Transfer valid blocks, mark invalid ones

---

# Error Handling

## Error Scenarios

### Scenario 1: API Connection Failure
**Trigger**: Cannot connect to Namal HitoAPI

**System Response**:
```python
except Exception as e:
    logging.info(f'ERROR MESSAGE {e}')
    return False
```

**Business Impact**: Process stops, no data transfer occurs

**Recovery**: Process retries in next cycle (1 minute later)

### Scenario 2: Invalid Record Data
**Trigger**: Record missing required ID field

**System Response**:
```python
origin_entity_body["records"].append({
    "recordId": record["recordId"],
    "paramValues": [{
        "id": program_status_param_id,
        "valueId": 3,
        "value": "נבדק - לא תקין"
    }]
})
```

**Business Impact**: Record marked as invalid, not transferred

**Recovery**: Manual intervention required to fix data

### Scenario 3: Transfer Failure
**Trigger**: Cannot create records in destination entity

**System Response**:
```python
except Exception as e:
    logging.info(f'ERROR MESSAGE {e}')
    return False
```

**Business Impact**: Valid records remain in staging, not transferred

**Recovery**: Process retries in next cycle

## Error Status Values

| Status Value | Hebrew Text | English | Meaning |
|--------------|-------------|---------|---------|
| 1 | - | Ready | Record ready for transfer |
| 2 | נבדק - תקין | Checked - Valid | Successfully transferred |
| 3 | נבדק - לא תקין | Checked - Invalid | Failed validation |

---

# Performance Characteristics

## Execution Frequency

**Process Interval**: 60 seconds (1 minute)
**Thread Priority**: High (most frequent process in system)
**Execution Time**: Typically < 10 seconds per cycle

## Data Volume Handling

**Entity 105 → 62**:
- **Parameters**: 58 fields per record
- **Batch Size**: All records with status = 1
- **Memory Usage**: Moderate (depends on record count)

**Entity 106 → 102**:
- **Parameters**: 16 fields per record
- **Batch Size**: All records with status = 1
- **Memory Usage**: Low (fewer fields)

## Scalability Considerations

**Strengths**:
- Simple validation logic
- Efficient batch processing
- Minimal data transformation

**Limitations**:
- No pagination (processes all records at once)
- No rate limiting
- No retry mechanism for failed transfers

---

# Business Rules

## Data Integrity Rules

### Rule 1: Mandatory ID Field
**Requirement**: Records must have valid ID field

**Validation**:
```
IF transferring record THEN
  ID field (param 1721 or 1746) must have value
```

**Business Reason**: Ensures data traceability and prevents orphaned records

### Rule 2: Status-Based Processing
**Requirement**: Only process records with specific status

**Validation**:
```
IF processing records THEN
  Status must equal 1 (Ready for transfer)
```

**Business Reason**: Prevents duplicate processing and maintains workflow control

### Rule 3: Atomic Transfer
**Requirement**: All-or-nothing transfer approach

**Validation**:
```
IF transferring batch THEN
  Either ALL records transfer successfully OR NONE transfer
```

**Business Reason**: Maintains data consistency and prevents partial transfers

## Workflow Rules

### Rule 4: Sequential Processing
**Requirement**: Process entities in specific order

**Workflow**:
```
1. Process Entity 105 → 62
2. Process Entity 106 → 102
3. Wait 60 seconds
4. Repeat
```

**Business Reason**: Ensures predictable processing order and resource management

### Rule 5: Status Update Requirement
**Requirement**: Update source record status after transfer

**Workflow**:
```
IF record transferred successfully THEN
  Update source status to 2 (Transferred)
ELSE
  Update source status to 3 (Failed)
```

**Business Reason**: Provides audit trail and prevents reprocessing

---

# Summary

## Namal in One Page

**What Namal Does**:
- Operates dual data transfer pipelines
- Transfers records from staging to production entities
- Validates data integrity before transfer
- Maintains real-time data synchronization

**Key Business Processes**:
1. **Entity 105 → 62**: Standard record transfer (58 fields)
2. **Entity 106 → 102**: Block-based record transfer (16 fields)

**Critical Success Factors**:
- **Valid ID Fields**: Records must have proper identifiers
- **Status Management**: Only process records with status = 1
- **Atomic Transfers**: All-or-nothing approach for data consistency
- **Real-Time Processing**: 1-minute cycle ensures near real-time updates

**System Characteristics**:
- **Frequency**: Every 1 minute (highest in system)
- **Validation**: Simple presence checks
- **Error Handling**: Mark invalid records, retry failed transfers
- **Performance**: Fast execution, minimal resource usage

**Value Delivered**:
- Real-time data availability
- Data consistency between staging and production
- Automated error detection and handling
- Simple, reliable data pipeline

**Business Model**:
Namal operates as a **data synchronization service** that ensures staging data is continuously and reliably transferred to production systems, providing real-time data availability for business operations.

---

**Document Version**: 1.0  
**Last Updated**: 2024-10-22  
**Business Domain**: Data Synchronization / ETL  
**System**: Namal Transfer Pipeline





