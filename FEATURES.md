# ArogyaPath Features

## 🎯 Core Lab Operations

### Lab Order Management
- Create lab orders with multiple tests
- Track order status (Draft, Submitted, Completed, Cancelled)
- Link orders to patients and referring doctors
- Support for bulk test ordering
- Automatic sample type assignment

### Sample Collection
- Track sample collection centers
- Record sample collection details
- Link samples to lab orders
- Sample tube management with barcode support
- Collection status tracking

### Lab Testing
- **200+ Predefined Tests** organized by department
- Test master with:
  - HSN/SAC code (999316 for pathology)
  - GST exemption flags
  - Reference ranges by age and gender
  - Calculated parameters support
  - Critical value thresholds
- Test panels for grouped testing
- Department-wise test organization

### Lab Results
- Advanced result entry interface
- Support for:
  - Numeric results with units
  - Text/descriptive results
  - Boolean results
  - Ratio results
  - Calculated parameters
- Automatic reference range validation
- Critical value flagging
- Amendment support with audit trail
- Pathologist approval workflow

### Lab Reports
- Professional report generation
- Features:
  - Department-wise grouping
  - Critical value highlighting
  - Reference ranges display
  - Pathologist signatures
  - QR code generation
  - Custom report templates
  - Header configuration per lab

### Quality Control
- QC Material tracking
- QC Result recording
- Westgard Rule configuration
- QC validation before report generation
- Analyzer-specific QC tracking

---

## 💰 Financial Management

### Lab Invoice
- GST-compliant invoicing
- Features:
  - Automatic tax calculations (CGST/SGST/IGST)
  - Tax template selection based on location
  - Item-level tax breakdown
  - Professional invoice format
  - Tax invoice vs Bill of Supply determination
  - Outstanding amount tracking
  - Payment status management

### Payment Entry
- Integrated payment processing
- Features:
  - Payment Entry creation from Lab Invoice
  - Payment Request support for online payments
  - Multiple payment mode support
  - Bank account integration
  - Currency handling
  - Reconciliation support

### Doctor Commission
- Automatic commission calculation
- Features:
  - Commission percentage configuration
  - Referred doctor tracking
  - Commission settlement
  - Commission log with audit trail
  - Batch commission processing

### Corporate Accounts
- Special pricing for corporate clients
- Features:
  - Corporate account master
  - Rate card management
  - Discount application
  - Corporate-specific billing
  - Volume-based pricing

### Discount Schemes
- Flexible discount management
- Features:
  - Percentage-based discounts
  - Fixed amount discounts
  - Test-specific discounts
  - Corporate discounts
  - Seasonal promotions

---

## 📊 Inventory & Equipment

### Reagent Management
- Reagent master with:
  - Lot tracking
  - Expiry date management
  - Quantity tracking
  - Supplier information
  - Cost tracking
- Reagent consumption entry
- Automatic expiry alerts
- Stock ledger integration

### Equipment Management
- Analyzer tracking
- Features:
  - Equipment master
  - Calibration logging (NABL-compliant)
  - Calibration due date tracking
  - Calibration history
  - Equipment status (Active/Inactive)
  - Maintenance scheduling

### Stock Ledger
- Real-time inventory tracking
- Features:
  - Multi-location support
  - Transaction categorization
  - Opening/closing balances
  - Stock movement reports
  - Inventory aging analysis

---

## 🇮🇳 GST Compliance (India)

### Tax Calculations
- Automatic CGST/SGST/IGST calculation
- Features:
  - Intra-state transactions (CGST + SGST)
  - Inter-state transactions (IGST)
  - Tax-exempt items support
  - Proportional discount handling
  - Per-item exemption checks

### Tax Templates
- Pre-configured tax templates for:
  - 18% GST (standard rate)
  - 5% GST (reduced rate)
  - 0% GST (exempted)
  - Reverse charge applicable items

### Place of Supply
- Automatic determination based on:
  - Customer location
  - Billing address state
  - GSTIN state code
- All 28 Indian states + UTs supported

### GSTIN Validation
- Built-in GSTIN validation
- Features:
  - Format validation
  - State code extraction
  - Duplicate GSTIN prevention
  - Registered/Unregistered category detection

### Tax Invoices
- Professional tax invoice format
- Features:
  - Tax invoice for registered customers
  - Bill of Supply for unregistered customers
  - Tax breakdown display
  - Place of supply indication
  - GSTIN display

---

## 🔔 Notifications & Alerts

### TAT Alerts
- Turn-around-time breach notifications
- Features:
  - Configurable TAT thresholds
  - Automatic alerts on breach
  - Email and WhatsApp notifications
  - Escalation support

### Expiry Alerts
- Reagent expiry notifications
- Equipment calibration due alerts
- Features:
  - Configurable alert window (e.g., 7 days before)
  - Overdue tracking
  - Batch notifications

### Critical Results
- Automatic critical value alerts
- Features:
  - Critical value thresholds per test
  - Pathologist notification
  - Patient notification (optional)
  - Alert history tracking

### WhatsApp Integration
- Send notifications via WhatsApp
- Features:
  - Template-based messages
  - Patient contact integration
  - Delivery tracking
  - Bulk messaging support

---

## 👥 User Management

### Role-Based Access Control
- **Lab Admin** — Full system access
- **Lab Manager** — Lab operations and reporting
- **Lab Pathologist** — Result approval and report generation
- **Lab Technician** — Sample collection and result entry
- **Lab Receptionist** — Patient registration and order creation

### Department Segregation
- Organize tests by department:
  - Clinical Pathology
  - Biochemistry
  - Microbiology
  - Immunology
  - Hematology
  - Serology

### Workflow Approvals
- Pathologist approval for results
- Features:
  - Multi-level approval
  - Approval comments
  - Rejection with feedback
  - Audit trail

---

## 📱 Additional Features

### Patient Management
- Patient master with:
  - Contact information
  - Medical history
  - Insurance details
  - Emergency contacts
  - Address management

### Doctor Management
- Referring doctor tracking
- Features:
  - Doctor master
  - Specialization
  - Commission configuration
  - Performance tracking

### Lab Settings
- Configurable defaults:
  - Default TAT values
  - Critical value thresholds
  - Default sample types
  - Report header configuration
  - Notification settings

### Reporting
- Built-in reports:
  - Lab order summary
  - Result completion status
  - Invoice aging
  - Doctor performance
  - Reagent consumption
  - Equipment maintenance

---

## 🔗 Integration Points

### ERPNext Integration
- Uses ERPNext's:
  - Company structure
  - Chart of Accounts
  - Payment Entry system
  - Address management
  - Contact management

### Payments App Integration
- Razorpay payment gateway support
- Payment Request creation
- Online payment processing

### Custom Field Integration
- GST custom fields (via India Compliance pattern)
- GSTIN validation
- Tax category mapping
- Place of supply options

