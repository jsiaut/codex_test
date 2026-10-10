# Fragilité financière et relations documentées

Situation des sources arrêtée au 2026-10-09T10:24:21.129672+00:00. Périmètre : extension des cinq familles de notes autorisée ; découverte non ouverte.

Les critères E, la liste F et les seuils n’ont pas changé. Commit d’origine : `d9e886e92fe46c2bd3f2f497103dce895be8edd2` ; commit courant de config.yaml : `e59807676c027121710f9469f8e1c976e40ce3a6`. Le manifeste et les annexes du dossier d’audit portent les empreintes et l’horodatage de la première requête.

Les pièces déposées ne permettent pas de discriminer entre les deux lectures. La part indéterminée des issues de paire E1 et E2 au point de tête vaut 1 ; le périmètre borné et les numérateurs non attribuables en sont les premières limites. Cette proportion porte sur les paires publiées dans le registre, sans pondérer les montants. Les échéances non établies restent explicitement indéterminées. La sensibilité revised et les autres points de grille sont publiés dans les tables.

Aucun arrêt durable d’accès SEC ni échec comptable généralisé. Les échecs et conflits locaux restent exclus. L’audit indépendant n’a pas été effectué, conformément à la demande de travailler sans sous-agent ; le dossier permet de le faire ultérieurement.

## Contrôles

| Contrôle | ok | mismatch | not_testable | tautological |
| --- | ---: | ---: | ---: | ---: |
| c10_maturity_sums | 419 | 0 | 24 | 0 |
| c11_segments | 312 | 0 | 83 | 0 |
| c12_revenue_disaggregation | 721 | 0 | 620 | 0 |
| c13_rpo | 218 | 0 | 0 | 0 |
| c14_eps_scale | 402 | 9 | 108 | 0 |
| c15_tax_rate | 154 | 13 | 130 | 0 |
| c16_concentration | 1801 | 0 | 6 | 0 |
| c1_balance_components | 1610 | 1 | 93 | 0 |
| c2_cash_flow_components | 1554 | 2 | 28 | 0 |
| c3_cash_reconciliation | 34 | 0 | 350 | 0 |
| c4_restatement_detection | 137268 | 0 | 13 | 0 |
| c5_bilateral | 0 | 0 | 794 | 0 |
| c6_income_articulation | 242 | 0 | 0 | 0 |
| c7_cash_continuity | 289 | 1 | 26 | 0 |
| c8_debt_rollforward | 0 | 0 | 258 | 0 |
| c9_lease_liability | 169 | 0 | 168 | 0 |

Les écarts sont conservés avec leurs deux termes, leur précision et leur explication. Un contrôle non testable ne devient pas un succès.

## Événements

