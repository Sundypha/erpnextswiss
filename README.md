# erpnextswiss
ERPNext application for Switzerland-specific use cases

ERPNext ([https://www.erpnext.org](https://www.erpnext.org)) is a global, leading, cloud based
open source enterprise resource planning software. ERPNext is a trademark by Frappé Technologies.

The ERPNextSwiss application adds country-specific features to this platform such as 
bank, tax and payment integrations.

ERPNextSwiss is maintaned by [libracore AG](https://www.libracore.com).

For more information, refer to [https://erpnext.swiss](https://erpnext.swiss)

## License 
GNU Affero General Public License, refer to LICENSE

ERPNextSwiss is developed and maintained by libracore and contributors. 
The copyright is owned by libracore and contributors. 
The software comes as-is without any warranty.

## Requirements
Requires an ERPNext server instance (refer to [https://github.com/frappe/erpnext](https://github.com/frappe/erpnext))

## Compatibility
ERPNextSwiss provides version branches for the Frappe/ERPNext release it targets.
There are compatibility branches for v11 (for users who prefer the old desk) and
v13/v14/v15, `master` (v14/v15), and **`version-16`** for Frappe/ERPNext v16.

The `version-16` branch installs, migrates and builds cleanly on **Python 3.11–3.14**
(Frappe v16 itself runs on Python 3.14). Framework compatibility is declared in
`pyproject.toml` under `[tool.bench.frappe-dependencies]`.

## Installation
From the frappe-bench folder, execute (for a Frappe/ERPNext v16 bench, use the
`version-16` branch):

    $ bench get-app https://github.com/libracore/erpnextswiss.git --branch version-16
    $ bench --site site_name install-app erpnextswiss

(where site_name is e.g. erp.example.com)

For a `frappe_docker` layered build, add to your `apps.json`:

    { "url": "https://github.com/libracore/erpnextswiss", "branch": "version-16" }

### Optional dependencies
The default install stays lean. Some features need extra Python packages, declared
as extras in `pyproject.toml`:

    $ pip install -e "apps/erpnextswiss[ocr]"    # read QR codes from scanned PDFs (opencv-python, numpy)
    $ pip install -e "apps/erpnextswiss[ebics]"  # EBICS bank connectivity (licensed `fintech` library)
    $ pip install -e "apps/erpnextswiss[sftp]"   # Planzer SFTP shipment upload (pysftp)
    $ pip install -e "apps/erpnextswiss[all]"    # all of the above

The Human-Resources features (Salary Certificate, worktime reporting, automatic
settling of salary/expense payments, and doctypes that link to Employee / Salary
Slip) require the [`hrms`](https://github.com/frappe/hrms) app to be installed.

## Update
Run updates with

    $ bench update

In case you update from the sources and observe an error, make sure to update dependencies with

    $ bench update --requirements

## Features 
* Banking / Accounting
    * Bank wizard: processes camt.053 and camt.054 files to payment entries (including linking to related documents)
    * Payment proposal: create payment files based on open purchase invoices, expenses and salaries (pain.001)
    * Direct debit proposal: create payment files from direct debit enabled sales invoices (pain.008)
    * Payment reminder: create payment reminders for overdue sales invoices
    * Bank import: allows to import bank account statements to update local payment entries (receiving; csv or camt)
    * Match payments: match unpaid sales invoices with the corresponding payments
    * Payment export: allows to create payment files for banks (pain.001) from payment entries (paying)
    * QR invoices and ESR invoices: outgoing (sales invoices) as well as incoming (scan purchase invoices); QR invoice supports ESR/NON/SCOR
    * ZUGFeRD: fully electronic invoices.
    * ZUGFeRD Wizard: read and interpret both ZUGFeRD and QR-invoices to purchase invoices
* Taxes
    * Import monthly average exchange rates, daily exchange rates (ESTV)
    * VAT declaration (with ESTV data transfer easyTax/ePortal)
    * Zefix integration
* Human resources
    * Salary certificate ("Lohnausweis")
    * Seco overtime reporting (based on timesheet)
    * Seco monthly worktime (working hours and breaks) (based on timesheet)
    * Automatic settling of expenses and salary payments
    * Import public holidays (region-dependent) into the Holidays List
* General tools
    * Postal code lookup
    * Script-based data import
    * Large data import tools
    * Dynamic newsletter content
 * Interfaces
    * Interface to ESTV: 
        * read exchange rates
        * monthly average rates
        * transmit tax forms
    * Interface to abacus (export transaction data)
    * ISO 20022
    * EBICS: electronic banking internet communication standard, allows to fully automate bank integration
    * ZUGFeRD
    * Interface to Zefix
    * Payments
        * Datatrans interface for payments
        * Payrexx payment interface
    * EDI connector: allows to fully integrate EDI exchange (PRICAT, DESADV, ORDERS, SLSRPT, ...)
    * NextCloud:
        * Update contacts from ERPNext to NextCloud address book
    * Logistics:
        * Interface to Planzer logistics
        * Interface to DPD
    * CalDav-feed for CRM (Lead/Customer) and ToDos
    * Mautic Integration
 * Business Intelligence
    * Data Provider for Looker Studio (refer to the libracore Connector to connect to your data)
 * Productivity
    * Gitlab integration: sync ERPNext Issues to Gitlab

## Release notes
Refer to [https://github.com/libracore/erpnextswiss/wiki/Release-Notes](https://github.com/libracore/erpnextswiss/wiki/Release-Notes)

## Data protection
Please note that the provided sample QR code invoice uses a libracore server to process QR codes according to ISO 20022. The server is located in Switzerland, the invoice details will be transmitted to the server for processing.

Please use a personal QR-code generation server to prevent data being sent to libracore. The source code is available from [https://github.com/lasalesi/phpqrcode](PhpQrCode)
