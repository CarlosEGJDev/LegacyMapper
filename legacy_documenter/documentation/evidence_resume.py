import json
from legacy_documenter.documentation.resume import run
if __name__=="__main__": print(json.dumps(run(evidence_constrained=True,status_prefix="V3-R7_2_3"),ensure_ascii=False,sort_keys=True,indent=2))