| Groupe | Période | Observable | Public le | Pièce et emplacement |
| --- | --- | --- | --- | --- |
| AMD | 2021-03-27 | F6 | 2021-04-28 | 0000002488-21-000056 / rawbytes:544386:566469 |
| AMD | 2023-04-01 | F8 | 2023-05-03 | 0000002488-22-000170 / id:id3VybDovL2RvY3MudjEvZG9jOmMxNTc1ZjJkY2FjNjQ4OGM4ZmYyZThlOWRjZDk1ZTkyL3NlYzpjMTU3NWYyZGNhYzY0ODhjOGZmMmU4ZTlkY2Q5NWU5Ml8xNi9mcmFnOmQ0OWNmOTg0ODhhYjQ1NmE4ZjVlNWJkYWZiNDc5NDI5L3RhYmxlOjNhNmQ0OTZhNDZlMDQ4NTg5YzI2NTk3N2I1OGQxMTZhL3RhYmxlcmFuZ2U6M2E2ZDQ5NmE0NmUwNDg1ODljMjY1OTc3YjU4ZDExNmFfMy01LTEtMS05NjM2OQ_47295347-51fb-4cbe-bd87-c7dc80c77fda; 0000002488-22-000170 / id:id3VybDovL2RvY3MudjEvZG9jOmMxNTc1ZjJkY2FjNjQ4OGM4ZmYyZThlOWRjZDk1ZTkyL3NlYzpjMTU3NWYyZGNhYzY0ODhjOGZmMmU4ZTlkY2Q5NWU5Ml8xNi9mcmFnOmQ0OWNmOTg0ODhhYjQ1NmE4ZjVlNWJkYWZiNDc5NDI5L3RhYmxlOjNhNmQ0OTZhNDZlMDQ4NTg5YzI2NTk3N2I1OGQxMTZhL3RhYmxlcmFuZ2U6M2E2ZDQ5NmE0NmUwNDg1ODljMjY1OTc3YjU4ZDExNmFfMy03LTEtMS05NjM2OQ_9339961f-1291-4c19-ac01-07e80527e361; 0000002488-23-000047 / id:id3VybDovL2RvY3MudjEvZG9jOjE3OWYwZDY3NzljMjQ3OTRhNjc2ODE3NTVmZmI5YTA0L3NlYzoxNzlmMGQ2Nzc5YzI0Nzk0YTY3NjgxNzU1ZmZiOWEwNF8xMDYvZnJhZzoyZTYwYjFmOGUwMjA0MjNhOWVlNDI5NzM4ODdmYTBhZC90YWJsZTplNWJiZTQzOGMxZjI0OTllYjBjODI4ZTBiMDdkZmQ4ZC90YWJsZXJhbmdlOmU1YmJlNDM4YzFmMjQ5OWViMGM4MjhlMGIwN2RmZDhkXzMtMS0xLTEtMTA2NzA3_df1970d8-71da-454d-88fd-d793425d8434; 0000002488-23-000047 / id:id3VybDovL2RvY3MudjEvZG9jOjE3OWYwZDY3NzljMjQ3OTRhNjc2ODE3NTVmZmI5YTA0L3NlYzoxNzlmMGQ2Nzc5YzI0Nzk0YTY3NjgxNzU1ZmZiOWEwNF8xMDYvZnJhZzoyZTYwYjFmOGUwMjA0MjNhOWVlNDI5NzM4ODdmYTBhZC90YWJsZTplNWJiZTQzOGMxZjI0OTllYjBjODI4ZTBiMDdkZmQ4ZC90YWJsZXJhbmdlOmU1YmJlNDM4YzFmMjQ5OWViMGM4MjhlMGIwN2RmZDhkXzMtMy0xLTEtMTA2NzA3_4e247c3c-8880-46c4-b12c-268740bfccb1; 0000002488-23-000076 / id:id3VybDovL2RvY3MudjEvZG9jOmFmNTRlZWM4OGY5NTQ1NDRhNWRmZmU4ZmMzYjVjMzQyL3NlYzphZjU0ZWVjODhmOTU0NTQ0YTVkZmZlOGZjM2I1YzM0Ml8xNi9mcmFnOjI1MGZiYmVlOGU2MzQ4MTc4Mzg5Mjk5ZGMwYjE1YmM0L3RhYmxlOjM3MjFhMWI0MzkxZjQyOGU4YTAxNDMyYjNmNzEwYzZiL3RhYmxlcmFuZ2U6MzcyMWExYjQzOTFmNDI4ZThhMDE0MzJiM2Y3MTBjNmJfMy01LTEtMS0xMzQ4Nzg_a87d4bd1-cb98-4201-b310-260f71cad45c; 0000002488-23-000076 / id:id3VybDovL2RvY3MudjEvZG9jOmFmNTRlZWM4OGY5NTQ1NDRhNWRmZmU4ZmMzYjVjMzQyL3NlYzphZjU0ZWVjODhmOTU0NTQ0YTVkZmZlOGZjM2I1YzM0Ml8xNi9mcmFnOjI1MGZiYmVlOGU2MzQ4MTc4Mzg5Mjk5ZGMwYjE1YmM0L3RhYmxlOjM3MjFhMWI0MzkxZjQyOGU4YTAxNDMyYjNmNzEwYzZiL3RhYmxlcmFuZ2U6MzcyMWExYjQzOTFmNDI4ZThhMDE0MzJiM2Y3MTBjNmJfMy03LTEtMS0xMzQ4Nzg_4df54762-8d8f-453a-8db9-dd793877e5fb |
| AMD | 2025-12-27 | F4 | 2025-11-05 | 0000002488-25-000166 / rawbytes:691282:698556 |
| AMZN | 2025-03-31 | F7 | 2025-05-02 | 0001018724-25-000004 / rawbytes:957120:1115856; 0001018724-25-000036 / rawbytes:351450:421537 |
| AMZN | 2025-06-30 | F4 | 2025-08-01 | 0001018724-25-000036 / rawbytes:606715:651476; 0001018724-25-000086 / rawbytes:732062:776209 |
| AVGO | 2025-02-02 | F4 | 2025-03-12 | 0001730168-25-000021 / rawbytes:643826:839942 |
| AVGO | 2025-05-04 | F4 | 2025-06-11 | 0001730168-25-000064 / rawbytes:837300:1038993 |
| AVGO | 2025-08-03 | F4 | 2025-06-11 | 0001730168-25-000064 / rawbytes:837300:1038993 |
| CRWV | 2024-06-30 | F4 | 2025-03-31 | 0001193125-25-067651 / rawbytes:3163793:3264931 |
| CRWV | 2024-09-30 | F1 | 2025-11-13 | 0001769628-25-000014 / id:f-319; 0001769628-25-000014 / id:f-321; 0001769628-25-000041 / id:f-439; 0001769628-25-000041 / id:f-441; 0001769628-25-000062 / id:f-499; 0001769628-25-000062 / id:f-501 |
| CRWV | 2025-03-31 | F5 | 2025-05-15 | 0001769628-25-000014 / rawbytes:1194195:1205700 |
| CRWV | 2025-06-30 | F4 | 2025-08-13 | 0001769628-25-000003 / rawbytes:0:681792; 0001769628-25-000003 / rawbytes:19705:21884; 0001769628-25-000014 / rawbytes:740349:826307; 0001769628-25-000041 / rawbytes:1056938:1166798 |
| CRWV | 2025-06-30 | F5 | 2025-08-13 | 0001769628-25-000041 / rawbytes:1666126:1677948 |
| CRWV | 2025-09-30 | F4 | 2025-11-13 | 0001193125-25-227562 / rawbytes:0:1327158; 0001193125-25-227562 / rawbytes:18513:23044; 0001769628-25-000041 / rawbytes:1378927:1386661; 0001769628-25-000062 / rawbytes:1224886:1354216 |
| CRWV | 2025-09-30 | F5 | 2025-11-13 | 0001769628-25-000062 / rawbytes:1851252:1862723 |
| CRWV | 2025-12-31 | F4 | 2026-01-02 | 0001769628-25-000062 / rawbytes:1562018:1566363; 0001769628-26-000003 / rawbytes:19452:26555 |
| CRWV | 2025-12-31 | F5 | 2026-03-02 | 0001769628-26-000104 / rawbytes:2548865:2560671 |
| CRWV | 2026-03-31 | F5 | 2026-05-08 | 0001769628-26-000222 / rawbytes:1215447:1227705 |
| CRWV | 2026-06-30 | F1 | 2026-08-12 | 0001769628-26-000222 / id:f-284; 0001769628-26-000222 / id:f-286; 0001769628-26-000366 / id:f-391; 0001769628-26-000366 / id:f-393 |
| CRWV | 2026-06-30 | F5 | 2026-08-12 | 0001769628-26-000366 / rawbytes:1650655:1663659 |
| GOOGL | 2025-06-30 | F4 | 2025-04-25 | 0001652044-25-000043 / rawbytes:930653:958135 |
| META | 2021-03-31 | F6 | 2021-04-29 | 0001326801-21-000033 / rawbytes:645574:653257 |
| META | 2022-06-30 | F8 | 2022-07-28 | 0001326801-22-000057 / id:id3VybDovL2RvY3MudjEvZG9jOmVhNzBlMzI4Y2FhOTRjZWZiNzZhOWRiNmVkNjMzOGZjL3NlYzplYTcwZTMyOGNhYTk0Y2VmYjc2YTlkYjZlZDYzMzhmY18yNS9mcmFnOmM2NzVlNjBmOGIwODQ2MjhhY2Q2YWI4NmVlNzQ2NmE3L3RhYmxlOmFiNTBkOWEwYjliNzRjOGE4NzA3MTQwMzUzZGE3OTY5L3RhYmxlcmFuZ2U6YWI1MGQ5YTBiOWI3NGM4YTg3MDcxNDAzNTNkYTc5NjlfMi0xLTEtMS04NzE4OA_f0bcae23-6f1f-485d-9e29-4632de8a5241; 0001326801-22-000057 / id:id3VybDovL2RvY3MudjEvZG9jOmVhNzBlMzI4Y2FhOTRjZWZiNzZhOWRiNmVkNjMzOGZjL3NlYzplYTcwZTMyOGNhYTk0Y2VmYjc2YTlkYjZlZDYzMzhmY18yNS9mcmFnOmM2NzVlNjBmOGIwODQ2MjhhY2Q2YWI4NmVlNzQ2NmE3L3RhYmxlOmFiNTBkOWEwYjliNzRjOGE4NzA3MTQwMzUzZGE3OTY5L3RhYmxlcmFuZ2U6YWI1MGQ5YTBiOWI3NGM4YTg3MDcxNDAzNTNkYTc5NjlfMi0zLTEtMS04NzE4OA_0a8b54ca-3d2d-46e1-8415-94395d8410ed; 0001326801-22-000082 / id:id3VybDovL2RvY3MudjEvZG9jOmFlYjk3Y2MwNzA5ZTRmODA4Y2Y3YzZkOWFlNWRmMDMyL3NlYzphZWI5N2NjMDcwOWU0ZjgwOGNmN2M2ZDlhZTVkZjAzMl8yNS9mcmFnOjBjNzMzY2JhMWVhZTQyYzg5NjQ0ZTM2MDU1ZjQ3OWFmL3RhYmxlOjZjNzA0NmQyMzEwZjQ5Yzg4MWQ1NmQwMDhiZDBmNWUwL3RhYmxlcmFuZ2U6NmM3MDQ2ZDIzMTBmNDljODgxZDU2ZDAwOGJkMGY1ZTBfMi0xLTEtMS0xMzAwMjI_8e548d71-e413-4e13-b245-9d598f63db88; 0001326801-22-000082 / id:id3VybDovL2RvY3MudjEvZG9jOmFlYjk3Y2MwNzA5ZTRmODA4Y2Y3YzZkOWFlNWRmMDMyL3NlYzphZWI5N2NjMDcwOWU0ZjgwOGNmN2M2ZDlhZTVkZjAzMl8yNS9mcmFnOjBjNzMzY2JhMWVhZTQyYzg5NjQ0ZTM2MDU1ZjQ3OWFmL3RhYmxlOjZjNzA0NmQyMzEwZjQ5Yzg4MWQ1NmQwMDhiZDBmNWUwL3RhYmxlcmFuZ2U6NmM3MDQ2ZDIzMTBmNDljODgxZDU2ZDAwOGJkMGY1ZTBfMi0zLTEtMS0xMzAwMjI_175fbb34-909c-4606-b5be-7c722a77ae1c |
| MRVL | 2021-01-30 | F4 | 2020-12-08 | 0001193125-20-312706 / rawbytes:0:622898; 0001193125-20-312706 / rawbytes:18096:39686 |
| MRVL | 2021-05-01 | F4 | 2021-04-21 | 0001193125-21-120469 / rawbytes:0:29807; 0001193125-21-120469 / rawbytes:18251:21826; 0001193125-21-123305 / rawbytes:0:112170; 0001193125-21-123305 / rawbytes:0:27983; 0001193125-21-123305 / rawbytes:0:27987; 0001193125-21-123305 / rawbytes:25743:30475 |
| MRVL | 2023-04-29 | F4 | 2023-05-26 | 0001193125-23-103639 / rawbytes:0:54073; 0001193125-23-103639 / rawbytes:17890:26902; 0001835632-23-000029 / rawbytes:677910:798950 |
| MRVL | 2023-04-29 | F8 | 2023-05-26 | 0001835632-22-000053 / id:id3VybDovL2RvY3MudjEvZG9jOjNlYTFkZjhiOTExMzRmM2E4Nzc2YmUzYjAwM2M4OGE1L3NlYzozZWExZGY4YjkxMTM0ZjNhODc3NmJlM2IwMDNjODhhNV8xOS9mcmFnOjhlNWNkZjNkODhiYTRmZTM5NGE2ZmQ5NGIwOWZhZTE4L3RhYmxlOjEyMWU2MDM4ODY3MTQ1YmI4Yzc0MTg3MTg5Mzc0ZTExL3RhYmxlcmFuZ2U6MTIxZTYwMzg4NjcxNDViYjhjNzQxODcxODkzNzRlMTFfMi01LTEtMS0xMTg3MjA_d53735cc-d961-460f-8580-76c8a68737f4; 0001835632-22-000053 / id:id3VybDovL2RvY3MudjEvZG9jOjNlYTFkZjhiOTExMzRmM2E4Nzc2YmUzYjAwM2M4OGE1L3NlYzozZWExZGY4YjkxMTM0ZjNhODc3NmJlM2IwMDNjODhhNV8xOS9mcmFnOjhlNWNkZjNkODhiYTRmZTM5NGE2ZmQ5NGIwOWZhZTE4L3RhYmxlOjEyMWU2MDM4ODY3MTQ1YmI4Yzc0MTg3MTg5Mzc0ZTExL3RhYmxlcmFuZ2U6MTIxZTYwMzg4NjcxNDViYjhjNzQxODcxODkzNzRlMTFfMi03LTEtMS0xMTg3MjA_f95e186a-8285-473b-82a4-6df18c20bce9; 0001835632-23-000013 / id:id3VybDovL2RvY3MudjEvZG9jOjQxZDk2YzJlZDUxZDQwZTc5YmZlYmI5YTZiZDU0NjJmL3NlYzo0MWQ5NmMyZWQ1MWQ0MGU3OWJmZWJiOWE2YmQ1NDYyZl83MC9mcmFnOjZkMWZlNmU3NjVmMTQ2NmZhOTk2ZDYwOGM5YTExNGE0L3RhYmxlOjM2MzIwZjZjMTU3MzQ4YzY5NDhlMzFiNTBmODdlYTliL3RhYmxlcmFuZ2U6MzYzMjBmNmMxNTczNDhjNjk0OGUzMWI1MGY4N2VhOWJfMi0xLTEtMS0xMzA5MzA_827157f2-2a02-4fd0-adf7-f668e37ca21b; 0001835632-23-000013 / id:id3VybDovL2RvY3MudjEvZG9jOjQxZDk2YzJlZDUxZDQwZTc5YmZlYmI5YTZiZDU0NjJmL3NlYzo0MWQ5NmMyZWQ1MWQ0MGU3OWJmZWJiOWE2YmQ1NDYyZl83MC9mcmFnOjZkMWZlNmU3NjVmMTQ2NmZhOTk2ZDYwOGM5YTExNGE0L3RhYmxlOjM2MzIwZjZjMTU3MzQ4YzY5NDhlMzFiNTBmODdlYTliL3RhYmxlcmFuZ2U6MzYzMjBmNmMxNTczNDhjNjk0OGUzMWI1MGY4N2VhOWJfMi0zLTEtMS0xMzA5MzA_417a1f5b-29ad-4e73-ba60-28ba0ce0a129; 0001835632-23-000029 / id:id3VybDovL2RvY3MudjEvZG9jOjZiYTRiYzNlN2MzNjQ5MmU4NzhlMWM5NDUwYWM3YjRhL3NlYzo2YmE0YmMzZTdjMzY0OTJlODc4ZTFjOTQ1MGFjN2I0YV8xOS9mcmFnOmI0NmU5OWEzNTQ0NDQwNmQ5YThhM2I3MWFhOWIwZWI5L3RhYmxlOjM1MWE1NDhhZGU1OTQ3MGNhMjMzMTIxNjQ4ODQ1NTk5L3RhYmxlcmFuZ2U6MzUxYTU0OGFkZTU5NDcwY2EyMzMxMjE2NDg4NDU1OTlfMi0xLTEtMS0xNjI3Nzg_aabebe00-ae57-411a-865e-1a61f1f5111b; 0001835632-23-000029 / id:id3VybDovL2RvY3MudjEvZG9jOjZiYTRiYzNlN2MzNjQ5MmU4NzhlMWM5NDUwYWM3YjRhL3NlYzo2YmE0YmMzZTdjMzY0OTJlODc4ZTFjOTQ1MGFjN2I0YV8xOS9mcmFnOmI0NmU5OWEzNTQ0NDQwNmQ5YThhM2I3MWFhOWIwZWI5L3RhYmxlOjM1MWE1NDhhZGU1OTQ3MGNhMjMzMTIxNjQ4ODQ1NTk5L3RhYmxlcmFuZ2U6MzUxYTU0OGFkZTU5NDcwY2EyMzMxMjE2NDg4NDU1OTlfMi0zLTEtMS0xNjI3Nzg_f41a486e-078d-44c5-aaf7-b0811fcbcac1 |
| MRVL | 2024-05-04 | F8 | 2024-05-31 | 0001835632-23-000046 / id:f-86; 0001835632-23-000046 / id:f-87; 0001835632-24-000009 / id:f-110; 0001835632-24-000009 / id:f-111; 0001835632-24-000063 / id:f-84; 0001835632-24-000063 / id:f-85 |
| MRVL | 2025-08-02 | F4 | 2025-08-29 | 0001193125-25-152676 / rawbytes:18152:29299; 0001835632-25-000189 / rawbytes:810257:868670 |
| MSFT | 2023-12-31 | F4 | 2023-11-06 | 0001193125-23-271376 / rawbytes:22184:46658 |
| NVDA | 2022-10-30 | F8 | 2022-11-18 | 0001045810-22-000147 / id:id3VybDovL2RvY3MudjEvZG9jOmRkZmY1OTljNjg0YzQ1Mzk5MmM3ZDExYmQxNGNhYTE0L3NlYzpkZGZmNTk5YzY4NGM0NTM5OTJjN2QxMWJkMTRjYWExNF8xNi9mcmFnOjFiZjdiNjZkMzA5OTQ5ZjlhMjhhYmZiMzc1ZWM5ZjUwL3RhYmxlOjNhMmIyZjg1MDQzNTQ5Y2E5MmE4NGZmMGM1Mjc4M2ZlL3RhYmxlcmFuZ2U6M2EyYjJmODUwNDM1NDljYTkyYTg0ZmYwYzUyNzgzZmVfNC0xLTEtMS00NjI0NQ_c156e4f1-1d66-4ed4-b99a-78135257b604; 0001045810-22-000147 / id:id3VybDovL2RvY3MudjEvZG9jOmRkZmY1OTljNjg0YzQ1Mzk5MmM3ZDExYmQxNGNhYTE0L3NlYzpkZGZmNTk5YzY4NGM0NTM5OTJjN2QxMWJkMTRjYWExNF8xNi9mcmFnOjFiZjdiNjZkMzA5OTQ5ZjlhMjhhYmZiMzc1ZWM5ZjUwL3RhYmxlOjNhMmIyZjg1MDQzNTQ5Y2E5MmE4NGZmMGM1Mjc4M2ZlL3RhYmxlcmFuZ2U6M2EyYjJmODUwNDM1NDljYTkyYTg0ZmYwYzUyNzgzZmVfNC0zLTEtMS00NjI0NQ_1a4b021a-bc2a-43a3-b3c4-b693fcaff7e0; 0001045810-22-000166 / id:id3VybDovL2RvY3MudjEvZG9jOjZiY2I3YjY4MWM5MTQ5YTdiZDA5ZDBkZjFmYzdjMTAzL3NlYzo2YmNiN2I2ODFjOTE0OWE3YmQwOWQwZGYxZmM3YzEwM18xNi9mcmFnOjJmNTY5NGQxZTJlMTQ1ZTdiOTk1NTI1N2ZmMjhlYzE4L3RhYmxlOjEwMTdiOWRhNzY3MjQ2Yjk5OGY3NTU5ODZkNzczNmY3L3RhYmxlcmFuZ2U6MTAxN2I5ZGE3NjcyNDZiOTk4Zjc1NTk4NmQ3NzM2ZjdfNC0xLTEtMS01ODM2OA_fc22bbbd-34a5-418c-aab4-ffccb106b453; 0001045810-22-000166 / id:id3VybDovL2RvY3MudjEvZG9jOjZiY2I3YjY4MWM5MTQ5YTdiZDA5ZDBkZjFmYzdjMTAzL3NlYzo2YmNiN2I2ODFjOTE0OWE3YmQwOWQwZGYxZmM3YzEwM18xNi9mcmFnOjJmNTY5NGQxZTJlMTQ1ZTdiOTk1NTI1N2ZmMjhlYzE4L3RhYmxlOjEwMTdiOWRhNzY3MjQ2Yjk5OGY3NTU5ODZkNzczNmY3L3RhYmxlcmFuZ2U6MTAxN2I5ZGE3NjcyNDZiOTk4Zjc1NTk4NmQ3NzM2ZjdfNC0zLTEtMS01ODM2OA_f72b2f82-4a69-4748-9571-fc77f7eee237 |
| ORCL | 2025-08-31 | F1 | 2025-09-10 | 0000950170-25-037143 / id:F_64e5d859-9974-440e-af0e-3de2bb500b03; 0000950170-25-037143 / id:F_9ebd7c76-1252-4f79-9a71-572d5e95347a; 0000950170-25-087926 / id:F_48c0aad1-cca5-4212-9754-212572b35a2b; 0000950170-25-087926 / id:F_abeb0a35-0921-404c-ad73-b5f69c7497c6; 0001193125-25-200095 / id:F_09ef0b4b-3eaa-4f20-9f9f-72bb5414a514; 0001193125-25-200095 / id:F_c7ea67e4-4662-438e-9c0d-3c941b8b7cce |
| ORCL | 2025-11-30 | F1 | 2025-12-11 | 0001193125-25-200095 / id:F_09ef0b4b-3eaa-4f20-9f9f-72bb5414a514; 0001193125-25-200095 / id:F_c7ea67e4-4662-438e-9c0d-3c941b8b7cce; 0001193125-25-315925 / id:F_14bf7e1c-67e4-4116-808e-a43e59764405; 0001193125-25-315925 / id:F_d8f17dc4-4aaa-4810-a066-7854af542813 |
| ORCL | 2026-02-28 | F1 | 2026-03-11 | 0001193125-25-200095 / id:F_09ef0b4b-3eaa-4f20-9f9f-72bb5414a514; 0001193125-25-200095 / id:F_c7ea67e4-4662-438e-9c0d-3c941b8b7cce; 0001193125-25-315925 / id:F_14bf7e1c-67e4-4116-808e-a43e59764405; 0001193125-25-315925 / id:F_d8f17dc4-4aaa-4810-a066-7854af542813; 0001193125-26-101045 / id:F_5a3d4971-c81e-4883-a5c6-5b467c5fa113; 0001193125-26-101045 / id:F_e991ec1c-69a6-470e-bedb-9b2cd24f36d7 |
| ORCL | 2026-05-31 | F1 | 2026-06-22 | 0001193125-25-315925 / id:F_14bf7e1c-67e4-4116-808e-a43e59764405; 0001193125-25-315925 / id:F_d8f17dc4-4aaa-4810-a066-7854af542813; 0001193125-26-101045 / id:F_5a3d4971-c81e-4883-a5c6-5b467c5fa113; 0001193125-26-101045 / id:F_e991ec1c-69a6-470e-bedb-9b2cd24f36d7; 0001193125-26-277521 / id:F_cb073321-3d77-4861-8d30-be6b36c0451e; 0001193125-26-277521 / id:F_ea4be9ee-f076-44be-9d35-14b1681ecadc |
| ORCL | 2026-08-31 | F1 | 2026-09-11 | 0001193125-26-101045 / id:F_5a3d4971-c81e-4883-a5c6-5b467c5fa113; 0001193125-26-101045 / id:F_e991ec1c-69a6-470e-bedb-9b2cd24f36d7; 0001193125-26-277521 / id:F_cb073321-3d77-4861-8d30-be6b36c0451e; 0001193125-26-277521 / id:F_ea4be9ee-f076-44be-9d35-14b1681ecadc; 0001193125-26-389274 / id:F_20139350-41b2-4695-a0cd-cc401a11f57e; 0001193125-26-389274 / id:F_6b02eddf-d360-4c8a-bcc1-e8b94789e26d |

