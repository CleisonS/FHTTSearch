from __future__ import annotations
from app.models.control_info import ControlInfo
from app.models.readiness_result import ReadinessItem, ReadinessResult
from app.constants import READINESS_COLUMNS
class ReadinessAnalyzer:
    def _hay(self,c): return f"{c.name} {c.text} {c.control_type} {c.class_name} {c.automation_id}".lower()
    def _item(self,c,score,notes): return ReadinessItem(True,c.backend,c.control_type,c.class_name,c.automation_id,c.handle,c.rectangle,score,notes,{"supports_focus": bool(c.keyboard_focusable), "visible": c.visible, "enabled": c.enabled, "children_count": c.children_count})
    def analyze(self, controls: list[ControlInfo])->ReadinessResult:
        r=ReadinessResult(); flat=controls[:]
        for c in flat:
            h=self._hay(c)
            if not r.search_field.detected and ('search' in h or ('edit' in h and c.keyboard_focusable)): r.search_field=self._item(c,85 if 'search' in h else 55,["Campo candidato para Search"])
            if not r.onu_table.detected and (('onu list' in h and c.control_type.lower() in ('table','datagrid','list','pane')) or c.control_type.lower() in ('table','datagrid')): r.onu_table=self._item(c,80,["Tabela/lista candidata para ONU List"])
            if not r.device_tree.detected and ('device tree' in h or 'main topology' in h or c.control_type.lower()=='tree'): r.device_tree=self._item(c,80,["Árvore candidata detectada"])
            if not r.onu_list_tab.detected and ('onu list' in h and ('tab' in c.control_type.lower() or 'page' in c.control_type.lower())): r.onu_list_tab=self._item(c,75,["Aba ONU List candidata"])
            for col in READINESS_COLUMNS:
                if col.lower() in h and col not in r.columns: r.columns[col]=self._item(c,90,[f"Coluna {col} detectada"])
        score=sum([r.search_field.confidence_score,r.onu_table.confidence_score,r.device_tree.confidence_score,r.onu_list_tab.confidence_score])//4 + min(20,len(r.columns)*2)
        r.confidence_score=min(100,score)
        r.classification='EXCELLENT' if r.confidence_score>=85 else 'GOOD' if r.confidence_score>=65 else 'PARTIAL' if r.confidence_score>=35 else 'POOR' if flat else 'UNKNOWN'
        r.recommendation='Direct control automation' if r.classification in ('EXCELLENT','GOOD') else 'Hybrid control and keyboard automation' if r.classification=='PARTIAL' else 'Insufficient information'
        r.notes.append(f"{len(r.columns)} colunas prioritárias detectadas."); return r
