import unittest
from legacy_documenter.documentation.contracts import *

def contract(kind="FUNCTIONAL_ASSESSMENT", approved=False):
    return DocumentationContract(DocumentMetadata("DOC-1",kind,{"sha256":"x"},status="VALIDATED" if approved else "DRAFT",validation_status="VALIDATED" if approved else "NOT_VALIDATED",approval_status="APPROVED" if approved else "NOT_APPROVED"))

class V3R1Tests(unittest.TestCase):
    def test_valid_confirmed_claim_and_determinism(self):
        item=contract(); item.claims=[DocumentClaim("C-1","DOC-1","scope","TECHNOLOGY","x","CONFIRMED","CONFIRMED",[EvidenceReference("DETERMINISTIC_CODE_FACT","project:1",True)])]
        self.assertTrue(item.validate()); self.assertEqual(item.canonical_json(),item.canonical_json())
    def test_confirmed_requires_authoritative_evidence(self):
        item=contract(); item.claims=[DocumentClaim("C-1","DOC-1","s","UNKNOWN","x","CONFIRMED","CONFIRMED")]
        with self.assertRaises(ValueError): item.validate()
    def test_duplicate_and_approval_gate(self):
        item=contract(); item.modules=[FunctionalModule("M","UNKNOWN","","UNRESOLVED","UNRESOLVED"),FunctionalModule("M","UNKNOWN","","UNRESOLVED","UNRESOLVED")]
        with self.assertRaises(ValueError): item.validate()
        self.assertTrue(approval_gate(contract(approved=True),contract("TECHNICAL_ASSESSMENT",True)))
    def test_templates_and_stable_id(self):
        self.assertIn("Functional Modules",functional_markdown_template()); self.assertIn("Patterns",technical_markdown_template()); self.assertEqual(stable_id("X","a"),stable_id("X","a"))