## Fragilité par groupe

### AMD

Dernière période de revenu exploitable : 2024-12-28. Les séries complètes sont dans series.csv ; les périodes fiscales et dates de publicité y sont distinctes.

| Mesure | Terme / variante | Valeur | Unité | Statut / motif | Source |

| --- | --- | ---: | --- | --- | --- |

| revenue_total | none / original | 7658000000.000000 | http://www.xbrl.org/2003/iso4217:USD | computed / — | 0000002488-24-000163 / id:f-32; 0000002488-25-000012 / id:f-40 |

| revenue_growth | ttm / original | 0.136905 | ratio | computed / — | 0000002488-24-000056 / id:f-30; 0000002488-24-000056 / id:f-31; 0000002488-24-000123 / id:f-30; 0000002488-24-000123 / id:f-31; 0000002488-24-000163 / id:f-30; 0000002488-24-000163 / id:f-31; 0000002488-24-000163 / id:f-32; 0000002488-24-000163 / id:f-33; 0000002488-25-000012 / id:f-40; 0000002488-25-000012 / id:f-41 |

| revenue_growth | yoy / original | 0.241569 | ratio | computed / — | 0000002488-24-000163 / id:f-32; 0000002488-24-000163 / id:f-33; 0000002488-25-000012 / id:f-40; 0000002488-25-000012 / id:f-41 |

