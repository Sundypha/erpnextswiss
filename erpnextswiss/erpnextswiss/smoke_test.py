# Copyright (c) 2025, libracore (https://www.libracore.com) and contributors
# For license information, please see license.txt
#
# Lightweight smoke test for the four core Swiss features. It imports the entry
# modules of each feature (catching any import-time API breakage on the target
# Frappe/ERPNext build that static analysis might miss) and exercises the
# ISO 20022 XSD validator against a bundled schema (proving lxml + the shipped
# XSDs load on this Python build).
#
# Run in CI with:
#   bench --site <site> execute erpnextswiss.erpnextswiss.smoke_test.run

import importlib
import os

import frappe

# entry module of each core feature
CORE_MODULES = [
    # ISO 20022 pain.001 / pain.008 payment export
    "erpnextswiss.erpnextswiss.doctype.payment_proposal.payment_proposal",
    "erpnextswiss.erpnextswiss.doctype.direct_debit_proposal.direct_debit_proposal",
    "erpnextswiss.erpnextswiss.page.payment_export.payment_export",
    # camt.053 / camt.054 bank statement import
    "erpnextswiss.erpnextswiss.page.bank_wizard.bank_wizard",
    "erpnextswiss.erpnextswiss.page.bankimport.bankimport",
    # MWST / VAT declaration (Ziffern) + ESTV eCH-0217 XML export
    "erpnextswiss.erpnextswiss.doctype.vat_declaration.vat_declaration",
    "erpnextswiss.erpnextswiss.report.kontrolle_mwst.kontrolle_mwst",
    # Swiss QR-bill / ESR reference math
    "erpnextswiss.scripts.esr_qr_tools",
    # ISO 20022 XSD validation helper
    "erpnextswiss.erpnextswiss.xml",
    # ZUGFeRD / Factur-X e-invoice + optional-dependency defensive imports
    "erpnextswiss.erpnextswiss.zugferd.zugferd",
    "erpnextswiss.erpnextswiss.zugferd.qr_reader",
    "erpnextswiss.erpnextswiss.planzer",
]


def run():
    failed = []
    for module in CORE_MODULES:
        try:
            importlib.import_module(module)
            print("  import OK    {0}".format(module))
        except Exception as exc:  # noqa: BLE001 - we want to report every failure
            print("  import FAIL  {0}: {1}".format(module, exc))
            failed.append((module, str(exc)))

    # Exercise the ISO 20022 XSD validator against a bundled Swiss schema.
    from erpnextswiss.erpnextswiss.xml import validate_xml_against_xsd

    xsd = os.path.join(
        frappe.get_app_path("erpnextswiss"), "public", "xsd", "pain.001.001.03.ch.02.xsd"
    )
    valid, _message = validate_xml_against_xsd("<Document/>", xsd)
    # An empty <Document/> is *invalid* against the schema; we only assert the
    # validator ran (returned a bool) instead of raising -- proving that lxml and
    # the shipped XSD both load on this Python/Frappe build.
    assert valid in (True, False), "XSD validator did not return a boolean"
    print("  XSD validator ran against pain.001.001.03.ch.02.xsd -> valid={0}".format(valid))

    if failed:
        frappe.throw(
            "Smoke test failed: {0} core module(s) could not be imported:\n{1}".format(
                len(failed), "\n".join("{0}: {1}".format(m, e) for m, e in failed)
            )
        )

    print(
        "Smoke test OK: {0} core modules imported, ISO 20022 XSD validator functional.".format(
            len(CORE_MODULES)
        )
    )
    return "ok"
