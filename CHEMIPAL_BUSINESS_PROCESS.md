# ChemiPal Warehouse Management System - Business Process Documentation

## Executive Summary

ChemiPal is a **warehouse inventory and order management system** that operates as an intermediary between suppliers and customers. The system manages:

- **Incoming Inventory**: Receiving goods from multiple suppliers
- **Product Catalog**: Managing item definitions, specifications, and contracts
- **Inventory Tracking**: Real-time pallet-level inventory management
- **Outbound Orders**: Processing and fulfilling customer orders
- **Data Integration**: Bi-directional file exchange with external ERP systems

**Core Business Model**: ChemiPal acts as a **logistics hub** that receives products from various suppliers, stores them in a warehouse, and fulfills orders by shipping products to end customers.

---

## Table of Contents

1. [Business Context](#business-context)
2. [Master Data Structure](#master-data-structure)
3. [Complete Process Flow](#complete-process-flow)
4. [Inventory Receiving Process (INV)](#inventory-receiving-process-inv)
5. [Item Definition Process (FITEM)](#item-definition-process-fitem)
6. [Order Fulfillment Process (ORD)](#order-fulfillment-process-ord)
7. [Supporting Processes](#supporting-processes)
8. [Business Rules & Validations](#business-rules--validations)
9. [Integration Points](#integration-points)
10. [Exception Handling](#exception-handling)

---

# Business Context

## What ChemiPal Does

ChemiPal operates a **contract-based warehouse** where:

1. **Suppliers** deliver products to the ChemiPal warehouse
2. **Products** are received, verified, and stored on pallets
3. **Inventory** is tracked at the pallet level with batch/lot numbers
4. **Customers** place orders for products
5. **Orders** are fulfilled by retrieving pallets from inventory
6. **Delivery documents** are created and products shipped

## Key Business Entities

### Real-World Mapping

| System Entity | Business Meaning | Example |
|---------------|------------------|---------|
| **Supplier (SPK)** | Company providing products | ABC Chemicals Ltd |
| **Item (FITEM)** | Product in catalog | Liquid Soap 5L |
| **Contract (CTR)** | Agreement between supplier & ChemiPal | ABC-2024-001 |
| **Inventory (INV)** | Physical goods received | Pallet #12345 with 100 units |
| **Order (ORD)** | Request to ship products | Order #ORD-001 for 50 units |
| **Document (DOC)** | Delivery confirmation | Delivery note #DN-001 |

---

# Master Data Structure

## Entity Relationship Overview

```
┌──────────────┐
│   Supplier   │ (Entity 4 - SPK)
│   (SPK)      │
└──────┬───────┘
       │
       │ has contracts for
       ▼
┌──────────────┐      ┌──────────────┐
│   Contract   │◄─────│  Pallet Type │ (Entity 6)
│    (CTR)     │      │    Sizes     │
│  Entity 7    │      └──────────────┘
└──────┬───────┘
       │
       │ defines products
       ▼
┌──────────────┐      ┌──────────────┐
│     Item     │◄─────│  Item Codes  │ (Entity 5 - ITM)
│   (FITEM)    │      │    (ITM)     │
│   Entity 1   │      └──────────────┘
└──────┬───────┘
       │
       │ used in
       ├─────────────────────┐
       ▼                     ▼
┌──────────────┐      ┌──────────────┐
│  Inventory   │      │    Order     │
│    (INV)     │─────►│    (ORD)     │
│   Entity 8   │      │   Entity 10  │
└──────────────┘      └──────────────┘
       ▲                     │
       │                     │
       │                     ▼
┌──────────────┐      ┌──────────────┐
│  Return Inv  │      │   Document   │
│   (RINV)     │      │    (DOC)     │
│   Entity 9   │      │   Entity 19  │
└──────────────┘      └──────────────┘
```

## Critical Master Data

### 1. Suppliers (Entity 4 - SPK)
- Supplier code (unique identifier)
- Supplier name
- Contact information
- **Imported from**: SPK*.csv files (every 30 minutes)

### 2. Contracts (Entity 7 - CTR)
- Supplier reference
- Product type
- Pallet size specifications
- Valid from/to dates
- Expiry/batch requirements
- **Imported from**: CTR*.csv files (every 30 minutes)

### 3. Item Codes (Entity 5 - ITM)
- ChemiPal internal item codes
- Mapping to supplier codes
- **Imported from**: ITM*.csv files (every 30 minutes)

### 4. Items/Products (Entity 1 - FITEM)
- Product master record
- Supplier code
- Item code (מק"ט כמיפל)
- Pallet type and size
- Batch/expiry settings
- Max quantity per pallet
- Warehouse locations
- **Imported from**: FITEM*.csv files (every 7 minutes)

---

# Complete Process Flow

## High-Level Business Cycle

```
┌─────────────────────────────────────────────────────────────┐
│                     DAILY OPERATIONS                         │
└─────────────────────────────────────────────────────────────┘

1. MORNING: Supplier Deliveries Arrive
   └─> Physical goods arrive at warehouse
   └─> Delivery notes received
   └─> Warehouse staff scan/count goods

2. DATA ENTRY: Information Captured
   └─> External ERP generates INV*.csv files
   └─> Files contain: supplier, item, quantity, pallet#, batch, expiry
   └─> Files placed in FTP folder

3. AUTOMATIC IMPORT: ChemiPal Processes (Every 7 minutes)
   └─> System reads INV files
   └─> Validates against contracts, items, suppliers
   └─> Creates inventory records
   └─> Generates delivery confirmations

4. AFTERNOON: Customer Orders
   └─> Sales team receives customer orders
   └─> External system generates ORD*.csv files
   └─> Files contain: customer, item, quantity, pallet#

5. ORDER PROCESSING: ChemiPal Validates (Every 7 minutes)
   └─> Verifies inventory availability
   └─> Checks pallet not already shipped
   └─> Creates order records
   └─> Generates picking lists

6. EVENING: Export to ERP
   └─> ChemiPal exports INV.csv (hourly)
   └─> ChemiPal exports ORD.csv (every 15 min)
   └─> ERP imports data for invoicing/shipping

7. SHIPMENT: Next Day
   └─> Warehouse picks pallets based on orders
   └─> Trucks loaded and shipped
   └─> Delivery documents (DOC*.csv) imported
   └─> Inventory updated
```

---

# Inventory Receiving Process (INV)

## Business Purpose

**What**: Record goods received from suppliers into warehouse inventory

**Why**: 
- Track what inventory is available
- Validate goods match contracts
- Generate delivery confirmations for suppliers
- Enable inventory-based order fulfillment

## Process Flow - Step by Step

### Phase 1: File Import (Every 7 minutes)

**Trigger**: INV*.csv file appears in FTP folder

**File Contents Example**:
```csv
RecordID,SupplierCode,ItemCode,DeliveryNote,PalletNumber,BatchNumber,ExpiryDate,Quantity,PalletType,...
auto,SUP001,ITEM123,DN001,PAL12345,BATCH001,20251231,100,EURO,...
```

**Process**:
```python
# Step 1: System detects INV*.csv file
inv_file_import = PreNames("INV", 8, chemipal, source_folder, dest_folder)

# Step 2: Parse CSV and create staging records in Entity 8
new_inv_files_imported = inv_file_import.creating_body_to_update_with_new_id_INV_FITEM()

# Step 3: Enrich with item barcode from FITEM
if new_inv_files_imported:
    entity_param_2_entity_param(
        origin_entity_id=1,  # FITEM
        dest_entity_id=8,    # INV
        # Match by item code, copy barcode to inventory
    )
```

**Business Result**: Raw inventory data is imported into staging (Entity 8 directly)

---

### Phase 2: Transfer to Validation Staging (Entity 33 - INVFILE)

**Note**: While Phase 1 imports directly to Entity 8, there's a parallel validation process through Entity 33.

**Process**:
```python
# Check for new rows in staging
inv_functions = InvFunctions(chemipal)
inv_functions.check_for_new_inv_rows()  # Entity 33
```

**What Happens**:
- New records in Entity 33 get status: "Ready for Validation" (status = 1)

---

### Phase 3: Validation (Multi-Stage)

**Purpose**: Ensure inventory record is legitimate and can be processed

#### Validation Rule 1: Delivery Note Number
```python
# Business Rule: Reference number must exist and be unique
if reference_number is None or reference_number > 10 chars:
    status = "Invalid - No reference / too long"
    
if reference_number exists in Entity 8:
    status = "Invalid - Duplicate delivery note"
```

**Business Reason**: Prevents duplicate imports of same delivery

#### Validation Rule 2: Supplier Verification
```python
# Business Rule: Supplier must exist in master data
if supplier_code not in Entity 4 (SPK):
    status = "Invalid - Supplier code doesn't match"
```

**Business Reason**: Only registered suppliers can deliver goods

#### Validation Rule 3: Item Verification
```python
# Business Rule: Item must exist for this supplier
if (supplier_code, item_code) not in Entity 1 (FITEM):
    status = "Invalid - ChemiPal item code doesn't exist"
```

**Business Reason**: Can only receive items that are in the product catalog

#### Validation Rule 4: Pallet Type Match
```python
# Business Rule: Pallet type must match item definition
if pallet_type in file != pallet_type in FITEM:
    status = "Invalid - Pallet type doesn't match item"
```

**Business Reason**: Ensure physical goods match specifications

#### Validation Rule 5: Quantity Limits
```python
# Business Rule: Can't exceed max quantity per pallet
if quantity > max_quantity_in_FITEM:
    status = "Invalid - Quantity exceeds max per pallet"
```

**Business Reason**: Safety/physical limits on pallet capacity

#### Validation Rule 6: Batch/Expiry Requirements
```python
# Business Rule: Batch/expiry required if specified in item
if item requires batch and no batch provided:
    status = "Invalid - Batch/expiry not provided"
    
if item requires expiry and no expiry provided:
    status = "Invalid - Batch/expiry not provided"
```

**Business Reason**: Regulatory compliance for tracked products

#### Validation Rule 7: Active Contract
```python
# Business Rule: Must have valid contract for supplier+item+pallet
contract = find_in_Entity_7(supplier, item_type, pallet_size)

if not contract:
    status = "Invalid - No valid contract"
    
if contract.expiry_date < today:
    status = "Invalid - Contract expired"
```

**Business Reason**: Only accept goods under valid agreements

---

### Phase 4: Order Numbering

**Purpose**: Assign sequential line numbers to delivery

**Process**:
```python
# Group by: Supplier + Delivery Note + Date
# Assign row numbers: 1, 2, 3... within each group

inv_order_numbering = OrderNumbering(
    entity_num=33,
    numbering_param_id=461,  # Row number field
    order_num_param_id=460,  # Delivery note field
    sapak_name=458,          # Supplier field
    date_pickup=459,         # Date field
)
inv_order_numbering.start()
```

**Business Result**: 
```
Delivery DN001 from SUP001 on 2024-01-15:
  Row 1: Pallet PAL001
  Row 2: Pallet PAL002
  Row 3: Pallet PAL003
```

**Why**: Enables line-item tracking in delivery documents

---

### Phase 5: Transfer to Production (Entity 8 - INV)

**Trigger**: Record status = "Ready for transfer" (status = 5)

**Process**:
```python
new_inv_records = entity2entity(
    origin_entity_id=33,  # INVFILE (staging)
    dest_entity_id=8,     # INV (production)
    search_criteria=[{"paramId": 701, "operator": "EQ", "values": ["5"]}],
    param_ids_to_transfer=[458, 459, 460, 461, ...],  # All fields
    param_ids_to_receive=[62, 71, 72, 88, ...],       # Mapped fields
)
```

**Data Mapping Example**:
| Source (Entity 33) | Destination (Entity 8) | Field Name |
|-------------------|----------------------|------------|
| 458 | 62 | Supplier Code |
| 459 | 71 | Date |
| 460 | 72 | Delivery Note |
| 461 | 88 | Row Number |
| 462 | 64 | Quantity |

**Business Result**: Valid inventory is now in production database

---

### Phase 6: Data Enrichment

**Purpose**: Link inventory to related master data

```python
if new_inv_records:
    # 1. Link return inventory notes
    entity_param_2_entity_param(
        origin_entity_id=9,   # RINV (Return Inventory)
        dest_entity_id=8,     # INV
        # Copy pallet number from returns to inventory
    )
    
    # 2. Link delivery documents
    entity_param_2_entity_param_by_criteria(
        origin_entity_id=19,  # DOC (Delivery Documents)
        dest_entity_id=10,    # ORD (Orders)
        # Link document number to orders
    )
    
    # 3. Link document details to inventory
    entity_param_2_entity_param_by_criteria(
        origin_entity_id=19,  # DOC
        dest_entity_id=8,     # INV
        # Copy delivery date to inventory
        # Only for records with "ask order" flag
    )
    
    # 4. Set inventory status flag
    change_param_value_based_on_another_param_is_not_empty(
        entity_id=8,
        dest_param={"id": 628, "valueId": 3},  # Set status
        # When delivery date is populated
    )
    
    # 5. Link FITEM record ID
    entity_param_2_entity_param(
        origin_entity_id=1,   # FITEM
        dest_entity_id=8,     # INV
        # Copy FITEM ID based on matching item code
    )
    
    # 6. Link FITEM barcode
    entity_param_2_entity_param(
        origin_entity_id=1,   # FITEM
        dest_entity_id=8,     # INV
        # Copy barcode for scanning
    )
```

**Business Result**: Inventory record now has complete context and relationships

---

### Phase 7: Export to ERP (Hourly)

**Process**:
```python
# Every 1 hour
inv_file_export = INVORD(chemipal, 8)  # Entity 8 = INV
inv_file_export.start()
```

**What It Does**:
1. Query all inventory records created today
2. Generate INV.csv file with all columns
3. Save to export folder: `C:\FTP_Clients\chemipal\Out\INV.csv`
4. Save backup: `C:\FTP_Clients\chemipal\Out\backup\INV-YYYY-MM-DD-HH-MM.csv`

**File Usage**: 
- External ERP imports this file
- Used for invoicing suppliers
- Updates ERP inventory levels
- Triggers accounts payable

---

## Inventory Status Lifecycle

```
┌─────────────┐
│ File Import │ → Status: Empty/New
└──────┬──────┘
       ▼
┌─────────────┐
│ Initial Check│ → Status: 1 (Ready for Validation)
└──────┬──────┘
       ▼
┌─────────────┐
│  Validation │ → Status: 4 (Ready for Numbering) ✓
└──────┬──────┘   Status: 7 (Failed Validation) ✗
       ▼
┌─────────────┐
│  Numbering  │ → Status: 5 (Ready for Transfer)
└──────┬──────┘
       ▼
┌─────────────┐
│  Transfer   │ → Status: 6 (Transferred to Production)
└─────────────┘
```

---

# Item Definition Process (FITEM)

## Business Purpose

**What**: Define products that can be received and sold

**Why**:
- Create product catalog
- Link supplier items to ChemiPal item codes
- Define pallet specifications
- Set batch/expiry tracking requirements
- Specify warehouse locations

## Process Flow - Step by Step

### Phase 1: File Import (Every 7 minutes)

**File Contents Example**:
```csv
RecordID,SupplierCode,SupplierName,ItemCode,ItemName,PalletType,PalletSize,BatchReq,MaxQty,...
auto,SUP001,ABC Chemicals,ITEM123,Liquid Soap 5L,EURO,120x80,YES,100,...
```

**Process**:
```python
fitem_file_import = PreNames("FITEM", 1, chemipal, source_folder, dest_folder)
new_fitem_files_imported = fitem_file_import.creating_body_to_update_with_new_id_INV_FITEM()
```

---

### Phase 2: Data Enrichment (Immediately After Import)

**Purpose**: Link item to master data

```python
if new_fitem_files_imported:
    # 1. Link item barcode to inventory
    entity_param_2_entity_param(
        origin_entity_id=1,  # FITEM
        dest_entity_id=8,    # INV
        # Copy barcode for existing inventory
    )
    
    # 2. Link to item code master
    entity_param_2_entity_param(
        origin_entity_id=5,  # ITM (Item Codes)
        dest_entity_id=1,    # FITEM
        # Copy item description
    )
    
    # 3. Link to pallet type specifications (2 calls)
    entity_param_2_entity_param(
        origin_entity_id=6,  # Pallet Types
        dest_entity_id=1,    # FITEM
        # Copy pallet dimensions
    )
    
    # 4. Link to supplier master
    entity_param_2_entity_param(
        origin_entity_id=4,  # SPK (Suppliers)
        dest_entity_id=1,    # FITEM
        # Copy supplier name
    )
    
    # 5. Link to batch/lot definitions
    entity_param_2_entity_param(
        origin_entity_id=21,  # Batch/Lot master
        dest_entity_id=1,     # FITEM
        # Copy batch requirements
    )
    
    # 6-7. Link to warehouse locations
    entity_param_2_entity_param(
        origin_entity_id=35,  # Location Set 1
        dest_entity_id=1,     # FITEM
    )
    entity_param_2_entity_param(
        origin_entity_id=36,  # Location Set 2
        dest_entity_id=1,     # FITEM
    )
```

---

### Phase 3: Validation Staging (Entity 28 - FITEMCHECK)

**Purpose**: Validate new items before adding to catalog

**Process**:
```python
fitem_functions = FitemFunctions(chemipal)

# Step 1: Detect new items
fitem_functions.check_for_new_fitem_rows()
# Sets status = 1 (Ready for Validation)

# Step 2: Validate items
fitem_functions.validate_fitem_rows()
```

---

### Phase 4: Validation Rules

#### Validation 1: Mandatory Fields
```python
# Must have: supplier code, item code, pallet type, size
if any_field_missing:
    status = "Failed - Missing details"
```

#### Validation 2: Contract Exists
```python
# Must have contract for this supplier
if supplier not in Entity 7 (CTR):
    status = "Failed - No contract for this supplier"
```

#### Validation 3: Pallet Type & Size Valid
```python
# Pallet type + size combo must exist in contracts
if (pallet_type, pallet_size) not in Entity 7 for supplier:
    status = "Failed - Invalid pallet type or size"
```

#### Validation 4: No Duplicate Items
```python
# Item code must be unique
if item_code exists in Entity 1 (FITEM):
    status = "Failed - Already exists in FITEM"
```

#### Validation 5: No Duplicates in Same Batch
```python
# Can't have same item twice in one import
if item_code appears twice in Entity 28:
    status = "Failed - Duplicate in import batch"
```

**Passed Validation**: Status = 5 (Ready for Transfer)

---

### Phase 5: Transfer to Production (Entity 1 - FITEM)

**Process**:
```python
new_fitem_records = entity2entity(
    origin_entity_id=28,  # FITEMCHECK (staging)
    dest_entity_id=1,     # FITEM (production)
    search_criteria=[{"paramId": 702, "operator": "EQ", "values": ["5"]}],
    # Transfer all 23 fields
)
```

**Data Includes**:
- Item identification (codes, names)
- Supplier information
- Pallet specifications
- Batch/expiry requirements
- Quantity limits
- Warehouse locations

---

### Phase 6: Post-Transfer Enrichment

**Purpose**: Update related records with new item data

```python
if new_fitem_records:
    # Same enrichment as Phase 2
    # Updates existing inventory and orders with new item details
```

**Business Result**: New product is now available for inventory receiving and order fulfillment

---

## FITEM Status Lifecycle

```
┌─────────────┐
│ File Import │ → Direct to Entity 1 (FITEM)
└─────────────┘

       +
       
┌─────────────┐
│Manual Entry │ → Entity 28 (FITEMCHECK)
└──────┬──────┘
       ▼
┌─────────────┐
│ Detection   │ → Status: 1 (Ready for Validation)
└──────┬──────┘
       ▼
┌─────────────┐
│ Validation  │ → Status: 5 (Ready for Transfer) ✓
└──────┬──────┘   Status: 7 (Failed) ✗
       ▼
┌─────────────┐
│ Transfer    │ → Created in Entity 1 (FITEM)
└─────────────┘
```

---

# Order Fulfillment Process (ORD)

## Business Purpose

**What**: Process customer orders to ship products from inventory

**Why**:
- Fulfill customer requests
- Track what's being shipped
- Update inventory availability
- Generate picking lists for warehouse
- Create shipping documentation

## Process Flow - Step by Step

### Phase 1: Reference Number Assignment (Manual Step)

**Business Context**: Orders need a unique reference number (like a purchase order number) before processing.

**Process**:
1. New order file imported to Entity 34 (ORDFILE)
2. System detects order has **no reference number**
3. Status set to: "Waiting for Reference" (status = 6)

**Manual Intervention Required**:
```python
ord_functions.ord_temp_reference()

# What it does:
# 1. Groups orders by: Supplier + Date + Timestamp
# 2. Creates request in Entity 44 (TEMPORDDATES)
# 3. Status: "Waiting for Reference" (triggers notification)
# 4. User manually enters reference number in Entity 44
# 5. User changes status to "Reference Received" (status = 2)
```

**Example**:
```
Order Group ABC123 from Supplier SUP001 on 2024-01-15:
  - 3 pallets total
  - Waiting for PO number
  → User enters: PO-2024-001
  → System assigns PO-2024-001 to all 3 pallets
```

---

### Phase 2: Reference Transfer

**Trigger**: User set status = 2 in Entity 44

**Process**:
```python
ord_functions.check_for_new_reference()

# What it does:
# 1. Find completed references in Entity 44
# 2. Match back to orders in Entity 34 by Supplier+Date+Timestamp
# 3. Copy reference number to all matching orders
# 4. Set Entity 34 status = "Ready for Validation" (status = 3)
# 5. Set Entity 34 ChemiPal status = "New Request" (status = 1)
# 6. Set Entity 44 status = "Reference Transferred" (status = 3)
```

---

### Phase 3: Initial Order Check

**Process**:
```python
ord_functions.check_for_new_ord_rows()

# For orders without reference:
status = "Waiting for Reference" (status = 6)

# For orders with reference:
status = "Ready for Validation" (status = 3)
```

---

### Phase 4: Validation (Most Critical Phase)

#### Validation 1: Pallet Number Exists
```python
# Business Rule: Must specify which pallet to ship
if pallet_number is None:
    status = "Invalid - Missing pallet number"
```

**Business Reason**: Can't ship without knowing which physical pallet

#### Validation 2: No Duplicate Orders
```python
# Business Rule: Can't order same pallet twice
if (pallet_number, supplier) exists in Entity 10 (ORD):
    status = "Invalid - Order already exists for this pallet"
```

**Business Reason**: Prevents shipping same pallet multiple times

#### Validation 3: Pallet Not Already Shipped
```python
# Business Rule: Pallet can't be in transit or delivered
if pallet_number in Entity 19 (DOC - Delivery Documents):
    status = "Invalid - Pallet already left ChemiPal (delivery note exists)"
```

**Business Reason**: Can't ship inventory that's already gone

#### Validation 4: Pallet Exists in Inventory
```python
# Business Rule: Must have pallet in warehouse
if (pallet_number, supplier) not in Entity 8 (INV):
    status = "Invalid - Pallet doesn't exist in inventory"
```

**Business Reason**: Can only ship what we have

#### Validation 5: Reference Number Length
```python
# Business Rule: Reference max 10 characters
if len(reference_number) > 10:
    status = "Invalid - Reference too long (>10 chars)"
```

**Business Reason**: System limitation / printing limitation

#### Validation 6: Unique Reference
```python
# Business Rule: Reference must be unique per supplier
if (reference_number, supplier) exists in Entity 10 (ORD):
    status = "Invalid - Reference number already used"
```

**Business Reason**: Prevents duplicate invoicing

**Passed All Validations**: 
- Status = "Request Sent to ChemiPal" (ChemiPal status = 2)
- Program Status = "Passed Validation, Waiting for INV Update" (status = 9)

---

### Phase 5: Update Inventory "Ask Ord" Flag

**Purpose**: Mark inventory pallets that have orders against them

**Process**:
```python
ord_functions.update_ask_ord_in_inv()

# What it does:
# 1. Find orders with status = 9 (validated, waiting for INV update)
# 2. Find matching pallets in Entity 8 (INV)
# 3. Set INV param 528 (askord) = 1
# 4. Set Order status = "Ready for Numbering" (status = 4)
```

**Business Purpose**:
- Flags inventory as "reserved" for order
- Prevents same pallet being ordered twice
- Links inventory to outbound order

**Database State**:
```
Before:
  INV Pallet PAL001: askord = empty
  
After:
  INV Pallet PAL001: askord = 1 (has order)
```

---

### Phase 6: Order Numbering

**Purpose**: Assign line numbers for multi-pallet orders

**Process**:
```python
ord_order_numbering = OrderNumbering(
    entity_num=34,
    numbering_param_id=474,  # Row number
    order_num_param_id=472,  # Reference
    sapak_name=471,          # Supplier
    date_pickup=473,         # Pickup date
    status_param_id=691,
    status_value_id=5,       # Ready for transfer
    searchCriteria=[{"paramId": 477, "operator": "EQ", "values": ["2"]}]  # ChemiPal status = 2
)
ord_order_numbering.start()
```

**Business Result**:
```
Order PO-2024-001 from SUP001:
  Row 1: Pallet PAL001
  Row 2: Pallet PAL002
  Row 3: Pallet PAL003
```

**Status After**: 5 (Ready for Transfer)

---

### Phase 7: Transfer to Production (Entity 10 - ORD)

**Process**:
```python
new_ord_records = entity2entity(
    origin_entity_id=34,  # ORDFILE (staging)
    dest_entity_id=10,    # ORD (production)
    search_criteria=[{"paramId": 691, "operator": "EQ", "values": ["5"]}],
    # Transfer all order fields
)
```

**Data Mapping**:
| Field | Description |
|-------|-------------|
| Supplier code | Who ordered |
| Reference | PO number |
| Pickup date | When to ship |
| Row number | Line item |
| Quantity | Amount to ship |
| Pallet number | Which pallet |
| ChemiPal status | Order stage |

---

### Phase 8: Order Enrichment

**Purpose**: Link order to delivery documents and inventory details

```python
if new_ord_records:
    # 1. Link delivery document date
    entity_param_2_entity_param(
        origin_entity_id=19,  # DOC
        dest_entity_id=10,    # ORD
        # Copy delivery date
    )
    
    # 2. Link additional delivery details
    entity_param_2_entity_param(
        origin_entity_id=19,  # DOC
        dest_entity_id=10,    # ORD
        # Copy delivery note number
    )
    
    # 3. Link inventory FITEM ID
    entity_param_2_entity_param(
        origin_entity_id=8,   # INV
        dest_entity_id=10,    # ORD
        # Copy FITEM record ID
    )
    
    # 4. Link FITEM barcode
    entity_param_2_entity_param(
        origin_entity_id=1,   # FITEM
        dest_entity_id=10,    # ORD
        # Copy product barcode
    )
    
    # 5. Link FITEM item code
    entity_param_2_entity_param(
        origin_entity_id=1,   # FITEM
        dest_entity_id=10,    # ORD
        # Copy ChemiPal item code
    )
    
    # 6. Link warehouse location
    entity_param_2_entity_param(
        origin_entity_id=1,   # FITEM
        dest_entity_id=10,    # ORD
        # Copy warehouse location for picking
    )
```

**Business Result**: Order now has complete picking information

---

### Phase 9: Export to ERP (Every 15 minutes)

**Process**:
```python
# fifteen_min() thread
ord_file_export = INVORD(chemipal, 10)  # Entity 10 = ORD
ord_file_export.start()
```

**What It Generates**:
- ORD.csv file with all orders created today
- Includes: supplier, reference, pallet, quantity, location
- Used by warehouse for picking
- Used by ERP for shipping documentation

---

## Order Status Lifecycle

```
┌──────────────┐
│ File Import  │ → Entity 34 (ORDFILE)
└──────┬───────┘
       ▼
┌──────────────┐
│ Check Ref    │ → Has Ref? → Status 3 (Ready for Validation)
└──────┬───────┘   No Ref?  → Status 6 (Waiting for Reference)
       │                            ▼
       │                     ┌──────────────┐
       │                     │ Manual Entry │ → Entity 44
       │                     │ Reference    │
       │                     └──────┬───────┘
       │                            ▼
       │                     ┌──────────────┐
       │                     │ Transfer Ref │ → Status 3
       │                     └──────┬───────┘
       │◄────────────────────────────┘
       ▼
┌──────────────┐
│  Validation  │ → Pass → Status 9 (Waiting for INV Update)
└──────┬───────┘   Fail → Status 7 (Failed)
       ▼
┌──────────────┐
│ Update INV   │ → Status 4 (Ready for Numbering)
│ "askord" flag│
└──────┬───────┘
       ▼
┌──────────────┐
│  Numbering   │ → Status 5 (Ready for Transfer)
└──────┬───────┘
       ▼
┌──────────────┐
│  Transfer    │ → Created in Entity 10 (ORD)
│ to Production│
└──────────────┘
```

---

# Supporting Processes

## 1. Supplier Master (SPK) - Every 30 Minutes

**File**: SPK*.csv

**Process**:
```python
# thirty_min() thread
spk_file_import = PreNames("SPK", 4, chemipal, source, dest)
new_spk_files_imported = spk_file_import.creating_body_to_update()

if new_spk_files_imported:
    # Link supplier name to items
    entity_param_2_entity_param(
        origin_entity_id=4,  # SPK
        dest_entity_id=1,    # FITEM
        # Update supplier name on items
    )
```

**Business Impact**: Updates supplier information across system

---

## 2. Item Codes (ITM) - Every 30 Minutes

**File**: ITM*.csv

**Process**:
```python
itm_file_import = PreNames("ITM", 5, chemipal, source, dest)
new_itm_files_imported = itm_file_import.creating_body_to_update()

if new_itm_files_imported:
    # Link item descriptions to products
    entity_param_2_entity_param(
        origin_entity_id=5,  # ITM
        dest_entity_id=1,    # FITEM
        # Update item descriptions
    )
```

**Business Impact**: Updates product descriptions

---

## 3. Contracts (CTR) - Every 30 Minutes

**File**: CTR*.csv

**Process**:
```python
ctr_file_import = PreNames("CTR", 7, chemipal, source, dest)
ctr_file_import.creating_body_to_update()

# Also updates contract balances
ctr_file_import.updateYetraCtr()  # Calculate remaining balances
```

**Business Impact**: 
- Defines what can be received
- Tracks contract utilization
- Validates inventory against agreements

---

## 4. Delivery Documents (DOC) - Every 15 Minutes

**File**: DOC*.csv

**Purpose**: Record actual shipments/deliveries

**Process**:
```python
# fifteen_min() thread
doc_file_import = PreNames("DOC", 19, chemipal, source, dest)
new_doc_files_imported = doc_file_import.creating_body_to_update_with_new_id()

if new_doc_files_imported:
    # Link delivery dates to orders
    entity_param_2_entity_param(origin=19, dest=10)
    
    # Link delivery dates to inventory
    entity_param_2_entity_param_by_criteria(origin=19, dest=8)
    
    # Set inventory shipped status
    change_param_value_based_on_another_param_is_not_empty(entity=8)
```

**Business Impact**: 
- Marks orders as shipped
- Updates inventory status
- Prevents re-shipping same pallet

---

## 5. Return Inventory (RINV) - Every 15 Minutes

**File**: RINV*.csv

**Purpose**: Record goods returned to warehouse

**Process**:
```python
rinv_file_import = PreNames("RINV", 9, chemipal, source, dest)
new_rinv_files_imported = rinv_file_import.creating_body_to_update()

if new_rinv_files_imported:
    # Link return pallet numbers to inventory
    entity_param_2_entity_param(origin=9, dest=8)
```

**Business Impact**: Updates inventory with returned goods

---

# Business Rules & Validations

## Master Data Rules

### Rule: Contract-Based Receiving
**Requirement**: Can only receive items with valid contracts

**Validation**:
```
IF receiving item THEN
  Contract must exist WHERE:
    - Supplier matches
    - Pallet type matches
    - Pallet size matches
    - Contract not expired
```

**Business Reason**: Legal/commercial agreements required

---

### Rule: Item Catalog Compliance
**Requirement**: All received items must be in FITEM

**Validation**:
```
IF receiving pallet THEN
  FITEM must exist WHERE:
    - Supplier code matches
    - Item code matches
    - Pallet type matches
```

**Business Reason**: Only handle known products

---

## Inventory Rules

### Rule: Unique Delivery Notes
**Requirement**: No duplicate imports

**Validation**:
```
IF importing inventory THEN
  Delivery note must NOT exist in INV
```

**Business Reason**: Prevent double-counting same delivery

---

### Rule: Quantity Limits
**Requirement**: Safety limits on pallet capacity

**Validation**:
```
IF receiving pallet THEN
  Quantity <= Max Quantity in FITEM
```

**Business Reason**: Physical/safety constraints

---

### Rule: Batch Tracking
**Requirement**: Regulated products need batch/expiry

**Validation**:
```
IF item requires batch tracking THEN
  Batch number must be provided
  Expiry date must be provided (if required)
```

**Business Reason**: Regulatory compliance, traceability

---

## Order Rules

### Rule: Inventory Availability
**Requirement**: Can't ship what you don't have

**Validation**:
```
IF creating order THEN
  Pallet must exist in INV WHERE:
    - Pallet number matches
    - Supplier matches
    - Not already shipped
```

**Business Reason**: Physical constraint

---

### Rule: No Double Shipping
**Requirement**: Pallet shipped only once

**Validation**:
```
IF creating order THEN
  Pallet must NOT exist in:
    - ORD (already ordered)
    - DOC (already shipped)
```

**Business Reason**: Prevent inventory errors

---

### Rule: Reference Uniqueness
**Requirement**: Unique reference per supplier

**Validation**:
```
IF creating order THEN
  (Reference, Supplier) must be unique in ORD
```

**Business Reason**: Prevent duplicate invoicing

---

# Integration Points

## Inbound Integrations (File Import)

| System | Files | Frequency | Purpose |
|--------|-------|-----------|---------|
| **ERP** | INV*.csv | On-demand | Incoming goods |
| **ERP** | FITEM*.csv | On-demand | New products |
| **ERP** | ORD*.csv | On-demand | Customer orders |
| **ERP** | SPK*.csv | Daily | Supplier updates |
| **ERP** | ITM*.csv | Daily | Item code updates |
| **ERP** | CTR*.csv | Daily | Contract updates |
| **ERP** | DOC*.csv | Real-time | Delivery confirmations |
| **ERP** | RINV*.csv | As needed | Returns |

## Outbound Integrations (File Export)

| File | Frequency | Destination | Purpose |
|------|-----------|-------------|---------|
| INV.csv | Hourly | ERP | Invoice suppliers |
| ORD.csv | Every 15 min | ERP/WMS | Pick lists |

## Data Flow Summary

```
External ERP/Systems
        │
        │ CSV Files (Import)
        ▼
┌─────────────────┐
│  FTP Folder     │
│  (In)           │
└────────┬────────┘
         │
         │ ChemiPal Reads
         ▼
┌─────────────────┐
│  ChemiPal       │
│  (Validation &  │
│   Processing)   │
└────────┬────────┘
         │
         │ CSV Files (Export)
         ▼
┌─────────────────┐
│  FTP Folder     │
│  (Out)          │
└────────┬────────┘
         │
         ▼
External ERP/Systems
```

---

# Exception Handling

## Business Exception Scenarios

### Scenario 1: Invalid Supplier Code

**Trigger**: Inventory file with unknown supplier

**System Response**:
```
Status = "Invalid - Supplier code doesn't match"
Program Status = 7 (Closed - Failed Validation)
```

**Business Action Required**:
1. Verify supplier code in file
2. Add supplier to SPK master if legitimate
3. Re-import file

---

### Scenario 2: Expired Contract

**Trigger**: Receiving goods after contract expired

**System Response**:
```
Status = "Invalid - No valid contract"
Program Status = 7 (Closed - Failed Validation)
```

**Business Action Required**:
1. Renew contract in CTR master
2. Update contract dates
3. Re-import inventory file

---

### Scenario 3: Out of Stock Order

**Trigger**: Order for pallet not in inventory

**System Response**:
```
Status = "Invalid - Pallet doesn't exist in inventory"
Program Status = 7 (Closed - Failed Validation)
```

**Business Action Required**:
1. Verify pallet number
2. Check if pallet already shipped
3. If error: correct order file
4. If stock issue: wait for goods to arrive

---

### Scenario 4: Duplicate Delivery Note

**Trigger**: Same delivery imported twice

**System Response**:
```
Status = "Invalid - Delivery note already exists"
Program Status = 7 (Closed - Failed Validation)
```

**Business Action Required**:
1. Verify if truly duplicate
2. If legitimate: use different delivery note number
3. If error: ignore, goods already in system

---

### Scenario 5: Pallet Already Shipped

**Trigger**: Order for pallet that was delivered

**System Response**:
```
Status = "Invalid - Pallet already left ChemiPal"
Program Status = 7 (Closed - Failed Validation)
```

**Business Action Required**:
1. Verify pallet hasn't actually shipped
2. If shipped: cannot fulfill order
3. If error in delivery doc: correct DOC record

---

## Error Resolution Workflow

```
┌─────────────────┐
│ Validation Fails│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Status = 7      │
│ (Failed)        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Review Log      │
│ Error Message   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Fix Root Cause: │
│ • Master Data   │
│ • File Error    │
│ • Business Rule │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Re-import File  │
│ or              │
│ Manual Override │
└─────────────────┘
```

---

# Summary

## ChemiPal in One Page

**What ChemiPal Does**:
- Manages warehouse inventory from multiple suppliers
- Validates all transactions against contracts and business rules
- Processes customer orders against available inventory
- Integrates with external ERP via CSV file exchange
- Provides full traceability with batch/lot tracking

**Key Business Processes**:
1. **Inventory Receiving**: Suppliers → Delivery → Validate → Record in INV
2. **Product Catalog**: Define items → Link to suppliers → Set specifications
3. **Order Fulfillment**: Customer order → Validate availability → Reserve inventory → Ship

**Critical Success Factors**:
- **Valid Contracts**: Can't receive without contract
- **Master Data**: Items, suppliers, pallets must be defined
- **Unique References**: Prevent duplicate processing
- **Inventory Accuracy**: Can only ship what exists

**System Cadence**:
- **Every 7 minutes**: Main process (INV, FITEM, ORD)
- **Every 15 minutes**: Documents and exports
- **Every 30 minutes**: Master data updates
- **Every hour**: Inventory export to ERP

**Value Delivered**:
- Automated validation prevents errors
- Real-time inventory visibility
- Contract compliance enforcement
- Audit trail for all transactions
- Integration with existing systems

---

**Document Version**: 1.0  
**Last Updated**: 2024-10-22  
**Business Domain**: Warehouse Management / Logistics  
**System**: ChemiPal Integration Platform