| capex_to_cfo | with / original | ND | — | not_determinable / missing_admissible_terms | — |

| capex_to_cfo | without / original | 0.160123 | ratio | computed / — | 0000002488-24-000163 / id:f-224; 0000002488-24-000163 / id:f-226; 0000002488-25-000012 / id:f-305; 0000002488-25-000012 / id:f-308 |

| fcf_basic | none / original | 1091000000.000000 | http://www.xbrl.org/2003/iso4217:USD | computed / — | 0000002488-24-000163 / id:f-224; 0000002488-24-000163 / id:f-226; 0000002488-25-000012 / id:f-305; 0000002488-25-000012 / id:f-308 |

| fcf_after_counterparty_financing | none / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| receivables_collection_period | none / receivables_only | 79.812157 | days | computed / — | 0000002488-24-000163 / id:f-126; 0000002488-24-000163 / id:f-32; 0000002488-25-000012 / id:f-116; 0000002488-25-000012 / id:f-40 |

| rpo_total | none / original | 85000000.000000 | http://www.xbrl.org/2003/iso4217:USD | computed / — | 0000002488-25-000012 / id:f-471 |

| rpo_total | none / text:7006690dde52f8c555a5b01e8fb3ee1739a19d3c73c67a9af5463bf0e6d2e3e7 | 85000000.000000 | http://www.xbrl.org/2003/iso4217:USD | computed / — | 0000002488-25-000012 / rawbytes:1071663:1111717 |

| liq_principal_due_to_cash | horizon_12m / original | ND | — | not_determinable / missing_admissible_terms | — |

| liq_principal_due_to_cash | horizon_24m / original | ND | — | not_determinable / missing_admissible_terms | — |

| lev_debt_and_leases_to_operating_income_plus_da | debt / original | ND | — | not_determinable / missing_admissible_terms | — |

| lev_debt_and_leases_to_operating_income_plus_da | leases / original | ND | — | not_determinable / missing_admissible_terms | — |

| lease_not_commenced_bridge | additions / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| lease_not_commenced_bridge | closing / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| lease_not_commenced_bridge | commenced / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| lease_not_commenced_bridge | opening / original | 4287000000.000000 | http://www.xbrl.org/2003/iso4217:USD | computed / — | 0000002488-24-000163 / id:f-872 |

La matrice conserve séparément les bases, échéances et composants ; aucune somme unique. Les additions et ponts non établis restent manquants. La qualité du résultat, les changements de durée et les gains ou pertes d’investissement gardent leur pièce et leur rupture de base dans les tables. Les engagements non lus ne sont pas tenus pour nuls.

### AMZN

Dernière période de revenu exploitable : 2026-06-30. Les séries complètes sont dans series.csv ; les périodes fiscales et dates de publicité y sont distinctes.

| Mesure | Terme / variante | Valeur | Unité | Statut / motif | Source |

| --- | --- | ---: | --- | --- | --- |

| revenue_total | none / original | 200606000000.000000 | http://www.xbrl.org/2003/iso4217:USD | computed / — | 0001018724-26-000026 / id:f-237 |

| revenue_growth | ttm / original | 0.157666 | ratio | computed / — | 0001018724-25-000123 / id:f-212; 0001018724-25-000123 / id:f-213; 0001018724-25-000123 / id:f-214; 0001018724-25-000123 / id:f-215; 0001018724-26-000004 / id:f-151; 0001018724-26-000004 / id:f-152; 0001018724-26-000014 / id:f-174; 0001018724-26-000014 / id:f-175; 0001018724-26-000026 / id:f-236; 0001018724-26-000026 / id:f-237 |

| revenue_growth | yoy / original | 0.196205 | ratio | computed / — | 0001018724-26-000026 / id:f-236; 0001018724-26-000026 / id:f-237 |

| capex_to_cfo | with / original | ND | — | not_determinable / missing_admissible_terms | — |

| capex_to_cfo | without / original | ND | — | not_determinable / missing_admissible_terms | — |

| fcf_basic | none / original | ND | — | not_determinable / missing_admissible_terms | — |

| fcf_after_counterparty_financing | none / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| receivables_collection_period | none / receivables_only | 37.112011 | days | computed / — | 0001018724-26-000014 / id:f-251; 0001018724-26-000026 / id:f-237; 0001018724-26-000026 / id:f-383 |

| rpo_total | none / original | ND | — | not_determinable / missing_admissible_terms | — |

| liq_principal_due_to_cash | horizon_12m / original | ND | — | not_determinable / missing_admissible_terms | — |

| liq_principal_due_to_cash | horizon_24m / original | ND | — | not_determinable / missing_admissible_terms | — |

| lev_debt_and_leases_to_operating_income_plus_da | debt / long_term_carrying_only | 0.782798 | ratio | partial / short_term_debt_and_other_components_not_established | 0001018724-25-000123 / id:f-245; 0001018724-25-000123 / id:f-247; 0001018724-25-000123 / id:f-43; 0001018724-25-000123 / id:f-45; 0001018724-26-000004 / id:f-176; 0001018724-26-000004 / id:f-65; 0001018724-26-000014 / id:f-191; 0001018724-26-000014 / id:f-63; 0001018724-26-000026 / id:f-269; 0001018724-26-000026 / id:f-407; 0001018724-26-000026 / id:f-67; 0001018724-26-000026 / id:f-937 |

| lev_debt_and_leases_to_operating_income_plus_da | debt / original | ND | — | not_determinable / missing_admissible_terms | — |

