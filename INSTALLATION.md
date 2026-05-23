# ArogyaPath Installation Guide

## Prerequisites

Before installing ArogyaPath, ensure you have:

### System Requirements
- **OS:** Linux (Ubuntu 20.04+, Debian 10+) or macOS
- **Python:** 3.10 or higher
- **Node.js:** 14.0 or higher
- **MariaDB:** 10.3 or higher
- **Git:** 2.0 or higher

### Frappe Setup
- **Frappe Bench:** Latest version
- **Frappe Framework:** v15.0 or higher
- **ERPNext:** v15.0 (optional, but recommended)

### Required Apps
- **frappe** — Core framework
- **payments** — Payment gateway integration (optional, but recommended for payment features)

### Hardware
- **Disk Space:** Minimum 5GB free space
- **RAM:** Minimum 2GB (4GB recommended)
- **CPU:** Dual-core processor minimum

## Installation Steps

### Step 1: Create a Frappe Bench (if not already done)

```bash
# Install bench
pip install frappe-bench

# Create a new bench directory
bench init frappe-bench --frappe-branch version-15
cd frappe-bench

# Create a new site
bench new-site pathlab.localhost
```

### Step 2: Install Required Apps

```bash
# Install Frappe (usually already installed)
bench get-app frappe

# Install Payments app (for payment gateway support)
bench get-app https://github.com/frappe/payments.git --branch develop
bench install-app payments --site pathlab.localhost
```

### Step 3: Get ArogyaPath App

```bash
# Clone the ArogyaPath repository
bench get-app https://github.com/yourusername/arogyapath.git --branch main

# Or if you have local copy
bench get-app /path/to/arogyapath
```

### Step 4: Install ArogyaPath

```bash
# Install the app on your site
bench install-app arogyapath --site pathlab.localhost

# Clear cache
bench --site pathlab.localhost clear-cache

# Restart bench
bench restart
```

### Step 5: Verify Installation

```bash
# Check if app is installed
bench --site pathlab.localhost list-apps

# You should see: arogyapath in the list
```

## Post-Installation Configuration

### 1. Create Pathology Lab

1. Go to **Pathology Lab** DocType
2. Click **+ New**
3. Fill in details:
   - **Lab Name:** Your lab name
   - **Company:** Select or create company
   - **GSTIN:** Your lab's GSTIN
   - **Address:** Lab address
   - **Contact:** Lab contact details
4. Save and Submit

### 2. Create Lab Branch

1. Go to **Lab Branch** DocType
2. Click **+ New**
3. Fill in details:
   - **Branch Name:** Branch name
   - **Pathology Lab:** Select your lab
   - **Address:** Branch address
4. Save and Submit

### 3. Configure Lab Settings

1. Go to **Lab Settings** DocType
2. Click on the default settings document
3. Configure:
   - **Default TAT (hours):** e.g., 24
   - **Critical TAT (hours):** e.g., 4
   - **Default Sample Type:** Select default
   - **Default Department:** Select default
   - **Report Header Config:** Select header template
4. Save

### 4. Create Lab Departments

1. Go to **Lab Department** DocType
2. Create departments:
   - Clinical Pathology
   - Biochemistry
   - Microbiology
   - Immunology
   - Hematology
   - Serology
3. Save each department

### 5. Configure Tax Settings (India GST)

#### Create Tax Categories

1. Go to **Lab Tax Category** DocType
2. Create two categories:

**Category 1: In State GST**
- **Category Name:** In State GST
- **Is Inter State:** Unchecked
- **Is Reverse Charge:** Unchecked

**Category 2: Out of State GST**
- **Category Name:** Out of State GST
- **Is Inter State:** Checked
- **Is Reverse Charge:** Unchecked

#### Create Tax Templates

1. Go to **Lab Tax Template** DocType
2. Create templates:

**Template 1: GST 18% Intrastate**
- **Template Name:** GST 18% Intrastate - [Lab Name]
- **Tax Category:** In State GST
- Add tax rows:
  - CGST @ 9%
  - SGST @ 9%

**Template 2: GST 18% Interstate**
- **Template Name:** GST 18% Interstate - [Lab Name]
- **Tax Category:** Out of State GST
- Add tax rows:
  - IGST @ 18%

### 6. Create Collection Centers

1. Go to **Collection Center** DocType
2. Click **+ New**
3. Fill in details:
   - **Center Name:** Center name
   - **Address:** Center address
   - **Contact:** Contact details
4. Save and Submit

### 7. Add Lab Tests

The app comes with 200+ pre-seeded lab tests. To add custom tests:

1. Go to **Lab Test Master** DocType
2. Click **+ New**
3. Fill in details:
   - **Test Code:** Unique code (e.g., HB)
   - **Test Name:** Full test name
   - **Department:** Select department
   - **Sample Type:** Select sample type
   - **HSN/SAC Code:** 999316 (for pathology)
   - **GST Treatment:** Registered
   - **Is GST Exempt:** No
