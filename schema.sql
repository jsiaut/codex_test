-- Huit tables seulement. Les énumérations sont appliquées par DuckDB.
CREATE TYPE filing_status_t AS ENUM ('filed','furnished','submitted_draft','correspondence','unclassified');
CREATE TYPE assurance_t AS ENUM ('audited','reviewed','unaudited','unknown','not_applicable');
CREATE TYPE tier_t AS ENUM ('A','B','C','D','E','F');
CREATE TYPE stage_t AS ENUM ('intent_non_binding','signed','available','drawn_or_paid','delivered','recognized','settled','terminated');
CREATE TYPE counterparty_evidence_t AS ENUM ('named','derivable','anonymous');
CREATE TYPE counterparty_method_t AS ENUM ('contract_parties','dimension_member_label','exact_named_amount_same_filing','explicit_cross_reference');
CREATE TYPE family_t AS ENUM ('financing','credit_support','commercial','customer_consideration');
CREATE TYPE link_type_t AS ENUM ('equity_primary','convertible_or_safe','loan_or_facility','vendor_credit','noncash_investment','lease_financing','guarantee','backstop','residual_value_guarantee','credit_enhancement','revenue_recognized','purchase','purchase_commitment','capacity_lease','prepayment','equity_or_warrants_to_customer','credits_to_customer','cash_incentive_to_customer');
CREATE TYPE edge_kind_t AS ENUM ('amount','relation');
CREATE TYPE financing_state_t AS ENUM ('active','lapsed','never','unknown');
CREATE TYPE financing_policy_t AS ENUM ('exposure_outstanding','ever_financed','none');
CREATE TYPE edge_structure_t AS ENUM ('financing_only','commercial_only','commercial_and_financing','reciprocal_commercial','none');
CREATE TYPE linkage_evidence_t AS ENUM ('documented_link','searched_none_found','search_incomplete');
CREATE TYPE linkage_class_t AS ENUM ('L1','L2','L3','L4','L5');
CREATE TYPE relationship_conclusion_t AS ENUM ('documented_dependency','commercial_with_financing','reciprocal_commercial_only','causality_not_established');
CREATE TYPE block_t AS ENUM ('recognized_liabilities','contractual_outflows','contingent_obligations','exposed_assets');
CREATE TYPE category_t AS ENUM ('debt','lease_liability','financing_obligation','supplier_finance_program','earnout','derivative_credit_support','lease_operating_maturity','lease_finance_maturity','lease_not_commenced','purchase_obligation','purchase_obligation_supplier_financing','take_or_pay','uncalled_commitment','jv_funding_commitment','construction_commitment','power_purchase_agreement','guarantee','vie_unconsolidated','standby_lc','capacity_backstop','receivables_transferred','indemnification','loss_contingency');
CREATE TYPE component_t AS ENUM ('principal','interest','lease_payment','purchase','minimum_purchase','capacity_fee','termination_payment','guarantee_cap','residual_value_guarantee','support_commitment_contractual','support_noncontractual','interest_held','other');
CREATE TYPE conditionality_t AS ENUM ('firm','conditional','optional');
CREATE TYPE trigger_t AS ENUM ('yes','no','unknown');
CREATE TYPE recast_cause_t AS ENUM ('error_correction_restatement','error_correction_revision','accounting_change','common_control_combination','discontinued_operations','segment_change','presentation_reclassification','unknown');
CREATE TYPE view_t AS ENUM ('as_known','revised');
CREATE TYPE event_t AS ENUM ('commitment','signing','availability','drawdown','funding','secondary_purchase','delivery','recognition','repayment','conversion','amendment','expiry','guarantee_call','payment','purchase','commencement','impairment','observable_price_adjustment','measurement_change','disposal','termination','default','acceleration','noncash_contribution','warrant_vesting');
CREATE TYPE amount_origin_t AS ENUM ('tagged_reference','narrative_only');
CREATE TYPE amount_qualifier_t AS ENUM ('exact','approximately','at_least','more_than','up_to','at_most','range');
CREATE TYPE coverage_t AS ENUM ('observed','explicit_zero','not_disclosed','not_applicable','redacted','not_collected','not_processed','parse_failed','conflicting','policy_excluded','unknown');
CREATE TYPE measure_status_t AS ENUM ('computed','bounded','partial','not_determinable','not_applicable','blocked_overlap');
CREATE TYPE relation_t AS ENUM ('same_measure','component_of','covers','overlaps','replaces','eliminated_with','transfers_to');
CREATE TYPE control_status_t AS ENUM ('ok','mismatch','not_testable','tautological');
CREATE TYPE tolerance_t AS ENUM ('instance','notes_dcml','inferred','none');
CREATE TYPE consolidation_t AS ENUM ('parent','consolidated_subsidiary','vie_consolidated','vie_unconsolidated','equity_method','investment_only','undetermined');
CREATE TYPE perspective_t AS ENUM ('reporting_entity','counterparty');
CREATE TYPE perimeter_t AS ENUM ('current','as_if_combined','legacy_only','constant','none');
CREATE TYPE quantity_kind_t AS ENUM ('instant','duration','text');
CREATE TYPE pair_coverage_t AS ENUM ('complete','partial','absent');
CREATE TYPE outcome_t AS ENUM ('supported','not_supported','refuted','indeterminate','compatible','incompatible','descriptive');
CREATE TYPE accounting_t AS ENUM ('us_gaap','ifrs','unknown');
CREATE TYPE entity_state_t AS ENUM ('confirmed','pending');