| lev_debt_and_leases_to_operating_income_plus_da | leases / original | 0.649871 | ratio | computed / — | 0001018724-25-000123 / id:f-245; 0001018724-25-000123 / id:f-247; 0001018724-25-000123 / id:f-43; 0001018724-25-000123 / id:f-45; 0001018724-26-000004 / id:f-176; 0001018724-26-000004 / id:f-65; 0001018724-26-000014 / id:f-191; 0001018724-26-000014 / id:f-63; 0001018724-26-000026 / id:f-269; 0001018724-26-000026 / id:f-67; 0001018724-26-000026 / id:f-767; 0001018724-26-000026 / id:f-768; 0001018724-26-000026 / id:f-774; 0001018724-26-000026 / id:f-775 |

| lease_not_commenced_bridge | additions / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| lease_not_commenced_bridge | closing / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| lease_not_commenced_bridge | commenced / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| lease_not_commenced_bridge | opening / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

La matrice conserve séparément les bases, échéances et composants ; aucune somme unique. Les additions et ponts non établis restent manquants. La qualité du résultat, les changements de durée et les gains ou pertes d’investissement gardent leur pièce et leur rupture de base dans les tables. Les engagements non lus ne sont pas tenus pour nuls.

### AVGO

Dernière période de revenu exploitable : 2026-05-03. Les séries complètes sont dans series.csv ; les périodes fiscales et dates de publicité y sont distinctes.

| Mesure | Terme / variante | Valeur | Unité | Statut / motif | Source |

| --- | --- | ---: | --- | --- | --- |

| revenue_total | none / original | 22187000000.000000 | http://www.xbrl.org/2003/iso4217:USD | computed / — | 0001730168-26-000054 / id:f-1063 |

| revenue_growth | ttm / original | 0.322880 | ratio | computed / — | 0001730168-25-000098 / id:f-1147; 0001730168-25-000098 / id:f-1148; 0001730168-25-000098 / id:f-1149; 0001730168-25-000098 / id:f-1150; 0001730168-25-000121 / id:f-129; 0001730168-25-000121 / id:f-130; 0001730168-26-000016 / id:f-859; 0001730168-26-000016 / id:f-860; 0001730168-26-000054 / id:f-1063; 0001730168-26-000054 / id:f-1064 |

| revenue_growth | yoy / original | 0.478739 | ratio | computed / — | 0001730168-26-000054 / id:f-1063; 0001730168-26-000054 / id:f-1064 |

| capex_to_cfo | with / original | ND | — | not_determinable / missing_admissible_terms | — |

| capex_to_cfo | without / original | 0.022015 | ratio | computed / — | 0001730168-26-000016 / id:f-184; 0001730168-26-000016 / id:f-186; 0001730168-26-000054 / id:f-242; 0001730168-26-000054 / id:f-244 |

| fcf_basic | none / original | 10262000000.000000 | http://www.xbrl.org/2003/iso4217:USD | computed / — | 0001730168-26-000016 / id:f-184; 0001730168-26-000016 / id:f-186; 0001730168-26-000054 / id:f-242; 0001730168-26-000054 / id:f-244 |

| fcf_after_counterparty_financing | none / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| receivables_collection_period | none / original | 80.053094 | days | computed / — | 0001730168-26-000016 / id:f-319; 0001730168-26-000016 / id:f-32; 0001730168-26-000054 / id:f-1063; 0001730168-26-000054 / id:f-32; 0001730168-26-000054 / id:f-463 |

| receivables_collection_period | none / receivables_only | 39.558976 | days | computed / — | 0001730168-26-000016 / id:f-32; 0001730168-26-000054 / id:f-1063; 0001730168-26-000054 / id:f-32 |

| rpo_total | none / original | 164600000000.000000 | http://www.xbrl.org/2003/iso4217:USD | computed / — | 0001730168-26-000054 / id:f-470 |

| liq_principal_due_to_cash | horizon_12m / original | ND | — | not_determinable / missing_admissible_terms | — |

| liq_principal_due_to_cash | horizon_24m / original | ND | — | not_determinable / missing_admissible_terms | — |

| lev_debt_and_leases_to_operating_income_plus_da | debt / original | ND | — | not_determinable / missing_admissible_terms | — |

| lev_debt_and_leases_to_operating_income_plus_da | leases / original | ND | — | not_determinable / missing_admissible_terms | — |

| lease_not_commenced_bridge | additions / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| lease_not_commenced_bridge | closing / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| lease_not_commenced_bridge | commenced / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| lease_not_commenced_bridge | opening / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

La matrice conserve séparément les bases, échéances et composants ; aucune somme unique. Les additions et ponts non établis restent manquants. La qualité du résultat, les changements de durée et les gains ou pertes d’investissement gardent leur pièce et leur rupture de base dans les tables. Les engagements non lus ne sont pas tenus pour nuls.

### CRWV

Dernière période de revenu exploitable : 2026-06-30. Les séries complètes sont dans series.csv ; les périodes fiscales et dates de publicité y sont distinctes.

| Mesure | Terme / variante | Valeur | Unité | Statut / motif | Source |

| --- | --- | ---: | --- | --- | --- |

| revenue_total | none / original | 2575000000.000000 | http://www.xbrl.org/2003/iso4217:USD | computed / — | 0001769628-26-000366 / id:f-147 |

| revenue_growth | ttm / original | ND | — | not_determinable / missing_admissible_terms | — |

| revenue_growth | yoy / original | 1.124587 | ratio | computed / — | 0001769628-26-000366 / id:f-147; 0001769628-26-000366 / id:f-148 |

| capex_to_cfo | with / original | ND | — | not_determinable / missing_admissible_terms | — |

| capex_to_cfo | without / original | 9.458027 | ratio | computed / — | 0001769628-26-000222 / id:f-284; 0001769628-26-000222 / id:f-286; 0001769628-26-000366 / id:f-391; 0001769628-26-000366 / id:f-393 |

| fcf_basic | none / original | -5743000000.000000 | http://www.xbrl.org/2003/iso4217:USD | computed / — | 0001769628-26-000222 / id:f-284; 0001769628-26-000222 / id:f-286; 0001769628-26-000366 / id:f-391; 0001769628-26-000366 / id:f-393 |

| fcf_after_counterparty_financing | none / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| receivables_collection_period | none / receivables_only | 82.359417 | days | computed / — | 0001769628-26-000222 / id:f-39; 0001769628-26-000366 / id:f-147; 0001769628-26-000366 / id:f-39 |

| rpo_total | none / original | 103700000000.000000 | http://www.xbrl.org/2003/iso4217:USD | computed / — | 0001769628-26-000366 / id:f-521 |

| liq_principal_due_to_cash | horizon_12m / original | ND | — | not_determinable / missing_admissible_terms | — |

| liq_principal_due_to_cash | horizon_24m / original | ND | — | not_determinable / missing_admissible_terms | — |

| lev_debt_and_leases_to_operating_income_plus_da | debt / original | ND | — | not_determinable / missing_admissible_terms | — |

| lev_debt_and_leases_to_operating_income_plus_da | leases / original | ND | — | not_determinable / missing_admissible_terms | — |

| lease_not_commenced_bridge | additions / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| lease_not_commenced_bridge | closing / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| lease_not_commenced_bridge | commenced / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| lease_not_commenced_bridge | opening / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

La matrice conserve séparément les bases, échéances et composants ; aucune somme unique. Les additions et ponts non établis restent manquants. La qualité du résultat, les changements de durée et les gains ou pertes d’investissement gardent leur pièce et leur rupture de base dans les tables. Les engagements non lus ne sont pas tenus pour nuls.

### GOOGL

Dernière période de revenu exploitable : 2026-06-30. Les séries complètes sont dans series.csv ; les périodes fiscales et dates de publicité y sont distinctes.

| Mesure | Terme / variante | Valeur | Unité | Statut / motif | Source |

| --- | --- | ---: | --- | --- | --- |

| revenue_total | none / original | 119796000000.000000 | http://www.xbrl.org/2003/iso4217:USD | computed / — | 0001652044-26-000071 / id:f-214 |

| revenue_growth | ttm / original | 0.200507 | ratio | computed / — | 0001652044-25-000091 / id:f-146; 0001652044-25-000091 / id:f-147; 0001652044-25-000091 / id:f-148; 0001652044-25-000091 / id:f-149; 0001652044-26-000018 / id:f-189; 0001652044-26-000018 / id:f-190; 0001652044-26-000048 / id:f-181; 0001652044-26-000048 / id:f-182; 0001652044-26-000071 / id:f-213; 0001652044-26-000071 / id:f-214 |

| revenue_growth | yoy / original | 0.242336 | ratio | computed / — | 0001652044-26-000071 / id:f-213; 0001652044-26-000071 / id:f-214 |

| capex_to_cfo | with / original | ND | — | not_determinable / missing_admissible_terms | — |

| capex_to_cfo | without / original | 1.149863 | ratio | computed / — | 0001652044-26-000048 / id:f-312; 0001652044-26-000048 / id:f-314; 0001652044-26-000071 / id:f-494; 0001652044-26-000071 / id:f-496 |

