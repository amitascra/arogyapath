# Contributing to ArogyaPath

Thank you for your interest in contributing to ArogyaPath! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Help others learn and grow

## Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/yourusername/arogyapath.git
cd arogyapath

# Add upstream remote
git remote add upstream https://github.com/original/arogyapath.git
```

### 2. Set Up Development Environment

```bash
# Create a new bench (if not already done)
bench init frappe-bench --frappe-branch version-15
cd frappe-bench

# Get the app from your fork
bench get-app /path/to/your/arogyapath

# Install the app
bench install-app arogyapath --site dev.localhost

# Install pre-commit hooks
cd apps/arogyapath
pre-commit install
```

### 3. Create a Feature Branch

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
```

## Development Workflow

### Code Style

#### Python Code

- **Line Length:** 110 characters max
- **Indentation:** Tabs (4 spaces)
- **Imports:** Organized by standard library, third-party, local
- **Docstrings:** Use triple quotes for all functions and classes

```python
def calculate_gst(amount, rate):
	"""
	Calculate GST amount based on rate.
	
	Args:
		amount (float): Base amount
		rate (float): GST rate percentage
	
	Returns:
		float: Calculated GST amount
	"""
	return amount * rate / 100
```

#### JavaScript Code

- **Line Length:** 110 characters max
- **Indentation:** Tabs
- **Semicolons:** Required
- **Quotes:** Single quotes for strings

```javascript
frappe.ui.form.on('Lab Invoice', {
	refresh: function(frm) {
		if (!frm.is_new() && frm.doc.docstatus === 1) {
			frm.add_custom_button(__('Payment'), function() {
				// Implementation
			}, __('Create'));
		}
	}
});
```

### Code Quality Tools

The project uses pre-commit hooks for code quality. These run automatically before each commit:

- **ruff** — Python linting and formatting
- **eslint** — JavaScript linting
- **prettier** — Code formatting
- **pyupgrade** — Python syntax modernization

#### Running Pre-commit Manually

```bash
# Run on all files
pre-commit run --all-files

# Run on staged files
pre-commit run

# Run specific hook
pre-commit run ruff --all-files
```

### Testing

#### Running Tests

```bash
# Run all tests
bench --site dev.localhost run-tests --module arogyapath

# Run specific test file
bench --site dev.localhost run-tests --module arogyapath --test test_lab_invoice

# Run with verbose output
bench --site dev.localhost run-tests --module arogyapath -v
```

#### Writing Tests

Create test files in `arogyapath/doctype/{doctype}/test_{doctype}.py`:

```python
import frappe
from frappe.tests.utils import FrappeTestCase

class TestLabInvoice(FrappeTestCase):
	def setUp(self):
		"""Set up test data"""
		self.patient = frappe.get_doc({
			'doctype': 'Patient',
			'patient_name': 'Test Patient',
			'email': 'test@example.com'
		}).insert()
	
	def test_invoice_creation(self):
		"""Test lab invoice creation"""
		invoice = frappe.get_doc({
			'doctype': 'Lab Invoice',
			'patient': self.patient.name,
			'pathology_lab': 'ViditPath Lab'
		})
		invoice.insert()
		self.assertEqual(invoice.status, 'Draft')
	
	def test_gst_calculation(self):
		"""Test GST calculation"""
		# Test implementation
		pass
```

#### Test Coverage

Aim for:
- Unit tests for utility functions
- Integration tests for DocType workflows
- Edge case tests for validation logic

### Documentation

#### Docstrings

All functions and classes should have docstrings:

```python
def validate_gstin(gstin):
	"""
	Validate GSTIN format and extract state code.
	
	Args:
		gstin (str): 15-character GSTIN
	
	Returns:
		dict: {
			'is_valid': bool,
			'state_code': str,
			'state_name': str,
			'error': str (if invalid)
		}
	
	Raises:
		frappe.ValidationError: If GSTIN is invalid
	"""
	pass
```

#### Comments

Use comments for complex logic:

```python
# Calculate proportional discount across items
for item in items:
	# Apply discount proportionally based on item amount
	item_discount = (item.amount / total_amount) * discount_amount
	item.discount_amount = item_discount
```

#### Commit Messages

Use clear, descriptive commit messages:

```
# Good
feat: Add Payment Request button to Lab Invoice

- Implement Payment Request creation for online payments
- Follow ERPNext's Sales Invoice pattern
- Add button under Create menu group

# Bad
fix: bug
update: code
```

### Pull Request Process

#### Before Submitting

1. **Update your branch:**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run tests:**
   ```bash
   bench --site dev.localhost run-tests --module arogyapath
   ```

3. **Run pre-commit:**
   ```bash
   pre-commit run --all-files
   ```

4. **Update documentation:**
   - Update README.md if needed
   - Update FEATURES.md for new features
   - Update ARCHITECTURE.md for structural changes

#### Submitting PR

1. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request:**
   - Use the PR template
   - Provide clear description
   - Link related issues
   - Add screenshots for UI changes

3. **PR Template:**
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update
   
   ## Related Issues
   Closes #123
   
   ## Testing
   - [ ] Unit tests added
   - [ ] Integration tests added
   - [ ] Manual testing done
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Documentation updated
   - [ ] No breaking changes
   - [ ] Tests pass
   ```

### Code Review

#### Reviewing Code

- Check for code quality and style
- Verify tests are included
- Ensure documentation is updated
- Test locally if possible
- Provide constructive feedback

#### Responding to Reviews

- Address all comments
- Ask for clarification if needed
- Update code and push changes
- Mark conversations as resolved

## Types of Contributions

### Bug Reports

**File an issue with:**
- Clear title and description
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable
- Environment details (OS, Frappe version, etc.)

### Feature Requests

**Propose features with:**
- Clear use case and benefit
- Proposed implementation approach
- Examples from other systems
- Potential impact on existing features

### Documentation

**Improve documentation by:**
- Fixing typos and grammar
- Adding examples
- Clarifying complex sections
- Adding new guides

### Code Contributions

**Contribute code for:**
- Bug fixes
- New features
- Performance improvements
- Code refactoring

## Development Tips

### Debugging

```bash
# Enable debug mode
bench --site dev.localhost console

# Import and test
>>> from arogyapath.arogyapath.utils.gst import validate_gstin
>>> validate_gstin('27AAAAP0267H2ZN')

# Check logs
bench --site dev.localhost show-log
```

### Database Queries

```bash
bench --site dev.localhost console

# Query data
>>> frappe.db.get_list('Lab Invoice', fields=['name', 'patient', 'grand_total'])

# Get single document
>>> doc = frappe.get_doc('Lab Invoice', 'INV-001')

# Update data
>>> frappe.db.set_value('Lab Invoice', 'INV-001', 'status', 'Paid')
```

### Performance Testing

```bash
# Profile a function
import cProfile
cProfile.run('compute_invoice_taxes(doc)')

# Check query count
frappe.db.query_count = 0
# ... run code ...
print(f"Queries: {frappe.db.query_count}")
```

## Project Structure

```
arogyapath/
├── arogyapath/
│   ├── controllers/          # Cross-cutting hooks
│   ├── doctype/              # 60+ DocTypes
│   ├── utils/                # Utility functions
│   ├── print_format/         # Report templates
│   ├── workspace/            # Module navigation
│   ├── install.py            # Installation hooks
│   ├── tasks.py              # Scheduled jobs
│   └── seed_*.py             # Data seeding
├── public/
│   └── js/                   # Custom scripts
├── README.md                 # Main documentation
├── FEATURES.md               # Feature documentation
├── ARCHITECTURE.md           # Architecture guide
├── INSTALLATION.md           # Installation guide
├── CONTRIBUTING.md           # This file
├── LICENSE                   # MIT License
├── pyproject.toml            # Python project config
└── .pre-commit-config.yaml   # Pre-commit configuration
```

## Common Tasks

### Adding a New DocType

1. **Create DocType JSON:**
   ```bash
   bench new-doctype Lab Invoice Item
   ```

2. **Edit JSON file:**
   ```json
   {
     "doctype": "Lab Invoice Item",
     "fields": [
       {
         "fieldname": "test",
         "label": "Test",
         "fieldtype": "Link",
         "options": "Lab Test Master"
       }
     ]
   }
   ```

3. **Create Python controller:**
   ```python
   # arogyapath/doctype/lab_invoice_item/lab_invoice_item.py
   from frappe.model.document import Document
   
   class LabInvoiceItem(Document):
       pass
   ```

4. **Create test file:**
   ```python
   # arogyapath/doctype/lab_invoice_item/test_lab_invoice_item.py
   from frappe.tests.utils import FrappeTestCase
   
   class TestLabInvoiceItem(FrappeTestCase):
       pass
   ```

### Adding a New Feature

1. Create feature branch
2. Implement feature with tests
3. Update documentation
4. Submit PR with description
5. Address review comments
6. Merge to main

### Fixing a Bug

1. Create issue if not exists
2. Create bugfix branch
3. Write failing test
4. Fix bug
5. Verify test passes
6. Submit PR with issue reference

## Resources

- [Frappe Documentation](https://frappe.io/docs)
- [Frappe Framework GitHub](https://github.com/frappe/frappe)
- [ERPNext Documentation](https://docs.erpnext.com)
- [Python Style Guide (PEP 8)](https://www.python.org/dev/peps/pep-0008/)
- [JavaScript Style Guide (Airbnb)](https://github.com/airbnb/javascript)

## Questions?

- Check existing issues and discussions
- Review documentation
- Ask in GitHub discussions
- Email: hello@amitkumar.live

Thank you for contributing to ArogyaPath! 🙏