CREATE TABLE documents (
  document_id VARCHAR PRIMARY KEY,
  group_id VARCHAR, entity_id VARCHAR, cik VARCHAR,
  accession VARCHAR, document_rank INTEGER NOT NULL DEFAULT 0,
  document_rank_source VARCHAR, source_document_id VARCHAR,
  url VARCHAR NOT NULL, cache_path VARCHAR NOT NULL, sha256 VARCHAR NOT NULL,
  form VARCHAR, item VARCHAR, exhibit_type VARCHAR,
  filing_status filing_status_t NOT NULL, assurance_level assurance_t,
  incorporated_by_reference BOOLEAN, incorporation_evidence VARCHAR,
  location VARCHAR, document_kind VARCHAR, tier tier_t,
  acceptance_datetime TIMESTAMPTZ, filing_date DATE, knowledge_date DATE,
  period_start DATE, period_end DATE, byte_count BIGINT,
  parse_status coverage_t, normalizer_version VARCHAR,
  as_of TIMESTAMPTZ NOT NULL
);

CREATE TABLE facts (
  fact_id VARCHAR PRIMARY KEY, semantic_key VARCHAR NOT NULL,
  document_id VARCHAR NOT NULL, accession VARCHAR NOT NULL,
  entity_id VARCHAR NOT NULL, group_id VARCHAR NOT NULL,
  concept VARCHAR NOT NULL, taxonomy_namespace VARCHAR, taxonomy_version VARCHAR,
  canonical_concept VARCHAR NOT NULL, model_quantity VARCHAR,
  period_start DATE, period_end DATE NOT NULL, unit VARCHAR NOT NULL,
  currency VARCHAR, dimensions VARCHAR NOT NULL DEFAULT '{}',
  accounting_framework accounting_t NOT NULL,
  reporting_scope VARCHAR NOT NULL, source_perspective perspective_t NOT NULL,
  value DECIMAL(38,6), text_value VARCHAR, is_nil BOOLEAN NOT NULL DEFAULT false,
  explicit_zero BOOLEAN NOT NULL DEFAULT false, decimals VARCHAR,
  is_tagged BOOLEAN NOT NULL, locator VARCHAR NOT NULL,
  primary_statement_occurrence BOOLEAN,
  primary_statement_role VARCHAR,
  primary_statement_parenthetical BOOLEAN,
  occurrence_rank BIGINT NOT NULL, document_rank INTEGER NOT NULL DEFAULT 0,
  document_rank_source VARCHAR, source_document_id VARCHAR,
  acceptance_datetime TIMESTAMPTZ NOT NULL, knowledge_date DATE NOT NULL,
  filing_status filing_status_t NOT NULL, assurance_level assurance_t NOT NULL,
  location VARCHAR NOT NULL, tier tier_t NOT NULL, stage stage_t,
  coverage_state coverage_t NOT NULL,
  recast_cause recast_cause_t NOT NULL DEFAULT 'unknown',
  amends_accession VARCHAR, mapping_rule VARCHAR, mapping_evidence VARCHAR,
  as_of TIMESTAMPTZ NOT NULL,
  CHECK (NOT is_nil OR value IS NULL),
  CHECK (NOT explicit_zero OR (value IS NOT NULL AND value = 0))
);