| fcf_basic | none / original | -5855000000.000000 | http://www.xbrl.org/2003/iso4217:USD | computed / — | 0001652044-26-000048 / id:f-312; 0001652044-26-000048 / id:f-314; 0001652044-26-000071 / id:f-494; 0001652044-26-000071 / id:f-496 |

| fcf_after_counterparty_financing | none / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| receivables_collection_period | none / receivables_only | 50.201317 | days | computed / — | 0001652044-26-000048 / id:f-90; 0001652044-26-000071 / id:f-114; 0001652044-26-000071 / id:f-214 |

| rpo_total | none / original | 519500000000.000000 | http://www.xbrl.org/2003/iso4217:USD | computed / — | 0001652044-26-000071 / id:f-645 |

| liq_principal_due_to_cash | horizon_12m / original | ND | — | not_determinable / missing_admissible_terms | — |

| liq_principal_due_to_cash | horizon_24m / original | ND | — | not_determinable / missing_admissible_terms | — |

| lev_debt_and_leases_to_operating_income_plus_da | debt / original | ND | — | not_determinable / missing_admissible_terms | — |

| lev_debt_and_leases_to_operating_income_plus_da | leases / original | ND | — | not_determinable / missing_admissible_terms | — |

| lease_not_commenced_bridge | additions / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| lease_not_commenced_bridge | closing / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| lease_not_commenced_bridge | commenced / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| lease_not_commenced_bridge | opening / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

La matrice conserve séparément les bases, échéances et composants ; aucune somme unique. Les additions et ponts non établis restent manquants. La qualité du résultat, les changements de durée et les gains ou pertes d’investissement gardent leur pièce et leur rupture de base dans les tables. Les engagements non lus ne sont pas tenus pour nuls.

### META

Dernière période de revenu exploitable : 2026-06-30. Les séries complètes sont dans series.csv ; les périodes fiscales et dates de publicité y sont distinctes.

| Mesure | Terme / variante | Valeur | Unité | Statut / motif | Source |

| --- | --- | ---: | --- | --- | --- |

| revenue_total | none / original | 60801000000.000000 | http://www.xbrl.org/2003/iso4217:USD | computed / — | 0001628280-26-050705 / id:f-97 |

| revenue_growth | ttm / original | 0.276521 | ratio | computed / — | 0001628280-25-047240 / id:f-100; 0001628280-25-047240 / id:f-101; 0001628280-25-047240 / id:f-102; 0001628280-25-047240 / id:f-99; 0001628280-26-003942 / id:f-127; 0001628280-26-003942 / id:f-128; 0001628280-26-028526 / id:f-97; 0001628280-26-028526 / id:f-98; 0001628280-26-050705 / id:f-97; 0001628280-26-050705 / id:f-98 |

| revenue_growth | yoy / original | 0.279590 | ratio | computed / — | 0001628280-26-050705 / id:f-97; 0001628280-26-050705 / id:f-98 |

| capex_to_cfo | with / original | ND | — | not_determinable / missing_admissible_terms | — |

| capex_to_cfo | without / original | 0.945201 | ratio | computed / — | 0001628280-26-028526 / id:f-212; 0001628280-26-028526 / id:f-214; 0001628280-26-050705 / id:f-303; 0001628280-26-050705 / id:f-305 |

| fcf_basic | none / original | 1746000000.000000 | http://www.xbrl.org/2003/iso4217:USD | computed / — | 0001628280-26-028526 / id:f-212; 0001628280-26-028526 / id:f-214; 0001628280-26-050705 / id:f-303; 0001628280-26-050705 / id:f-305 |

| fcf_after_counterparty_financing | none / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| receivables_collection_period | none / receivables_only | 29.351507 | days | computed / — | 0001628280-26-028526 / id:f-35; 0001628280-26-050705 / id:f-35; 0001628280-26-050705 / id:f-97 |

| rpo_total | none / original | ND | — | not_determinable / missing_admissible_terms | — |

| liq_principal_due_to_cash | horizon_12m / original | ND | — | not_determinable / missing_admissible_terms | — |

| liq_principal_due_to_cash | horizon_24m / original | ND | — | not_determinable / missing_admissible_terms | — |

| lev_debt_and_leases_to_operating_income_plus_da | debt / original | ND | — | not_determinable / missing_admissible_terms | — |

| lev_debt_and_leases_to_operating_income_plus_da | leases / original | ND | — | not_determinable / missing_admissible_terms | — |

| lease_not_commenced_bridge | additions / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| lease_not_commenced_bridge | closing / original | 278990000000.000000 | http://www.xbrl.org/2003/iso4217:USD | computed / — | 0001628280-26-050705 / id:f-764 |

| lease_not_commenced_bridge | commenced / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| lease_not_commenced_bridge | opening / original | 182880000000.000000 | http://www.xbrl.org/2003/iso4217:USD | computed / — | 0001628280-26-028526 / id:f-549 |

La matrice conserve séparément les bases, échéances et composants ; aucune somme unique. Les additions et ponts non établis restent manquants. La qualité du résultat, les changements de durée et les gains ou pertes d’investissement gardent leur pièce et leur rupture de base dans les tables. Les engagements non lus ne sont pas tenus pour nuls.

### MRVL

Dernière période de revenu exploitable : 2026-08-01. Les séries complètes sont dans series.csv ; les périodes fiscales et dates de publicité y sont distinctes.

| Mesure | Terme / variante | Valeur | Unité | Statut / motif | Source |

| --- | --- | ---: | --- | --- | --- |

| revenue_total | none / original | 2739300000.000000 | http://www.xbrl.org/2003/iso4217:USD | computed / — | 0001835632-26-000025 / id:f-92 |

| revenue_growth | ttm / original | 0.306210 | ratio | computed / — | 0001835632-25-000197 / id:f-84; 0001835632-25-000197 / id:f-85; 0001835632-25-000197 / id:f-86; 0001835632-25-000197 / id:f-87; 0001835632-26-000011 / id:f-125; 0001835632-26-000011 / id:f-126; 0001835632-26-000019 / id:f-92; 0001835632-26-000019 / id:f-93; 0001835632-26-000025 / id:f-92; 0001835632-26-000025 / id:f-93 |

| revenue_growth | yoy / original | 0.365485 | ratio | computed / — | 0001835632-26-000025 / id:f-92; 0001835632-26-000025 / id:f-93 |

| capex_to_cfo | with / original | ND | — | not_determinable / missing_admissible_terms | — |

| capex_to_cfo | without / original | 0.209249 | ratio | computed / — | 0001835632-26-000019 / id:f-239; 0001835632-26-000019 / id:f-243; 0001835632-26-000025 / id:f-334; 0001835632-26-000025 / id:f-338 |

| fcf_basic | none / original | 478800000.000000 | http://www.xbrl.org/2003/iso4217:USD | computed / — | 0001835632-26-000019 / id:f-239; 0001835632-26-000019 / id:f-243; 0001835632-26-000025 / id:f-334; 0001835632-26-000025 / id:f-338 |

| fcf_after_counterparty_financing | none / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| receivables_collection_period | none / receivables_only | 67.936900 | days | computed / — | 0001835632-26-000019 / id:f-32; 0001835632-26-000025 / id:f-32; 0001835632-26-000025 / id:f-92 |

| rpo_total | none / original | ND | — | not_determinable / missing_admissible_terms | — |

| liq_principal_due_to_cash | horizon_12m / original | ND | — | not_determinable / missing_admissible_terms | — |

| liq_principal_due_to_cash | horizon_24m / original | ND | — | not_determinable / missing_admissible_terms | — |

| lev_debt_and_leases_to_operating_income_plus_da | debt / original | ND | — | not_determinable / missing_admissible_terms | — |

| lev_debt_and_leases_to_operating_income_plus_da | leases / original | ND | — | not_determinable / missing_admissible_terms | — |

| lease_not_commenced_bridge | additions / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| lease_not_commenced_bridge | closing / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| lease_not_commenced_bridge | commenced / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| lease_not_commenced_bridge | opening / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

La matrice conserve séparément les bases, échéances et composants ; aucune somme unique. Les additions et ponts non établis restent manquants. La qualité du résultat, les changements de durée et les gains ou pertes d’investissement gardent leur pièce et leur rupture de base dans les tables. Les engagements non lus ne sont pas tenus pour nuls.

### MSFT

Dernière période de revenu exploitable : 2026-06-30. Les séries complètes sont dans series.csv ; les périodes fiscales et dates de publicité y sont distinctes.

| Mesure | Terme / variante | Valeur | Unité | Statut / motif | Source |

| --- | --- | ---: | --- | --- | --- |

| revenue_total | none / original | 90007000000.000000 | http://www.xbrl.org/2003/iso4217:USD | computed / — | 0001193125-26-191507 / id:F_e21662e1-735e-4c88-8572-41b8025be638; 0001193125-26-323660 / id:F_a62216e4-4826-4209-89af-643bc5c2df10 |

