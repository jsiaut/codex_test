"""Preserve inadvertently over-read body rows while excluding first-pass use."""
import json
from datetime import datetime, timezone
from pathlib import Path

selected = [
    ('5111b0a3f21ea4d0c6706546970e050895c74f90c67e4d4e72b9228026c1805f','META','0001193125-26-204128',2059,239241,'All five body packets read; article2 confines new series; DTC explicitly in article2 and forms. No Item3.03.'),
    ('83d3b91e011cd2ad2c05b4f972fa8655636b9d273fd8e90c7f6cce6d8f9d86b3','MRVL','0001193125-26-157134',2343,201997,'All four body packets read; financial DTC/Cede global holder explicit. No Item3.03.'),
    ('285affe4f734d81b51b903ebcb5a35c4ba9993dfc63cb64657bb79944c53252b','CRWV','0001769628-26-000183',13017,35917,'Complete one body packet read; additional notes form same class as April14 original; original bf49c72b financial registered DTC holder and11 financial initialpurchasers explicitly proved. Actual body3.1 clause change observed but no Item3.03, so excluded from firstpass F4 by fixed11.1rule.'),
]
p=Path('work/observation_quarantines.json')
rows=json.loads(p.read_text())
added=0
overrides=[]
for key,group,acc,start,end,detail in selected:
    for row in [json.loads(x) for x in (Path('work/observations')/(key+'.jsonl')).read_text().splitlines()]:
        if row['record_kind']!='observation' or row.get('abstained'):
            continue
        if any(x['observation_id']==row['observation_id'] for x in rows):
            raise ValueError('D89 already applied')
        rows.append(dict(observation_id=row['observation_id'],reason='financial_parties_only',scope='all_derived_measures_links_and_events',decision='D89',detail='Body outside authorized first-pass exception under11.1; preserve immutable accepted RAW observation but exclude amounts, relations, events and all downstream use. '+detail))
        added+=1
    overrides.append(dict(content_key=key,group=group,accession=acc,reason='financial_parties_only',raw_byte_start=start,raw_byte_end=end,decision='D89',body_personally_read=True,detail=detail))
p.write_text(json.dumps(rows,indent=2)+'\n')
Path('work/exhibit_body_policy_overrides.json').write_text(json.dumps(overrides,indent=2)+'\n')
with Path('decisions.md').open('a') as f:
    f.write('\nD89 — Correction de périmètre, sans réessai sémantique : les corps de trois Supplemental Indenture (Meta 4 mai2026 EX4.1, Marvell 15 avril2026 EX4.1, CoreWeave 21 avril2026 EX4.1) ont été lus intégralement à tort, bien que leurs 8-K ne portent pas Item3.03 et que la preuve de porteurs financiers soit établie. §11.1 limite explicitement l’exception d’amendement autonome EX4 à Item3.03. Les douze observations non abstention soumises sont conservées immuables mais placées en quarantaine de TOUT usage dérivé, y compris F4 CoreWeave et relations/garanties. Les lectures réelles restent journalisées ; aucune couverture comptable exploitée ne provient des corps. Les plages brutes exactes vont dans financial_parties_only via work/exhibit_body_policy_overrides.json en phase3. Les observations admissibles déjà faites dans les Items1.01/8.01 indépendants ne sont pas modifiées. Pas d’extension §14 ni changement E/F, ni effacement des propositions, rejets ou passes.\n')
with Path('journal.jsonl').open('a') as f:
    f.write(json.dumps(dict(as_of=json.loads(Path('work/run.json').read_text())['as_of'],timestamp=datetime.now(timezone.utc).isoformat(),event='first_pass_body_scope_correction',decision='D89',quarantined_observations=added,body_exclusions=len(overrides),final_delivery=False))+'\n')
print({'decision':'D89','quarantined_observations':added,'body_exclusions':len(overrides)})