CREATE TABLE observations (
  observation_id VARCHAR PRIMARY KEY, content_key VARCHAR NOT NULL,
  document_id VARCHAR NOT NULL, accession VARCHAR NOT NULL,
  group_id VARCHAR NOT NULL, entity_id VARCHAR NOT NULL,
  abstained BOOLEAN NOT NULL, abstention_reason VARCHAR,
  quote VARCHAR NOT NULL, locator VARCHAR NOT NULL,
  raw_byte_start BIGINT NOT NULL, raw_byte_end BIGINT NOT NULL,
  counterparty VARCHAR, counterparty_entity_id VARCHAR,
  counterparty_evidence counterparty_evidence_t,
  counterparty_method counterparty_method_t,
  payer VARCHAR, receiver VARCHAR,
  amount DECIMAL(38,6), amount_upper DECIMAL(38,6), unit VARCHAR, currency VARCHAR,
  amount_nature VARCHAR, amount_origin amount_origin_t, amount_qualifier amount_qualifier_t,
  tagged_fact_id VARCHAR, model_quantity VARCHAR,
  period_start DATE, period_end DATE, event_date DATE, event_type event_t,
  stage stage_t, instrument_key VARCHAR,
  family family_t, link_type link_type_t,
  block block_t, category_id category_t, measurement_basis VARCHAR,
  component_kind component_t, conditionality conditionality_t,
  trigger_description VARCHAR, trigger_occurred trigger_t, ultimate_obligor VARCHAR,
  seniority VARCHAR, recourse VARCHAR, is_ring_fenced BOOLEAN, flag_unknown_reason VARCHAR,
  vehicle_level BOOLEAN, judgment_sensitive BOOLEAN,
  issuer_treatment VARCHAR, issuer_treatment_quote VARCHAR,
  filing_status filing_status_t NOT NULL, assurance_level assurance_t NOT NULL,
  tier tier_t NOT NULL, location VARCHAR NOT NULL, knowledge_date DATE NOT NULL,
  source_perspective perspective_t NOT NULL, accounting_framework accounting_t NOT NULL,
  linkage_class linkage_class_t, linkage_quote VARCHAR,
  price_setting_participation BOOLEAN, sales_channel VARCHAR,
  standard_application VARCHAR, basis_break BOOLEAN, recast_cause recast_cause_t,
  event_observable VARCHAR, event_present BOOLEAN, as_of TIMESTAMPTZ NOT NULL,
  CHECK (raw_byte_start >= 0 AND raw_byte_end > raw_byte_start),
  CHECK (NOT abstained OR abstention_reason IS NOT NULL),
  CHECK (abstained OR amount IS NULL OR amount_origin IS NOT NULL),
  CHECK (amount_origin != 'tagged_reference' OR tagged_fact_id IS NOT NULL),
  CHECK (counterparty_evidence != 'derivable' OR counterparty_method IS NOT NULL),
  CHECK (conditionality != 'conditional' OR trigger_description IS NOT NULL),
  CHECK (event_observable IS NULL OR event_observable IN ('F1','F2','F3','F4','F5','F6','F7','F8','F9','F10'))
);

