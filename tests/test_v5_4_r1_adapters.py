"""V5.4 boundary, extension, compatibility and cache contract proofs."""
from __future__ import annotations

import ast
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from legacy_documenter.adapters.contracts import AdapterCapabilities, AdapterRegistry, AdapterSelectionError
from legacy_documenter.adapters.vbnet_webforms_oracle.adapter import ReferenceAdapter
from legacy_documenter.cache.context import build_context
from legacy_documenter.cache.manifest import validate_cache
from legacy_documenter.cli.full_pipeline import run_full_pipeline
from legacy_documenter.evidence.bundle import NormalizedEvidence
from legacy_documenter.evidence.entities import Component, SourceArtifact, ScanSummary
from legacy_documenter.evidence.identity import sha256_id
from legacy_documenter.evidence.invariants import validate_evidence
from legacy_documenter.evidence.persistence import write_evidence
from legacy_documenter.evidence.reference import EvidenceReference
from legacy_documenter.fingerprints import analyzer_code_fingerprint

ROOT=Path(__file__).resolve().parents[1]
PACKAGE=ROOT/'legacy_documenter'
FIXTURE=ROOT/'tests/fixtures/v4_2_r7_full_sample'


class SyntheticAdapter:
    descriptor=AdapterCapabilities('synthetic','1.0',frozenset({'synthetic'}),frozenset({'normalized_evidence'}))

    def normalize(self,indexes,repo_root=None):
        source_id=sha256_id('SRC','sample.synthetic')
        source=SourceArtifact(source_id,'sample.synthetic',1,'synthetic','synthetic','1.0',hashlib.sha256(b'x').hexdigest())
        component=Component(sha256_id('CMP','synthetic'), 'sample','unit',None,source_id,'confirmed',
                            'synthetic','1.0',provenance=[EvidenceReference.source(source_id)],extensions={'synthetic_fact':1})
        return NormalizedEvidence(source_artifacts=[source],components=[component],scan_summary=ScanSummary('',1,{'synthetic':1},[]))