| revenue_growth | ttm / original | 0.177887 | ratio | computed / — | 0001193125-25-256321 / id:F_3149e777-9a9e-40ad-9bbf-597ef75c0b4d; 0001193125-25-256321 / id:F_41b15cf6-c3cc-43d1-9e31-038f11b5c91a; 0001193125-26-027207 / id:F_456bad0d-d5de-42cd-b632-52f95f7d3231; 0001193125-26-027207 / id:F_98b2de65-42c6-4ae5-a372-805a791b90dc; 0001193125-26-191507 / id:F_2699a207-a0e9-4c55-8a3a-c180e2714314; 0001193125-26-191507 / id:F_3d73e726-8508-4605-87a7-ae4fbcdbc622; 0001193125-26-191507 / id:F_e21662e1-735e-4c88-8572-41b8025be638; 0001193125-26-191507 / id:F_f1524389-a67f-4850-a5b2-93042af90db7; 0001193125-26-323660 / id:F_a62216e4-4826-4209-89af-643bc5c2df10; 0001193125-26-323660 / id:F_d3febf44-5717-45d3-a565-dab944f2f096 |

| revenue_growth | yoy / original | 0.177470 | ratio | computed / — | 0001193125-26-191507 / id:F_2699a207-a0e9-4c55-8a3a-c180e2714314; 0001193125-26-191507 / id:F_e21662e1-735e-4c88-8572-41b8025be638; 0001193125-26-323660 / id:F_a62216e4-4826-4209-89af-643bc5c2df10; 0001193125-26-323660 / id:F_d3febf44-5717-45d3-a565-dab944f2f096 |

| capex_to_cfo | with / original | ND | — | not_determinable / missing_admissible_terms | — |

| capex_to_cfo | without / original | 0.645768 | ratio | computed / — | 0001193125-26-191507 / id:F_404612cb-5cca-4f4f-a0c6-31e54bd8a38d; 0001193125-26-191507 / id:F_c7bc0144-6bd5-4e47-810e-72b7dab8e726; 0001193125-26-323660 / id:F_09f41249-b58f-478b-a38c-f33fcdfa87ec; 0001193125-26-323660 / id:F_1bf2d932-9a21-41e8-9d22-32533c8ae3e5 |

| fcf_basic | none / original | 19639000000.000000 | http://www.xbrl.org/2003/iso4217:USD | computed / — | 0001193125-26-191507 / id:F_404612cb-5cca-4f4f-a0c6-31e54bd8a38d; 0001193125-26-191507 / id:F_c7bc0144-6bd5-4e47-810e-72b7dab8e726; 0001193125-26-323660 / id:F_09f41249-b58f-478b-a38c-f33fcdfa87ec; 0001193125-26-323660 / id:F_1bf2d932-9a21-41e8-9d22-32533c8ae3e5 |

| fcf_after_counterparty_financing | none / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| receivables_collection_period | none / receivables_only | 71.235832 | days | computed / — | 0001193125-26-191507 / id:F_36db8820-662b-4f79-afdc-bd78da4a0daa; 0001193125-26-191507 / id:F_e21662e1-735e-4c88-8572-41b8025be638; 0001193125-26-323660 / id:F_a2d55700-fe7f-4b37-97a5-3d8bac5c31fa; 0001193125-26-323660 / id:F_a62216e4-4826-4209-89af-643bc5c2df10 |

| rpo_total | none / original | 684000000000.000000 | http://www.xbrl.org/2003/iso4217:USD | computed / — | 0001193125-26-323660 / id:F_c4efedd6-6e0a-4c20-bcbd-40c3f3a0c364 |

| liq_principal_due_to_cash | horizon_12m / cash_only_long_term_principal | 0.441844 | ratio | partial / short_term_principal_not_included | 0001193125-26-323660 / id:F_94c65b37-f8c4-4ace-9b34-b361903ee64f; 0001193125-26-323660 / id:F_96a1227a-2fdd-4947-81c2-9d2f88189996 |

| liq_principal_due_to_cash | horizon_24m / original | ND | — | not_determinable / missing_admissible_terms | — |

| lev_debt_and_leases_to_operating_income_plus_da | debt / original | ND | — | not_determinable / missing_admissible_terms | — |

| lev_debt_and_leases_to_operating_income_plus_da | leases / original | ND | — | not_determinable / missing_admissible_terms | — |

| lease_not_commenced_bridge | additions / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| lease_not_commenced_bridge | closing / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| lease_not_commenced_bridge | commenced / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| lease_not_commenced_bridge | opening / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

La matrice conserve séparément les bases, échéances et composants ; aucune somme unique. Les additions et ponts non établis restent manquants. La qualité du résultat, les changements de durée et les gains ou pertes d’investissement gardent leur pièce et leur rupture de base dans les tables. Les engagements non lus ne sont pas tenus pour nuls.

### NVDA

Dernière période de revenu exploitable : 2026-07-26. Les séries complètes sont dans series.csv ; les périodes fiscales et dates de publicité y sont distinctes.

| Mesure | Terme / variante | Valeur | Unité | Statut / motif | Source |

| --- | --- | ---: | --- | --- | --- |

| revenue_total | none / original | 96221000000.000000 | http://www.xbrl.org/2003/iso4217:USD | computed / — | 0001045810-26-000075 / id:f-30 |

| revenue_growth | ttm / original | 0.833753 | ratio | computed / — | 0001045810-25-000230 / id:f-30; 0001045810-25-000230 / id:f-31; 0001045810-25-000230 / id:f-32; 0001045810-25-000230 / id:f-33; 0001045810-26-000021 / id:f-72; 0001045810-26-000021 / id:f-73; 0001045810-26-000052 / id:f-30; 0001045810-26-000052 / id:f-31; 0001045810-26-000075 / id:f-30; 0001045810-26-000075 / id:f-31 |

| revenue_growth | yoy / original | 1.058511 | ratio | computed / — | 0001045810-26-000075 / id:f-30; 0001045810-26-000075 / id:f-31 |

| capex_to_cfo | with / original | ND | — | not_determinable / missing_admissible_terms | — |

| capex_to_cfo | without / original | ND | — | not_determinable / missing_admissible_terms | — |

| fcf_basic | none / original | ND | — | not_determinable / missing_admissible_terms | — |

| fcf_after_counterparty_financing | none / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| receivables_collection_period | none / receivables_only | 49.069221 | days | computed / — | 0001045810-26-000052 / id:f-82; 0001045810-26-000075 / id:f-116; 0001045810-26-000075 / id:f-30 |

| rpo_total | none / original | 3200000000.000000 | http://www.xbrl.org/2003/iso4217:USD | computed / — | 0001045810-26-000075 / id:f-694 |

| liq_principal_due_to_cash | horizon_12m / original | ND | — | not_determinable / missing_admissible_terms | — |

| liq_principal_due_to_cash | horizon_24m / original | ND | — | not_determinable / missing_admissible_terms | — |

| lev_debt_and_leases_to_operating_income_plus_da | debt / long_term_carrying_only | 0.165781 | ratio | partial / short_term_debt_and_other_components_not_established | 0001045810-25-000209 / id:f-312; 0001045810-25-000230 / id:f-320; 0001045810-25-000230 / id:f-54; 0001045810-25-000230 / id:f-56; 0001045810-26-000021 / id:f-305; 0001045810-26-000021 / id:f-90; 0001045810-26-000052 / id:f-208; 0001045810-26-000052 / id:f-42; 0001045810-26-000075 / id:f-148; 0001045810-26-000075 / id:f-304; 0001045810-26-000075 / id:f-54; 0001045810-26-000075 / id:f-815 |

| lev_debt_and_leases_to_operating_income_plus_da | debt / original | ND | — | not_determinable / missing_admissible_terms | — |

| lev_debt_and_leases_to_operating_income_plus_da | leases / original | ND | — | not_determinable / missing_admissible_terms | — |

| lease_not_commenced_bridge | additions / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| lease_not_commenced_bridge | closing / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| lease_not_commenced_bridge | commenced / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| lease_not_commenced_bridge | opening / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

La matrice conserve séparément les bases, échéances et composants ; aucune somme unique. Les additions et ponts non établis restent manquants. La qualité du résultat, les changements de durée et les gains ou pertes d’investissement gardent leur pièce et leur rupture de base dans les tables. Les engagements non lus ne sont pas tenus pour nuls.

### ORCL

Dernière période de revenu exploitable : 2026-08-31. Les séries complètes sont dans series.csv ; les périodes fiscales et dates de publicité y sont distinctes.

| Mesure | Terme / variante | Valeur | Unité | Statut / motif | Source |

| --- | --- | ---: | --- | --- | --- |

| revenue_total | none / original | 19345000000.000000 | http://www.xbrl.org/2003/iso4217:USD | computed / — | 0001193125-26-389274 / id:F_9e745c96-2265-46b6-b29d-b54fa66160bd |