CREATE TABLE entities (
  entity_id VARCHAR NOT NULL, membership_id VARCHAR NOT NULL,
  alias_key VARCHAR NOT NULL DEFAULT 'none',
  legal_name VARCHAR NOT NULL, normalized_name VARCHAR NOT NULL,
  cik VARCHAR, jurisdiction VARCHAR, entity_status entity_state_t NOT NULL,
  group_id VARCHAR, economic_group_id VARCHAR,
  consolidation_treatment consolidation_t NOT NULL,
  combination_method VARCHAR, membership_start DATE, membership_end DATE,
  common_control_start DATE, legal_date DATE, knowledge_date DATE,
  alias VARCHAR, alias_start DATE, alias_end DATE,
  resolution_rule VARCHAR, evidence_document_id VARCHAR, evidence_locator VARCHAR,
  source_perspective perspective_t, as_of TIMESTAMPTZ NOT NULL,
  PRIMARY KEY (entity_id, membership_id, alias_key)
);

CREATE TABLE links (
  link_id VARCHAR PRIMARY KEY, edge_kind edge_kind_t,
  family family_t, type link_type_t,
  from_entity_id VARCHAR, to_entity_id VARCHAR, from_group_id VARCHAR, to_group_id VARCHAR,
  amount DECIMAL(38,6), unit VARCHAR, currency VARCHAR,
  period_start DATE, period_end DATE, event_date DATE,
  knowledge_date DATE, stage stage_t, event_type event_t,
  instrument_key VARCHAR, fact_id VARCHAR, observation_id VARCHAR,
  document_id VARCHAR, locator VARCHAR,
  filing_status filing_status_t, assurance_level assurance_t, tier tier_t,
  counterparty_evidence counterparty_evidence_t, accounting_framework accounting_t,
  source_perspective perspective_t, sales_channel VARCHAR,
  financing_state financing_state_t, financing_policy financing_policy_t,
  linkage_class linkage_class_t, linkage_evidence linkage_evidence_t,
  relationship_conclusion relationship_conclusion_t,
  relation_type relation_t, amount_a_id VARCHAR, amount_b_id VARCHAR,
  allocation DECIMAL(38,6), resolved BOOLEAN, resolution_evidence VARCHAR,
  pair_id VARCHAR, elimination_status VARCHAR,
  conditionality conditionality_t, trigger_description VARCHAR, trigger_occurred trigger_t,
  advance BOOLEAN, reciprocal_purchase BOOLEAN, wrong_way BOOLEAN,
  vehicle_level BOOLEAN, as_of TIMESTAMPTZ NOT NULL,
  CHECK (edge_kind != 'amount' OR (amount IS NOT NULL AND tier IN ('A','B','C','D')
    AND counterparty_evidence IN ('named','derivable') AND period_end IS NOT NULL)),
  CHECK (edge_kind != 'amount' OR family != 'financing' OR
    (tier IN ('A','B','C') AND stage IN ('drawn_or_paid','recognized'))),
  CHECK (relation_type IS NULL OR (amount_a_id IS NOT NULL AND amount_b_id IS NOT NULL))
);