4. Add test parameters in the **Parameters** table
5. Save and Submit

### 8. Create Test Panels (Optional)

1. Go to **Lab Test Panel** DocType
2. Click **+ New**
3. Fill in details:
   - **Panel Name:** Panel name
   - **Department:** Select department
   - Add tests in the **Panel Items** table
4. Save and Submit

### 9. Configure Notifications (Optional)

1. Go to **Notification Template** DocType
2. Configure templates for:
   - TAT Alerts
   - Critical Results
   - Payment Received
   - Sample Collected
3. Set up WhatsApp integration if needed

### 10. Set Up Payment Gateway (Optional)

If using Razorpay for online payments:

1. Go to **Razorpay Settings** DocType
2. Fill in:
   - **API Key:** Your Razorpay API key
   - **API Secret:** Your Razorpay API secret
3. Save

## Troubleshooting

### Installation Issues

#### Issue: "App not found" error
```bash
# Solution: Ensure app is in apps directory
ls apps/arogyapath

# If not present, clone again
bench get-app https://github.com/yourusername/arogyapath.git
```

#### Issue: "Module not found" error
```bash
# Solution: Clear cache and restart
bench --site pathlab.localhost clear-cache
bench restart
```

#### Issue: Database migration errors
```bash
# Solution: Run migrations manually
bench --site pathlab.localhost migrate

# If still failing, check logs
bench --site pathlab.localhost show-log
```

### Configuration Issues

#### Issue: Tax templates not appearing
```
Solution:
1. Ensure Lab Tax Category is created
2. Ensure Lab Tax Template is created
3. Clear cache: bench --site pathlab.localhost clear-cache
4. Refresh browser
```

#### Issue: Lab tests not seeding
```
Solution:
1. Check if seed_catalog.py ran successfully
2. Check logs: bench --site pathlab.localhost show-log
3. Manually run seed:
   bench --site pathlab.localhost console
   >>> from arogyapath.arogyapath.seed_catalog import seed_lab_tests
   >>> seed_lab_tests()
```

#### Issue: GSTIN validation failing
```
Solution:
1. Check GSTIN format (15 characters)
2. Ensure state code is valid
3. Check custom fields are created:
   bench --site pathlab.localhost console
   >>> from arogyapath.arogyapath.utils.custom_fields import setup_custom_fields
   >>> setup_custom_fields()
```

### Performance Issues

#### Issue: Slow lab order creation
```
Solution:
1. Check if indexes are created:
   bench --site pathlab.localhost console
   >>> frappe.db.commit()
2. Clear cache:
   bench --site pathlab.localhost clear-cache
3. Optimize database:
   bench --site pathlab.localhost console
   >>> frappe.db.optimize_table('tabLab Order')
```

#### Issue: Slow report generation
```
Solution:
1. Check if test data is too large
2. Archive old data:
   bench --site pathlab.localhost console
   >>> frappe.db.sql("DELETE FROM `tabLab Result` WHERE creation < DATE_SUB(NOW(), INTERVAL 1 YEAR)")
3. Rebuild indexes
```

## Upgrade Instructions

### From Previous Version

```bash
# Fetch latest code
cd apps/arogyapath
git pull origin main

# Clear cache
bench --site pathlab.localhost clear-cache

# Run migrations
bench --site pathlab.localhost migrate

# Restart
bench restart
```

### Database Backup Before Upgrade

```bash
# Backup database
bench --site pathlab.localhost backup

# Backup will be saved in: ./sites/pathlab.localhost/private/backups/
```

## Development Setup

### Install Pre-commit Hooks

```bash
cd apps/arogyapath
pre-commit install
```

### Run Tests

```bash
# Run all tests
bench --site pathlab.localhost run-tests --module arogyapath

# Run specific test
bench --site pathlab.localhost run-tests --module arogyapath --test test_lab_invoice
```

### Enable Debug Mode

```bash
# Edit site config
nano sites/pathlab.localhost/site_config.json

# Add:
{
  "developer_mode": 1,
  "logging": 1
}

# Restart
bench restart
```

## Uninstallation

### Remove ArogyaPath App

```bash
# Uninstall from site
bench uninstall-app arogyapath --site pathlab.localhost

# Remove app directory
rm -rf apps/arogyapath

# Clear cache
bench --site pathlab.localhost clear-cache

# Restart
bench restart
```

## Support

If you encounter issues:

1. **Check Logs:**
   ```bash
   bench --site pathlab.localhost show-log
   ```

2. **Check GitHub Issues:**
   Visit: https://github.com/yourusername/arogyapath/issues

3. **Check Documentation:**
   - README.md — Overview
   - FEATURES.md — Feature details
   - ARCHITECTURE.md — System design

4. **Contact Support:**
   Email: hello@amitkumar.live

## Next Steps

After installation:

1. Create a test patient
2. Create a lab order
3. Enter sample collection details
4. Enter lab results
5. Generate lab report
6. Create invoice
7. Process payment

See [FEATURES.md](FEATURES.md) for detailed feature documentation.

