# ArogyaPath Architecture

## System Overview

ArogyaPath is a modular pathology lab management system built on Frappe Framework v15. It follows a layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                    Frappe Desk (UI)                     │
│              (Vue.js based Form Interface)              │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              Frappe Framework (Backend)                  │
│  ├─ DocType Controllers                                 │
│  ├─ Custom Scripts (JS/Python)                          │
│  ├─ Hooks & Event Handlers                              │
│  └─ REST API Layer                                      │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│            ArogyaPath Application Layer                  │
│  ├─ Controllers (Cross-cutting concerns)                │
│  ├─ Utils (GST, GSTIN validation, calculations)         │
│  ├─ Seed Data (Tests, tax templates, COA)               │
│  └─ Custom Fields Setup                                 │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              Database Layer (MariaDB)                    │
│  ├─ DocType Tables (60+ tables)                         │
│  ├─ Child Tables (Tax rows, items, etc.)                │
│  └─ Indexes & Relationships                             │
└─────────────────────────────────────────────────────────┘
```

## Module Structure

```
arogyapath/
├── arogyapath/
│   ├── controllers/           # Cross-cutting hooks
│   │   ├── lab_invoice.py    # Lab Invoice validation & GST
│   │   └── ...
│   │
│   ├── doctype/              # 60+ DocTypes
│   │   ├── lab_invoice/
│   │   ├── lab_result/
│   │   ├── patient/
│   │   ├── pathology_lab/
│   │   ├── lab_tax_category/
│   │   └── ... (57 more)
│   │
│   ├── utils/                # Utility functions
│   │   ├── gst.py           # GST calculations
│   │   ├── custom_fields.py # Custom field setup
│   │   └── ...
│   │
│   ├── print_format/         # Report templates
│   │   ├── lab_invoice_gst.html
│   │   └── lab_report_standard.html
│   │
│   ├── workspace/            # Module navigation
│   │   ├── arogyapath.json
│   │   └── ... (6 more)
│   │
│   ├── install.py            # Installation hooks
│   ├── tasks.py              # Scheduled jobs
│   ├── seed_*.py             # Data seeding
│   └── hooks.py              # App configuration
│
└── public/
    └── js/
        └── address.js        # Custom Address scripts
```

## DocType Relationships

### Core Lab Workflow

```
Patient
  ↓
Patient Visit
  ↓
Lab Order ──→ Lab Order Item ──→ Lab Test Master
  ↓
Sample Collection ──→ Sample Type
  ↓
Lab Result ──→ Lab Result Item ──→ Test Parameter
  ↓
Lab Report ──→ Lab Report Template
  ↓
Lab Invoice ──→ Lab Invoice Item ──→ Lab Tax Row
```

### Financial Workflow

```
Lab Invoice
  ├─→ Lab Invoice Item
  ├─→ Lab Tax Row
  ├─→ Doctor Commission Log ──→ Commission Log Item
  └─→ Payment Entry ──→ Payment Entry Reference
         ↓
    Payment Entry Deduction
```

### Configuration Hierarchy

```
Pathology Lab
  ├─→ Lab Branch
  ├─→ Lab Settings
  ├─→ Lab Department
  ├─→ Lab Tax Category
  └─→ Lab Tax Template ──→ Lab Tax Row (template)

Lab Test Master
  ├─→ Test Parameter ──→ Reference Range
  └─→ Lab Test Panel ──→ Panel Item
```

### Inventory & Equipment

```
Reagent
  ├─→ Reagent Lot
  └─→ Reagent Consumption Entry ──→ Consumption Entry Item

Analyzer
  └─→ Equipment Calibration Log

QC Material
  └─→ QC Result ──→ QC Result Item
```

## Data Flow

### Lab Testing Workflow

```
1. Lab Order Creation
   └─→ Validate patient & tests
   └─→ Set default sample types
   └─→ Calculate estimated TAT

2. Sample Collection
   └─→ Record collection details
   └─→ Generate sample barcodes
   └─→ Update order status

3. Result Entry
   └─→ Validate reference ranges
   └─→ Flag critical values
   └─→ Calculate derived parameters
   └─→ QC validation

4. Pathologist Review
   └─→ Approve/reject results
   └─→ Add comments
   └─→ Sign report

5. Report Generation
   └─→ Format results
   └─→ Add pathologist signature
   └─→ Generate QR code
   └─→ Create PDF

6. Invoicing
   └─→ Calculate GST
   └─→ Apply discounts
   └─→ Calculate doctor commission
   └─→ Create invoice

7. Payment Processing
   └─→ Create payment entry
   └─→ Optional: Payment request
   └─→ Reconcile payment
   └─→ Update invoice status
```

### GST Calculation Flow

```
Lab Invoice Submission
  ↓
validate() hook triggered
  ↓
_compute_gst() called
  ↓
gst.compute_invoice_taxes()
  ├─ Determine is_inter_state
  ├─ Select tax template
  ├─ Calculate per-item taxes
  │  ├─ Apply exemptions
  │  ├─ Apply discounts
  │  └─ Set CGST/SGST/IGST amounts
  ├─ Aggregate tax totals
  └─ Update invoice totals
  ↓
Invoice submitted
  ↓
on_submit() hook triggered
  ↓
set_status() called
  └─ Update payment status (Paid/Unpaid/Partly Paid)