-- measure_id_t et les contraintes de termes sont générés depuis la liste
-- fermée dans le schéma Python, avant chargement de ce fichier.
CREATE TABLE measures (
  measure measure_id_t NOT NULL, group_id VARCHAR NOT NULL,
  entity_id VARCHAR NOT NULL DEFAULT 'none', counterparty_id VARCHAR NOT NULL DEFAULT 'none',
  period_start VARCHAR NOT NULL DEFAULT 'none', period_end VARCHAR NOT NULL DEFAULT 'none',
  view view_t NOT NULL, as_of TIMESTAMPTZ NOT NULL,
  term VARCHAR NOT NULL DEFAULT 'none', breakdown_key VARCHAR NOT NULL DEFAULT 'none',
  financing_policy financing_policy_t NOT NULL DEFAULT 'none',
  constant_perimeter perimeter_t NOT NULL DEFAULT 'current', variant VARCHAR NOT NULL DEFAULT 'original',
  knowledge_date DATE,
  information_cutoff TIMESTAMPTZ,
  value DECIMAL(38,6), value_lower DECIMAL(38,6), value_upper DECIMAL(38,6), bound_basis VARCHAR,
  unit VARCHAR, currency VARCHAR, numerator DECIMAL(38,6), denominator DECIMAL(38,6),
  status measure_status_t NOT NULL, nd_reason VARCHAR, coverage_state coverage_t NOT NULL,
  evidence_profile VARCHAR, lineage VARCHAR NOT NULL DEFAULT '[]',
  numerator_coverage pair_coverage_t, denominator_coverage pair_coverage_t,
  financing_state financing_state_t, edge_structure edge_structure_t,
  linkage_evidence linkage_evidence_t, relationship_conclusion relationship_conclusion_t,
  outcome outcome_t, tier INTEGER NOT NULL DEFAULT 1,
  basis_break BOOLEAN, basis_break_reason VARCHAR, recast_cause recast_cause_t,
  unequal_period_length BOOLEAN, wrong_way BOOLEAN, price_setting_participation BOOLEAN,
  overlap_possible BOOLEAN, visible_pairs_count BIGINT,
  first_published_period DATE, first_period_available_at_the_time DATE,
  source_perspective perspective_t, accounting_framework accounting_t,
  PRIMARY KEY (measure, group_id, entity_id, counterparty_id, period_start, period_end,
    view, as_of, term, breakdown_key, financing_policy, constant_perimeter, variant),
  CHECK (status != 'not_determinable' OR nd_reason IS NOT NULL),
  CHECK (status NOT IN ('not_determinable','not_applicable','blocked_overlap') OR value IS NULL),
  CHECK (status != 'bounded' OR (value_lower IS NOT NULL AND value_upper IS NOT NULL AND bound_basis IS NOT NULL)),
  CHECK (value_lower IS NULL OR value_upper IS NULL OR value_lower <= value_upper)
  ,CHECK (period_start='none' OR try_cast(period_start AS DATE) IS NOT NULL)
  ,CHECK (period_end='none' OR try_cast(period_end AS DATE) IS NOT NULL)
);

CREATE TABLE controls (
  control control_id_t NOT NULL, group_id VARCHAR NOT NULL,
  period_start VARCHAR NOT NULL DEFAULT 'none', period_end VARCHAR NOT NULL DEFAULT 'none', view view_t NOT NULL,
  as_of TIMESTAMPTZ NOT NULL, breakdown_key VARCHAR NOT NULL DEFAULT 'none',
  variant VARCHAR NOT NULL DEFAULT 'original',
  status control_status_t NOT NULL, lhs DECIMAL(38,12), rhs DECIMAL(38,12),
  residual DECIMAL(38,12), tolerance DECIMAL(38,12), tolerance_basis tolerance_t NOT NULL,
  explanation_code VARCHAR, evidence VARCHAR NOT NULL DEFAULT '[]',
  PRIMARY KEY (control,group_id,period_start,period_end,view,as_of,breakdown_key,variant),
  CHECK (status NOT IN ('not_testable','mismatch') OR explanation_code IS NOT NULL)
);

CREATE TABLE exclusions (
  exclusion_id VARCHAR PRIMARY KEY, group_id VARCHAR, entity_id VARCHAR, counterparty_id VARCHAR,
  accession VARCHAR, document_id VARCHAR, locator VARCHAR, content_key VARCHAR,
  element_type VARCHAR NOT NULL, element_id VARCHAR NOT NULL,
  reason VARCHAR NOT NULL, detail VARCHAR, raw_line VARCHAR, invariant VARCHAR,
  coverage_state coverage_t, period_start DATE, period_end DATE,
  as_of TIMESTAMPTZ NOT NULL
);
