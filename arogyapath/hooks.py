app_name = "arogyapath"
app_title = "ArogyaPath"
app_publisher = "Amit Kumar"
app_description = "Pathology Lab Management System"
app_email = "hello@amitkumar.live"
app_license = "mit"

# Apps
# ------------------

required_apps = ["frappe", "payments"]

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "arogyapath",
# 		"logo": "/assets/arogyapath/logo.png",
# 		"title": "ArogyaPath",
# 		"route": "/arogyapath",
# 		"has_permission": "arogyapath.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/arogyapath/css/arogyapath.css"
# app_include_js = "/assets/arogyapath/js/arogyapath.js"

# include js, css files in header of web template
# web_include_css = "/assets/arogyapath/css/arogyapath.css"
# web_include_js = "/assets/arogyapath/js/arogyapath.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "arogyapath/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
	"Address": "public/js/address.js",
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "arogyapath/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Boot Session
# ----------
# Boot session handler to add custom data
boot_session = "arogyapath.arogyapath.startup.boot.boot_session"

# Jinja
# ----------

# add methods and filters to jinja environment
jinja = {
	"methods": [
		"arogyapath.arogyapath.utils.report.get_report_context",
		"arogyapath.arogyapath.utils.gst.format_gstin",
	]
}

# Installation
# ------------

# before_install = "arogyapath.arogyapath.install.before_install"
after_install = "arogyapath.arogyapath.install.after_install"
after_migrate = "arogyapath.arogyapath.install.after_migrate"

# Fixtures
# --------
# Workspace is exported as a fixture — roles/role profiles are created in install.py
# Custom Fields are created programmatically via setup_custom_fields() (India Compliance pattern)
fixtures = [
	{
		"dt": "Workspace",
		"filters": [
			["module", "=", "ArogyaPath"]
		]
	}
]

# Uninstallation
# ------------

# before_uninstall = "arogyapath.uninstall.before_uninstall"
# after_uninstall = "arogyapath.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "arogyapath.utils.before_app_install"
# after_app_install = "arogyapath.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "arogyapath.utils.before_app_uninstall"
# after_app_uninstall = "arogyapath.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "arogyapath.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# NOTE: Lab Order, Lab Result, Lab Invoice, Reagent Lot all have logic in their
# own DocType controllers (doctype/*/py). The controllers/ folder is reserved
# for cross-cutting hooks that augment behaviour without replacing the controller.
doc_events = {
	"Address": {
		"validate": "arogyapath.arogyapath.overrides.address.validate",
	},
	"Lab Invoice": {
		"validate": "arogyapath.arogyapath.controllers.lab_invoice.validate",
	},
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	"daily": [
		"arogyapath.arogyapath.tasks.send_tat_alerts",
		"arogyapath.arogyapath.tasks.flag_expiring_reagents",
		"arogyapath.arogyapath.tasks.flag_expiring_amc",
		"arogyapath.arogyapath.tasks.flag_expiring_calibrations",
	],
	"hourly": [
		"arogyapath.arogyapath.tasks.check_critical_tat_breach",
	],
}

# Testing
# -------

# before_tests = "arogyapath.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "arogyapath.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "arogyapath.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["arogyapath.utils.before_request"]
# after_request = ["arogyapath.utils.after_request"]

# Job Events
# ----------
# before_job = ["arogyapath.utils.before_job"]
# after_job = ["arogyapath.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"arogyapath.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