class AdapterContractTests(unittest.TestCase):
    def test_selection_observed_kinds_unknown_and_duplicate(self):
        reference=ReferenceAdapter();fake=SyntheticAdapter()
        registry=AdapterRegistry([fake,reference])
        self.assertIs(registry.select(['vb_source','other']),reference)
        self.assertIs(registry.select(['synthetic']),fake)
        self.assertIsNone(registry.select(['javascript']))
        with self.assertRaises(AdapterSelectionError): registry.register(fake)
        with self.assertRaises(AdapterSelectionError): registry.select(['vb_source','synthetic'])

    def test_capabilities_and_version_are_explicit(self):
        descriptor=ReferenceAdapter().descriptor
        self.assertEqual(descriptor.cache_identity,('vbnet-webforms-oracle','1.0'))
        self.assertIn('database',descriptor.capabilities)
        self.assertEqual(descriptor.schema_version_target,'1.0')
        with self.assertRaises(AdapterSelectionError):
            AdapterRegistry([type('Invalid',(),{'descriptor':replace(descriptor,adapter_version='')})()])

    def test_fake_produces_valid_normalized_entities_without_changing_core(self):
        registry=AdapterRegistry([SyntheticAdapter()])
        evidence=registry.select(['synthetic']).normalize({})
        validate_evidence(evidence)
        with tempfile.TemporaryDirectory() as tmp:
            write_evidence(evidence,tmp)
            payload=json.loads((Path(tmp)/'evidence/components.json').read_text())
        self.assertEqual(payload[0]['extensions'],{'synthetic':{'synthetic_fact':1}})
        self.assertEqual(payload[0]['provenance'][0]['source_id'],evidence.source_artifacts[0].id)

    def test_normalized_core_does_not_load_reference_implementation(self):
        code='import sys; import legacy_documenter.evidence.invariants; import legacy_documenter.evidence.persistence; import legacy_documenter.analysis.normalized_flow; import legacy_documenter.adapters.contracts; assert not any(x.startswith("legacy_documenter.adapters.vbnet_webforms_oracle") for x in sys.modules)'
        result=subprocess.run([sys.executable,'-c',code],cwd=ROOT,capture_output=True)
        self.assertEqual(result.returncode,0)

    def test_all_adapter_modules_import_without_cycles_and_no_runtime_tooling_dependency(self):
        import importlib
        for path in (PACKAGE/'adapters').rglob('*.py'):
            module='.'.join(path.relative_to(ROOT).with_suffix('').parts)
            importlib.import_module(module)
            tree=ast.parse(path.read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                if isinstance(node,ast.ImportFrom):
                    self.assertFalse(any(part in (node.module or '').split('.') for part in ['llm','knowledge','tests','tools']))
                if isinstance(node,ast.Constant) and isinstance(node.value,str) and len(node.value)<120:
                    self.assertFalse(any(word in node.value for word in ['PROJECT_STATE','AGENTS.md','copilot']))

    def test_architecture_neutral_modules_never_import_technology_or_compatibility(self):
        for name in ['bundle','entities','identity','reference','invariants','persistence']:
            tree=ast.parse((PACKAGE/'evidence'/f'{name}.py').read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                if isinstance(node,ast.ImportFrom):
                    module=node.module or ''
                    self.assertFalse(any(word in module for word in ['extractors','analysis','vbnet','builder','projection']),module)
        # The composition root is the one place allowed to wire an implementation.
        self.assertIn('ReferenceAdapter', (PACKAGE/'cli/pipeline_stages.py').read_text())

    def test_legacy_shims_are_only_reexports_and_identity_is_preserved(self):
        shims=[]
        for group in ['extractors','analysis','evidence']:
            for path in (PACKAGE/group).glob('*.py'):
                text=path.read_text(encoding='utf-8')
                if text.startswith('"""Legacy import compatibility:'):
                    shims.append(path)
                    tree=ast.parse(text)
                    self.assertTrue(all(isinstance(n,ast.ImportFrom) or isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant) for n in tree.body),path)
        self.assertEqual(len(shims),21)
        from legacy_documenter.extractors.database_extractor import DatabaseExtractor as old
        from legacy_documenter.adapters.vbnet_webforms_oracle.extractors.database_extractor import DatabaseExtractor as new
        self.assertIs(old,new)
        from legacy_documenter.evidence.builder import NormalizedEvidenceBuilder as compatible
        from legacy_documenter.adapters.vbnet_webforms_oracle.normalization import NormalizedEvidenceBuilder as canonical
        self.assertIs(compatible,canonical)

    def test_unknown_repository_fails_explicitly_without_inventing_reference_evidence(self):
        from legacy_documenter.cli.pipeline_stages import scan_repository,extract_repository
        with tempfile.TemporaryDirectory() as tmp:
            repo=Path(tmp);(repo/'sample.js').write_text('let x=1')
            scan=scan_repository(repo,None)
            with self.assertRaisesRegex(ValueError,'UNSUPPORTED_TECHNOLOGY'):
                extract_repository(scan.files,repo)

    def test_adapter_implementation_and_descriptor_are_fingerprinted(self):
        from tests.test_v5_3_r2_3_versioning_and_fingerprints import _copy_analyzer_tree
        with tempfile.TemporaryDirectory() as tmp:
            root=_copy_analyzer_tree(Path(tmp));before=analyzer_code_fingerprint(root).sha256
            path=root/'adapters/vbnet_webforms_oracle/adapter.py'
            original=path.read_bytes();path.write_bytes(original+b'\n# implementation changed\n')
            self.assertNotEqual(analyzer_code_fingerprint(root).sha256,before)
            path.write_bytes(original.replace(b'REFERENCE_ADAPTER_VERSION,',b'"2.0",'))
            self.assertNotEqual(analyzer_code_fingerprint(root).sha256,before)

    def test_cache_reuse_and_adapter_identity_version_isolation(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);repo=base/'repo';shutil.copytree(FIXTURE,repo);out=base/'out'
            self.assertEqual(run_full_pipeline(repo,out,None,12).status.value,'SUCCESS')
            context=build_context(repo,None,12);cache=out/'_cache_v53'
            self.assertTrue(validate_cache(cache,context).valid)
            self.assertEqual(run_full_pipeline(repo,out,None,12).status.value,'SUCCESS')
            metrics=json.loads((cache/'RUN_METRICS.json').read_text())
            self.assertGreater(metrics['extraction_cache']['extraction_cache_hits'],0)
            for identity in [('synthetic','1.0'),('synthetic','2.0')]:
                self.assertFalse(validate_cache(cache,build_context(repo,None,12,adapter_identity=identity)).valid)
            a=build_context(repo,None,12,adapter_identity=('synthetic','1.0'))
            b=build_context(repo,None,12,adapter_identity=('synthetic','2.0'))
            self.assertNotEqual(a.analysis_config_fingerprint,b.analysis_config_fingerprint)

    def test_reference_normalization_preserves_oracle_extensions_and_unresolved(self):
        # DB algorithms are covered by the existing database regression suite;
        # this test proves their adapter boundary retains vocabulary/provenance.
        indexes={'stored_procedures':[{'id':'SP-1','name':'PKG.PROC','confidence':'unresolved','provider':'Oracle',
                                     'evidence':[{'file':'sample.vb','line':3,'expression':'call'}]}]}
        evidence=ReferenceAdapter().normalize(indexes)
        entity=evidence.data_objects[0].to_dict()
        self.assertEqual(entity['state'],'unresolved')
        self.assertEqual(entity['extensions']['vbnet-webforms-oracle']['provider'],'Oracle')
        self.assertEqual(entity['provenance'][0]['line'],3)

    def test_neutral_flow_core_accepts_synthetic_facts_without_technology_keys(self):
        from legacy_documenter.analysis.normalized_flow import NormalizedFlowResolver
        entry={'id':'EP-synthetic','confidence':'confirmed','start_ref':'Owner.Start','method_key':('Owner','Start','synthetic'),
               'source_ref':'unit.synthetic','trigger_label':'invoke','handler_ref':'start',
               'initial_nodes':[{'id':'unit','type':'SyntheticUnit','label':'unit','project':'synthetic'}],'initial_edges':[]}
        flows,paths,summary,unresolved=NormalizedFlowResolver().resolve([entry],[],[],[],[],[])
        self.assertEqual(len(flows),1)
        self.assertEqual(flows[0]['source_ref'],'unit.synthetic')
        self.assertEqual(paths[0]['terminal_target'],'synthetic::Owner.Start')
        self.assertEqual(unresolved,[])
        for path in [PACKAGE/'analysis'/name for name in ['normalized_flow.py','_neutral_graph.py','_neutral_flow_keys.py','_neutral_flow_reporting.py']]:
            tree=ast.parse(path.read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                if isinstance(node,ast.ImportFrom): self.assertNotIn('adapters',node.module or '')
                if isinstance(node,ast.Constant) and isinstance(node.value,str) and len(node.value)<120:
                    self.assertFalse(any(word in node.value for word in ['WebForm','Oracle','vbproj','VB.NET']))


if __name__=='__main__': unittest.main()
