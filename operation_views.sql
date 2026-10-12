-- Run after loading the eight current Parquet tables as views/tables.
CREATE OR REPLACE VIEW effective_links AS
SELECT l.* FROM links l WHERE NOT EXISTS (
 SELECT 1 FROM links replacement WHERE replacement.relation_type='replaces'
 AND replacement.resolved AND replacement.amount_a_id=l.link_id
);
CREATE OR REPLACE VIEW operation_quantities AS
SELECT * FROM measures WHERE variant='operation_dependencies_v1';
CREATE OR REPLACE VIEW operation_edges AS
SELECT * FROM effective_links WHERE instrument_key IN (
 'CEREBRAS_OPENAI','WHCO_CAPITAL_SOLUTION','NVIDIA_CRWV','TERAWULF_FLUIDSTACK',
 'SB_PORTS','NSCALE','IONIC_WARD','HUT_RIVER','HUT_BEACON','HYPERION','LAMBDA_COMPUTE_I'
);
