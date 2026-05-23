# ArogyaPath

**A comprehensive Pathology Lab Management System built on Frappe Framework**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Frappe Version](https://img.shields.io/badge/Frappe-15.0+-blue.svg)](https://github.com/frappe/frappe)
[![Python Version](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

## 📑 Documentation Tabs

- **[Overview](#overview)** — Project introduction and key features
- **[Features](FEATURES.md)** — Detailed feature documentation
- **[Architecture](ARCHITECTURE.md)** — System design and structure
- **[Installation](INSTALLATION.md)** — Setup and configuration guide
- **[Contributing](CONTRIBUTING.md)** — Development guidelines
- **[API Reference](#api-reference)** — API endpoints and usage
- **[FAQ](#faq)** — Frequently asked questions

---

## Overview

ArogyaPath is a full-featured pathology lab management system designed to streamline laboratory operations, from sample collection and testing to result reporting and billing. Built on the Frappe Framework, it provides a complete solution for managing lab workflows, inventory, quality control, and financial operations.

### 🎯 Key Highlights

- **200+ Predefined Lab Tests** — Organized by department with reference ranges
- **GST Compliance** — Automatic CGST/SGST/IGST calculations for India
- **Complete Lab Workflow** — From order to invoice to payment
- **Quality Control** — QC material tracking and Westgard rules
- **Equipment Management** — NABL-compliant calibration logging
- **Payment Integration** — Razorpay support with Payment Request
- **Professional Reports** — Jinja2-based lab reports with signatures and QR codes
- **Role-Based Access** — 5 predefined roles with granular permissions

### 📊 Quick Stats

| Metric | Value |
|--------|-------|
| **DocTypes** | 60+ |
| **Lab Tests** | 200+ |
| **Test Panels** | 50+ |
| **Departments** | 6 |
| **Roles** | 5 |
| **Custom Fields** | 40+ |
| **Scheduled Tasks** | 5 |

---

## 🚀 Quick Start

### Installation (5 minutes)

```bash
# Clone and install
bench get-app https://github.com/yourusername/arogyapath.git
bench install-app arogyapath --site your-site.localhost

# Post-installation configuration
# 1. Create Pathology Lab
# 2. Create Lab Branch
# 3. Configure Lab Settings
# 4. Create Tax Templates (for GST)
```

### First Lab Order (2 minutes)

```
1. Create Patient
2. Create Lab Order (select tests)
3. Record Sample Collection
4. Enter Lab Results
5. Generate Lab Report
6. Create Invoice
7. Process Payment
```

See [INSTALLATION.md](INSTALLATION.md) for detailed setup instructions.

---

## 📋 Core Features

### Lab Operations
- **Lab Orders** — Create and track orders with multiple tests
- **Sample Collection** — Track collection centers and workflows
- **Lab Testing** — 200+ tests with calculated parameters
- **Lab Results** — Advanced result entry with QC validation
- **Lab Reports** — Professional reports with signatures and QR codes
- **Quality Control** — QC material tracking and Westgard rules

### Financial Management
- **Lab Invoice** — GST-compliant invoicing with automatic tax calculations
- **Payment Entry** — Integrated payment processing
- **Payment Request** — Online payment support via Razorpay
- **Doctor Commission** — Automatic commission calculation
- **Corporate Accounts** — Special pricing for corporate clients
- **Discount Schemes** — Flexible discount management

### Inventory & Equipment
- **Reagent Management** — Lot tracking with expiry alerts
- **Equipment Calibration** — NABL-compliant calibration logging
- **Analyzer Management** — Equipment tracking with history
- **Stock Ledger** — Real-time inventory tracking

### GST Compliance (India)
- **Automatic Tax Calculation** — CGST/SGST/IGST based on location
- **Tax Templates** — Pre-configured for intra-state and inter-state
- **GSTIN Validation** — Built-in validation with state code extraction
- **Tax Invoices** — Professional tax invoice and bill of supply formats
- **Place of Supply** — Automatic determination based on customer location

### Notifications & Alerts
- **TAT Alerts** — Turn-around-time breach notifications
- **Expiry Alerts** — Reagent and calibration expiry notifications
- **Critical Results** — Automatic alerts for critical lab values
- **WhatsApp Integration** — Send notifications via WhatsApp

For complete feature list, see [FEATURES.md](FEATURES.md).

---

## 🏗️ Architecture

ArogyaPath follows a layered architecture built on Frappe Framework:

```
┌─────────────────────────────────────┐
│      Frappe Desk (Vue.js UI)        │
├─────────────────────────────────────┤
│    Frappe Framework (Backend)       │
│  - DocType Controllers              │
│  - Custom Scripts (JS/Python)       │
│  - Hooks & Event Handlers           │
├─────────────────────────────────────┤
│  ArogyaPath Application Layer       │
│  - Controllers (Cross-cutting)      │
│  - Utils (GST, GSTIN, Calcs)        │
│  - Seed Data (Tests, Templates)     │
├─────────────────────────────────────┤
│      Database (MariaDB)             │
│  - 60+ DocTypes                     │
│  - Child Tables & Relationships     │
└─────────────────────────────────────┘
```

### Key Modules

| Module | Purpose |
|--------|---------|
| **controllers/** | Cross-cutting hooks for Lab Invoice validation and GST |
| **doctype/** | 60+ DocTypes for lab operations, finance, and inventory |
| **utils/** | GST calculations, GSTIN validation, state code mapping |
| **seed_*.py** | 200+ lab tests, tax templates, chart of accounts |
| **print_format/** | Tax Invoice and Lab Report Jinja2 templates |
| **workspace/** | Organized module navigation for different roles |
| **tasks.py** | Scheduled jobs for TAT alerts and expiry notifications |

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system design.

---

## 🔧 Configuration

### Basic Setup (Post-Installation)

1. **Create Pathology Lab** — Your lab entity with GSTIN
2. **Create Lab Branch** — Physical lab locations
3. **Configure Lab Settings** — Default TAT, critical thresholds
4. **Create Tax Templates** — GST configuration for India
5. **Add Collection Centers** — Sample collection locations
6. **Configure Notifications** — Email and WhatsApp alerts

### Advanced Configuration

- **Custom Test Parameters** — Add calculated parameters
- **Reference Ranges** — Configure by age and gender
- **Westgard Rules** — QC validation rules
- **Report Templates** — Custom report layouts
- **Payment Gateway** — Razorpay integration

See [INSTALLATION.md](INSTALLATION.md) for step-by-step configuration.

---

## 📖 Documentation

### User Documentation
- [FEATURES.md](FEATURES.md) — Complete feature documentation
- [INSTALLATION.md](INSTALLATION.md) — Setup and configuration guide
- [FAQ](#faq) — Frequently asked questions

### Developer Documentation
- [ARCHITECTURE.md](ARCHITECTURE.md) — System design and structure
- [CONTRIBUTING.md](CONTRIBUTING.md) — Development guidelines
- [API Reference](#api-reference) — API endpoints

### Quick Links
- [GitHub Issues](https://github.com/yourusername/arogyapath/issues)
- [GitHub Discussions](https://github.com/yourusername/arogyapath/discussions)
- [Frappe Documentation](https://frappe.io/docs)

---

## 🔌 API Reference

### Payment Entry Creation

**Endpoint:** `arogyapath.arogyapath.doctype.lab_invoice.lab_invoice_payment.get_payment_entry`

**Parameters:**
- `lab_invoice_name` (string, required) — Lab Invoice document name

**Response:**
```json
{
  "doctype": "Payment Entry",
  "name": "PE-2026-00001",
  "payment_type": "Receive",
  "company": "Company Name",
  "party": "PT-2026-00001",
  "party_name": "Patient Name",
  "paid_amount": 472.00,
  "received_amount": 472.00
}
```

**Example:**
```javascript
frappe.call({
  method: 'arogyapath.arogyapath.doctype.lab_invoice.lab_invoice_payment.get_payment_entry',
  args: {
    lab_invoice_name: 'INV-BRANCH-2026-00009'
  },
  callback: function(r) {
    if (!r.exc) {
      frappe.set_route('Form', r.message.doctype, r.message.name);
    }
  }
});
```

### GST Details Fetching

**Endpoint:** `arogyapath.arogyapath.controllers.lab_invoice.get_patient_gst_details`

**Parameters:**
- `patient` (string, required) — Patient document name
- `pathology_lab` (string, required) — Pathology Lab document name

**Response:**
```json
{
  "customer_address": "Address-001",
  "company_address": "Address-002",
  "billing_address_gstin": "27AAAAP0267H2ZN",
  "company_gstin": "27ACDFA2150L1ZJ",
  "gst_category": "Registered Regular",
  "place_of_supply": "27-Maharashtra",
  "tax_category": "In State GST",
  "taxes_and_charges": "GST 18% Intrastate - Lab Name",
  "contact_person": "Patient Name",
  "contact_display": "Patient",
  "contact_mobile": "9560859178",
  "contact_email": "patient@example.com",
  "company_contact_person": "Lab Name"
}
```

### GST Calculation

**Function:** `arogyapath.arogyapath.utils.gst.compute_invoice_taxes`

**Parameters:**
- `doc` (LabInvoice) — Lab Invoice document

**Behavior:**
- Calculates item-level CGST/SGST/IGST amounts
- Aggregates tax totals
- Updates invoice grand total
- Handles tax exemptions and discounts

---

## 🧪 Testing

### Run Tests

```bash
# All tests
bench --site your-site.localhost run-tests --module arogyapath

# Specific test
bench --site your-site.localhost run-tests --module arogyapath --test test_lab_invoice

# With verbose output
bench --site your-site.localhost run-tests --module arogyapath -v
```

### Test Coverage

- Unit tests for utility functions (GST, GSTIN validation)
- Integration tests for DocType workflows
- Edge case tests for validation logic

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Development setup
- Code style guidelines
- Testing procedures
- Pull request process
- Issue reporting guidelines

### Quick Contribution Steps

1. Fork the repository
2. Create feature branch: `git checkout -b feature/your-feature`
3. Make changes and test: `bench --site dev.localhost run-tests --module arogyapath`
4. Commit with clear message: `git commit -m "feat: Add feature description"`
5. Push to fork: `git push origin feature/your-feature`
6. Create Pull Request

---

## 📋 FAQ

### Installation & Setup

**Q: What are the system requirements?**
A: Python 3.10+, MariaDB 10.3+, Node.js 14+, and Frappe v15+. See [INSTALLATION.md](INSTALLATION.md) for details.

**Q: How do I install ArogyaPath?**
A: Use `bench get-app` to clone the repository, then `bench install-app arogyapath`. See [INSTALLATION.md](INSTALLATION.md) for step-by-step instructions.

**Q: Do I need ERPNext installed?**
A: No, but it's recommended. ArogyaPath uses Frappe's Company and Chart of Accounts, which are available in both Frappe and ERPNext.

**Q: How do I configure GST?**
A: Create Lab Tax Categories and Lab Tax Templates. See [INSTALLATION.md](INSTALLATION.md) for detailed configuration steps.

### Features & Usage

**Q: How many lab tests are included?**
A: 200+ predefined tests organized by department. You can add custom tests as needed.

**Q: Can I customize lab tests and parameters?**
A: Yes, you can add custom tests and test parameters. See [FEATURES.md](FEATURES.md) for details.

**Q: How does GST calculation work?**
A: ArogyaPath automatically calculates CGST/SGST for intra-state and IGST for inter-state transactions based on customer location. See [FEATURES.md](FEATURES.md) for details.

**Q: Can I integrate with payment gateways?**
A: Yes, Razorpay integration is supported via the Payments app. See [INSTALLATION.md](INSTALLATION.md) for setup.

### Development & Customization

**Q: How do I extend ArogyaPath?**
A: You can create custom DocTypes, add custom fields, and write custom scripts. See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

**Q: How do I report bugs?**
A: Open an issue on GitHub with clear description, steps to reproduce, and expected vs actual behavior.

**Q: How do I request features?**
A: Open a feature request issue on GitHub with use case and proposed implementation.

**Q: Can I contribute code?**
A: Yes! See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

### Troubleshooting

**Q: Lab tests are not appearing after installation.**
A: Run `bench --site your-site.localhost clear-cache` and refresh the browser. If still not working, check the installation logs.

**Q: GSTIN validation is failing.**
A: Ensure the GSTIN format is correct (15 characters) and the state code is valid. Check custom fields are created properly.

**Q: Payment Entry creation is failing.**
A: Ensure the Pathology Lab has a Company linked, and the Company has a Chart of Accounts configured.

**Q: Tax templates are not showing in Lab Invoice.**
A: Ensure Lab Tax Categories and Lab Tax Templates are created. Clear cache and refresh browser.

---

## 📞 Support

### Getting Help

1. **Check Documentation:**
   - [FEATURES.md](FEATURES.md) — Feature documentation
   - [INSTALLATION.md](INSTALLATION.md) — Setup guide
   - [ARCHITECTURE.md](ARCHITECTURE.md) — System design

2. **Search Issues:**
   - [GitHub Issues](https://github.com/yourusername/arogyapath/issues)
   - [GitHub Discussions](https://github.com/yourusername/arogyapath/discussions)

3. **Contact:**
   - Email: hello@amitkumar.live
   - GitHub: [@amitkumar](https://github.com/amitkumar)

---

## 📝 License

MIT License — See [LICENSE](LICENSE) file for details

---

## 👨‍💻 Author

**Amit Kumar**
- Email: hello@amitkumar.live
- GitHub: [@amitkumar](https://github.com/amitkumar)

---

## 🙏 Acknowledgments

- Built on [Frappe Framework](https://frappe.io/)
- GST implementation inspired by [India Compliance](https://github.com/frappe/india-compliance)
- Payment integration via [Payments App](https://github.com/frappe/payments)

---

## 🗺️ Roadmap

- [ ] Mobile app for field technicians
- [ ] Advanced analytics and dashboards
- [ ] Integration with LIS (Laboratory Information System)
- [ ] Multi-language support
- [ ] Advanced report scheduling
- [ ] Inventory forecasting
- [ ] Barcode scanning integration
- [ ] DICOM support for imaging

---

**Made with ❤️ for pathology labs worldwide**

