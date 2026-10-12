
-- SoftBank official-source extension: preserved SEC views and explicit alias equivalence
CREATE OR REPLACE VIEW legacy_EDGAR_documents AS SELECT * FROM read_parquet('work/softbank/baseline/documents.parquet');
CREATE OR REPLACE VIEW legacy_EDGAR_facts AS SELECT * FROM read_parquet('work/softbank/baseline/facts.parquet');
CREATE OR REPLACE VIEW legacy_EDGAR_observations AS SELECT * FROM read_parquet('work/softbank/baseline/observations.parquet');
CREATE OR REPLACE VIEW legacy_EDGAR_entities AS SELECT * FROM read_parquet('work/softbank/baseline/entities.parquet');
CREATE OR REPLACE VIEW legacy_EDGAR_links AS SELECT * FROM read_parquet('work/softbank/baseline/links.parquet');
CREATE OR REPLACE VIEW legacy_EDGAR_measures AS SELECT * FROM read_parquet('work/softbank/baseline/measures.parquet');
CREATE OR REPLACE VIEW legacy_EDGAR_controls AS SELECT * FROM read_parquet('work/softbank/baseline/controls.parquet');
CREATE OR REPLACE VIEW legacy_EDGAR_exclusions AS SELECT * FROM read_parquet('work/softbank/baseline/exclusions.parquet');
CREATE OR REPLACE VIEW softbank_exact_legal_aliases AS SELECT 'legal:c6093da255d21e7a8ac43260664c079cda668f5af64b65f0df40bf88f6d47a0d' legacy_entity_id,'legal:c6093da255d21e7a8ac43260664c079cda668f5af64b65f0df40bf88f6d47a0d' canonical_entity_id UNION ALL SELECT 'legal:db237b7db1910037e6fa14b31156b22adbfa302f9a4606b7c01c517778089f06' legacy_entity_id,'legal:c6093da255d21e7a8ac43260664c079cda668f5af64b65f0df40bf88f6d47a0d' canonical_entity_id;
CREATE OR REPLACE VIEW softbank_qualified_measures AS SELECT * FROM read_parquet('tables/measures.parquet') WHERE group_id='external:0001065521' AND variant='extended_official_JP_sources';
CREATE OR REPLACE VIEW integrated_resolved_links AS
      SELECT l.*,COALESCE(a.canonical_entity_id,l.from_entity_id) canonical_from_entity_id,
        COALESCE(b.canonical_entity_id,l.to_entity_id) canonical_to_entity_id
      FROM read_parquet('tables/links.parquet') l
      LEFT JOIN softbank_exact_legal_aliases a ON a.legacy_entity_id=l.from_entity_id
      LEFT JOIN softbank_exact_legal_aliases b ON b.legacy_entity_id=l.to_entity_id;
