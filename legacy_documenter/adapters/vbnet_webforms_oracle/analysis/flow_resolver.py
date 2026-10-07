"""Reference adapter's legacy flow input/output projection.

Syntax-specific method keys, source labels and legacy reference identities
are prepared here. The neutral core traverses only those normalized facts.
"""
from legacy_documenter.analysis.normalized_flow import NormalizedFlowResolver
from ._flow_key_labels import method_key, entry_method_key, resolved_method_key
from legacy_documenter.analysis._neutral_graph import node


class FunctionalFlowResolver(NormalizedFlowResolver):
    def resolve(self, entry_points: list[dict], calls: list[dict], data_access: list[dict], stored_procedures: list[dict], sql_operations: list[dict], dependencies: list[dict], errors: list[dict] | None = None) -> tuple[list[dict], list[dict], dict, list[dict]]:
        entries=[]
        for entry in entry_points:
            start=entry_method_key(entry)
            event=f"{entry.get('webform')}::{entry.get('control') or '<page>'}.{entry.get('event')}"
            handler=f"handler::{entry.get('handler')}"
            start_label=self._method_label(start) if start else None
            entries.append({
                'id':entry.get('id'), 'confidence':entry.get('confidence'), 'start_ref':entry.get('handler_method'),
                'method_key':start, 'source_ref':entry.get('webform'), 'trigger_label':entry.get('event'), 'handler_ref':entry.get('handler'),
                'initial_nodes':[node('WebForm',entry.get('webform'),entry.get('webform')), node('Event',event,event), node('Handler',handler,entry.get('handler'))],
                'initial_edges':[{'source':source,'target':target,'type':kind,'confidence':entry.get('confidence'),'evidence_ref':entry.get('id')}
                                 for source,target,kind in [(entry.get('webform'),event,'WebForm -> Event'),(event,handler,'Event -> Handler'),(handler,start_label,'Handler -> Method')]],
            })
        normalized_calls=[]
        for group in calls:
            records=[]
            for call in group.get('calls',[]):
                records.append({
                    'owner_symbol':(call.get('containing_class') or '').lower(), 'owner_member':(call.get('containing_method') or '').lower(),
                    'confidence':call.get('confidence'), 'resolved_target':call.get('resolved_target'), 'resolved_project':call.get('resolved_project'),
                    'target_key':resolved_method_key(call), 'expression':call.get('expression'),
                    'call_reference':self._call_ref({**call,'file':group.get('file')}),
                })
            normalized_calls.append({'file':group.get('file'),'calls':records})
        operations=[{'owner_symbol':(op.get('class') or '').lower(), 'owner_member':(op.get('method') or '').lower(),
                     **{key:op[key] for key in ['id','project','stored_procedure','sql_operation','confidence'] if key in op}} for op in data_access]
        def terminals(records):
            return [{key:record[key] for key in ['id','name','operation','confidence'] if key in record} for record in records]
        links=[{key:record[key] for key in ['source','target','dependency_type'] if key in record} for record in dependencies]
        flows,paths,summary,unresolved=super().resolve(entries,normalized_calls,operations,terminals(stored_procedures),terminals(sql_operations),links,errors)
        aliases={'source_ref':'webform','trigger_label':'event','handler_ref':'handler','start_ref':'start_method'}
        return [{aliases.get(key,key):value for key,value in flow.items()} for flow in flows],paths,summary,unresolved

    def _entry_method_key(self, entry):
        return entry.get('method_key') if 'method_key' in entry else entry_method_key(entry)

    def _resolved_method_key(self, call):
        return call.get('target_key') if 'target_key' in call else resolved_method_key(call)

    def _method_key(self, symbol, member, project):
        return method_key(symbol,member,project)

    def _call_ref(self, call):
        if 'call_reference' in call:
            return call['call_reference']
        evidence=call.get('evidence') or {}
        return self._stable_id('CALL',call.get('file'),evidence.get('line'),call.get('expression'),call.get('resolved_target'))