```

## Key Components

### 1. Controllers (`controllers/`)

**Purpose:** Cross-cutting concerns that augment DocType behavior

**lab_invoice.py:**
- `validate()` — Validate GSTIN, set item amounts, apply discounts, compute GST
- `get_patient_gst_details()` — Fetch addresses, GSTIN, contact details
- `get_tax_template_for_patient()` — Select tax template based on location

### 2. Utils (`utils/`)

**gst.py:**
- `INDIA_STATE_CODES` — Mapping of state names to GST codes
- `validate_gstin()` — Validate GSTIN format and extract state
- `is_interstate()` — Determine if transaction is inter-state
- `get_tax_rates()` — Get applicable tax rates
- `compute_invoice_taxes()` — Calculate item-level and invoice-level taxes
- `compute_doctor_commission()` — Calculate referring doctor commission
- `flt()` — Float conversion with precision

**custom_fields.py:**
- `setup_custom_fields()` — Add GST custom fields to DocTypes

### 3. Seed Data (`seed_*.py`)

**seed_catalog.py:**
- Seeds 200+ lab tests
- Seeds test panels
- Seeds departments
- Seeds sample types

**seed_tax_templates.py:**
- Seeds tax categories (In State GST, Out of State GST)
- Seeds tax templates (18%, 5%, 0% GST)
- Seeds tax withholding categories

**seed_chart_of_accounts.py:**
- Seeds chart of accounts for pathology lab
- Creates tax accounts (CGST, SGST, IGST)
- Creates revenue accounts

**seed_panels.py:**
- Seeds test panels (grouped tests)

### 4. Scheduled Tasks (`tasks.py`)

```python
send_tat_alerts()           # Daily - Alert on TAT breach
flag_expiring_reagents()    # Daily - Alert on reagent expiry
flag_expiring_amc()         # Daily - Alert on AMC expiry
check_critical_tat_breach() # Hourly - Check critical TAT
flag_expiring_calibrations()# Daily - Alert on calibration due
```

### 5. Print Formats

**lab_invoice_gst.html:**
- Jinja2 template for tax invoices
- Displays tax breakdown
- Shows GSTIN and place of supply
- Professional formatting

**lab_report_standard.html:**
- Jinja2 template for lab reports
- Department-wise grouping
- Critical value highlighting
- Pathologist signature section
- QR code generation

## Integration Points

### With ERPNext

- **Company** — Lab's company entity
- **Chart of Accounts** — Financial accounts
- **Account** — GL accounts for invoicing
- **Payment Entry** — Payment processing
- **Address** — Customer/company addresses
- **Contact** — Contact person details

### With Payments App

- **Payment Request** — Online payment requests
- **Razorpay Settings** — Payment gateway configuration
- **Integration Request** — Payment transaction tracking

### Custom Integrations

- **WhatsApp** — Notification delivery
- **QR Code Generation** — Report identification
- **PDF Generation** — Report export

## Database Schema

### Key Tables

**lab_invoice:**
- name (PK)
- patient (FK → Patient)
- pathology_lab (FK → Pathology Lab)
- invoice_date
- gross_amount, total_tax, grand_total
- outstanding_amount
- status, payment_status
- tax_category, taxes_and_charges
- billing_address_gstin, company_gstin
- gst_category, place_of_supply
- contact_person, company_contact_person

**lab_invoice_item:**
- name (PK)
- parent (FK → Lab Invoice)
- test (FK → Lab Test Master)
- rate, amount
- cgst_rate, sgst_rate, igst_rate
- cgst_amount, sgst_amount, igst_amount
- tax_amount

**lab_result:**
- name (PK)
- lab_order (FK → Lab Order)
- patient (FK → Patient)
- status (Draft/Submitted/Approved/Rejected)
- is_amended, amendment_reason

**lab_result_item:**
- name (PK)
- parent (FK → Lab Result)
- test_parameter (FK → Test Parameter)
- result_value, result_type
- reference_range, is_critical

### Indexes

- `lab_invoice.patient` — Fast patient lookup
- `lab_invoice.pathology_lab` — Fast lab lookup
- `lab_result.lab_order` — Fast order lookup
- `lab_result.status` — Fast status filtering
- `reagent_lot.expiry_date` — Fast expiry lookup

## Security & Permissions

### Role-Based Access

- **Lab Admin** — All permissions
- **Lab Manager** — Lab operations, reporting
- **Lab Pathologist** — Result approval, report generation
- **Lab Technician** — Sample collection, result entry
- **Lab Receptionist** — Patient registration, order creation

### Document Permissions

- Lab Invoice — Visible to Lab Manager, Lab Admin
- Lab Result — Visible to Lab Pathologist, Lab Manager
- Lab Report — Visible to all roles (read-only for non-pathologist)

### Field-Level Security

- GSTIN fields — Visible to Lab Admin only
- Commission fields — Visible to Lab Manager only
- Critical values — Visible to Lab Pathologist only

## Performance Considerations

### Query Optimization

- Indexes on frequently filtered fields
- Cached queries for static data (tests, departments)
- Lazy loading of child tables

### Caching Strategy

- Lab Test Master — Cached (rarely changes)
- Tax Templates — Cached (rarely changes)
- Reference Ranges — Cached (rarely changes)
- Patient data — Not cached (frequently updated)

### Batch Operations

- Bulk test seeding on installation
- Batch invoice generation
- Batch payment processing

## Scalability

### Current Capacity

- Supports 10,000+ patients
- Handles 1,000+ daily lab orders
- Manages 200+ tests and panels
- Processes 100+ invoices daily

### Future Scaling

- Database partitioning by date
- Read replicas for reporting
- Caching layer (Redis)
- Async task processing (Celery)

## Error Handling

### Validation Errors

- GSTIN format validation
- Tax template selection validation
- Outstanding amount validation
- Reference range validation

### Business Logic Errors

- Duplicate invoice prevention
- Concurrent result entry handling
- Payment reconciliation errors
- TAT breach notifications

### System Errors

- Database connection failures
- File generation failures
- Email/WhatsApp delivery failures
- Payment gateway timeouts