| revenue_growth | ttm / original | 0.216188 | ratio | computed / — | 0001193125-25-315925 / id:F_23f40c56-a7ac-4cab-8418-48da10f82a9d; 0001193125-25-315925 / id:F_aacb8cb4-4e6f-4a47-ade3-64ec6df9dba0; 0001193125-26-101045 / id:F_16fd88e8-7223-40cb-8a29-9f410379ffd0; 0001193125-26-101045 / id:F_1e5f9a53-bc2e-4f4b-b5b7-ec8c1496406c; 0001193125-26-101045 / id:F_bc09b41b-ac6b-4b65-86e2-e333211825ed; 0001193125-26-101045 / id:F_f339f494-f165-4c31-b1fc-aae89f8cbe4c; 0001193125-26-277521 / id:F_09a80f59-5ca8-486a-b75d-23733e198cb6; 0001193125-26-277521 / id:F_6ea1d335-7434-4152-8c37-442a5e6fedc5; 0001193125-26-389274 / id:F_6435f1c9-f45b-4315-8e05-1f4e0c908ff0; 0001193125-26-389274 / id:F_9e745c96-2265-46b6-b29d-b54fa66160bd |

| revenue_growth | yoy / original | 0.296061 | ratio | computed / — | 0001193125-26-389274 / id:F_6435f1c9-f45b-4315-8e05-1f4e0c908ff0; 0001193125-26-389274 / id:F_9e745c96-2265-46b6-b29d-b54fa66160bd |

| capex_to_cfo | with / original | ND | — | not_determinable / missing_admissible_terms | — |

| capex_to_cfo | without / original | 1.233563 | ratio | computed / — | 0001193125-26-389274 / id:F_20139350-41b2-4695-a0cd-cc401a11f57e; 0001193125-26-389274 / id:F_6b02eddf-d360-4c8a-bcc1-e8b94789e26d |

| fcf_basic | none / original | -5396000000.000000 | http://www.xbrl.org/2003/iso4217:USD | computed / — | 0001193125-26-389274 / id:F_20139350-41b2-4695-a0cd-cc401a11f57e; 0001193125-26-389274 / id:F_6b02eddf-d360-4c8a-bcc1-e8b94789e26d |

| fcf_after_counterparty_financing | none / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| receivables_collection_period | none / receivables_only | 51.787749 | days | computed / — | 0001193125-26-389274 / id:F_79ec7763-1df4-4ea6-9c53-63276fa4f514; 0001193125-26-389274 / id:F_9e745c96-2265-46b6-b29d-b54fa66160bd; 0001193125-26-389274 / id:F_c6406765-5429-4f94-95af-8c99a7d45154 |

| rpo_total | none / text:c459569cfcd2d3c0f08330a17c32f90047f0bbc79775a74e12c94d9a303dd946 | 664000000000.000000 | http://www.xbrl.org/2003/iso4217:USD | partial / qualified_source_amount | 0001193125-26-389274 / rawbytes:791669:862272 |

| rpo_total | none / original | 664000000000.000000 | http://www.xbrl.org/2003/iso4217:USD | computed / — | 0001193125-26-389274 / id:F_b3c348b4-9226-462b-b27e-e98f45a68cc2 |

| liq_principal_due_to_cash | horizon_12m / original | ND | — | not_determinable / missing_admissible_terms | — |

| liq_principal_due_to_cash | horizon_24m / original | ND | — | not_determinable / missing_admissible_terms | — |

| lev_debt_and_leases_to_operating_income_plus_da | debt / original | ND | — | not_determinable / missing_admissible_terms | — |

| lev_debt_and_leases_to_operating_income_plus_da | leases / original | ND | — | not_determinable / missing_admissible_terms | — |

| lease_not_commenced_bridge | additions / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| lease_not_commenced_bridge | closing / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| lease_not_commenced_bridge | commenced / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| lease_not_commenced_bridge | opening / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

La matrice conserve séparément les bases, échéances et composants ; aucune somme unique. Les additions et ponts non établis restent manquants. La qualité du résultat, les changements de durée et les gains ou pertes d’investissement gardent leur pièce et leur rupture de base dans les tables. Les engagements non lus ne sont pas tenus pour nuls.

### SPCX

Dernière période de revenu exploitable : 2026-06-30. Les séries complètes sont dans series.csv ; les périodes fiscales et dates de publicité y sont distinctes.

| Mesure | Terme / variante | Valeur | Unité | Statut / motif | Source |

| --- | --- | ---: | --- | --- | --- |

| revenue_total | none / original | 7814000000.000000 | http://www.xbrl.org/2003/iso4217:USD | computed / — | 0001628280-26-052535 / id:f-135 |

| revenue_growth | ttm / original | ND | — | not_determinable / missing_admissible_terms | — |

| revenue_growth | yoy / original | 0.919430 | ratio | computed / — | 0001628280-26-052535 / id:f-135; 0001628280-26-052535 / id:f-136 |

| capex_to_cfo | with / original | ND | — | not_determinable / missing_admissible_terms | — |

| capex_to_cfo | without / original | ND | — | not_determinable / missing_admissible_terms | — |

| fcf_basic | none / original | ND | — | not_determinable / missing_admissible_terms | — |

| fcf_after_counterparty_financing | none / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| receivables_collection_period | none / original | ND | — | not_determinable / missing_admissible_terms | — |

| rpo_total | none / original | 47461000000.000000 | http://www.xbrl.org/2003/iso4217:USD | computed / — | 0001628280-26-052535 / id:f-574 |

| liq_principal_due_to_cash | horizon_12m / original | ND | — | not_determinable / missing_admissible_terms | — |

| liq_principal_due_to_cash | horizon_24m / original | ND | — | not_determinable / missing_admissible_terms | — |

| lev_debt_and_leases_to_operating_income_plus_da | debt / original | ND | — | not_determinable / missing_admissible_terms | — |

| lev_debt_and_leases_to_operating_income_plus_da | leases / original | ND | — | not_determinable / missing_admissible_terms | — |

| lease_not_commenced_bridge | additions / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| lease_not_commenced_bridge | closing / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| lease_not_commenced_bridge | commenced / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

| lease_not_commenced_bridge | opening / original | ND | — | not_determinable / public_attribution_or_complete_terms_not_established | — |

La matrice conserve séparément les bases, échéances et composants ; aucune somme unique. Les additions et ponts non établis restent manquants. La qualité du résultat, les changements de durée et les gains ou pertes d’investissement gardent leur pièce et leur rupture de base dans les tables. Les engagements non lus ne sont pas tenus pour nuls.

La présentation combinée de l’émetteur reste distincte du périmètre historique. Les tableaux annuels non balisés dont les contrôles n’ont pas abouti sont exclus ; aucune série annuelle de flux n’en est reconstruite. La série legacy_only hors ventilation sectorielle reste non déterminable.

## Circularité par paire

| Issue de paire | Nombre |
| --- | ---: |
| indeterminate | 692 |

Les cellules de documented_revenue_dependency, documented_backlog_dependency, consideration_to_customer et noncash_revenue_from_investees gardent leur contrepartie et leur motif. Un numérateur vide reste ND. La couverture du numérateur et celle du dénominateur sont séparées ; named_edge_coverage ne répartit pas artificiellement le revenu entre parts nommée, anonyme et résiduelle quand leur chevauchement n’est pas résolu.

Les plafonds et garanties publiés rendent certaines relations visibles sans prouver un financement versé. Le statut financé est daté, avec la sensibilité ever_financed à côté. La conclusion de chaque paire figure dans relationship_conclusion. Aucun ratio ni cycle ne démontre à lui seul une demande artificielle.

| Motif principal E7 | Issues de paire |
| --- | ---: |
| complete_public_attribution_not_established | 692 |

Les conditions de couverture enregistrées, non exclusives et distinctes des issues de paire, sont : {"anonymous_observations": 1512, "sales_channels": {}, "redacted_exclusions": 0, "not_processed_exclusions": 13689, "parse_failed_exclusions": 1, "non_filer": "not_determinable: annual-reporting status not established for each external legal identity"}. Les comptes de zéro portent sur les exclusions classées, jamais sur l’absence universelle d’une difficulté. Une concentration anonyme ne suffit pas à identifier juridiquement son client ; les non-déposants ne sont pas dénombrés par supposition.

Les critères E sont confrontés aux paires et aux exercices dans measures.parquet, même pour les cellules vides. Les chemins de l’extension restent non déterminables, motif not_processed ; ils ne sont pas comptés comme inexistants.

## Exclusions et évolution

Les motifs principaux sont publiés dans delta.md et audit/exclusions.csv. Les cinq familles de notes autorisées sont lues et assemblées. Les autres textes et la découverte gardent leur état de couverture propre. Les dates limites, identités, précisions et bases non établies restent visibles. Aucun comparatif exclu ni contrat signé ne remplit un versement ou un revenu manquant.

La comparaison avec le premier passage figure dans notes_complementaires.md. Les changements internes entre dépôts sont conservés par le contrôle de retraitement, avec leur cause connue ou inconnue. Les lectures et leur validation sont conservées pour les reprises.
