-- Les sélections et mesures ne s’appuient jamais sur fy/fp.
CREATE MACRO exact_ratio6(a,b) AS (
 WITH units AS (
  SELECT CAST(a*1000000 AS HUGEINT) AS n, CAST(b*1000000 AS HUGEINT) AS d
 ), scaled AS (
  SELECT abs(n)*1000000 AS n, abs(d) AS d, sign(n)*sign(d) AS s FROM units WHERE d<>0
 ), quotient AS (
  SELECT n//d AS q, n%d AS r,d,s FROM scaled
 ) SELECT CAST(s*(q+CASE WHEN 2*r>d OR (2*r=d AND q%2=1) THEN 1 ELSE 0 END) AS DECIMAL(38,0))
   * CAST('0.000001' AS DECIMAL(7,6)) FROM quotient
);

-- Candidates fixed before controls; multiple values in the SAME filing are
-- quarantined instead of resolved by a latest-occurrence tiebreak.
-- The API or another physical occurrence cannot readmit the same conflicting
-- semantic identity from that filing. A later corrected filing remains usable.
CREATE VIEW conflicting_semantics AS
SELECT DISTINCT f.accession,f.semantic_key FROM facts f
JOIN semantic_fact_quarantines q USING (fact_id);

-- Compare the deposited rounding intervals, not unequal rounded centres.
-- Missing precision never supplies an invented tolerance.
CREATE TEMP TABLE fact_precision_groups AS
SELECT f.*,
 precision_radius(decimals) AS rounding_radius,
 CASE WHEN upper(decimals)='INF' THEN 100000
      ELSE coalesce(try_cast(decimals AS INTEGER),-100000) END AS numeric_precision,
 count(DISTINCT value) OVER w AS distinct_values,
 count(*) FILTER (WHERE value IS NOT NULL AND precision_radius(decimals) IS NULL) OVER w AS unknown_precisions,
 count(*) FILTER (WHERE value IS NOT NULL AND upper(decimals)='INF') OVER w AS exact_values,
 max(value-precision_radius(decimals)) OVER w AS max_lower,
 min(value+precision_radius(decimals)) OVER w AS min_upper
 ,min(value+precision_radius(decimals)) FILTER (WHERE upper(decimals)!='INF') OVER w AS finite_min_upper
FROM facts f WINDOW w AS (PARTITION BY accession,semantic_key,document_rank);

CREATE TEMP TABLE eligible_facts AS
SELECT * EXCLUDE (value,coverage_state,rounding_radius,distinct_values,unknown_precisions,exact_values,max_lower,min_upper,finite_min_upper),
 CASE WHEN EXISTS (SELECT 1 FROM conflicting_semantics q
                    WHERE q.accession=f.accession AND q.semantic_key=f.semantic_key)
        OR (distinct_values>1 AND (unknown_precisions>0 OR max_lower>min_upper
             OR (max_lower=min_upper AND (exact_values=0 OR finite_min_upper=min_upper))))
      THEN NULL ELSE value END AS value,
 CASE WHEN EXISTS (SELECT 1 FROM conflicting_semantics q
                    WHERE q.accession=f.accession AND q.semantic_key=f.semantic_key)
        OR (distinct_values>1 AND (unknown_precisions>0 OR max_lower>min_upper
             OR (max_lower=min_upper AND (exact_values=0 OR finite_min_upper=min_upper))))
      THEN 'conflicting' ELSE coverage_state END AS coverage_state
FROM fact_precision_groups f WHERE tier IN ('A','B','C','D') AND filing_status='filed' AND NOT is_nil
 AND document_rank>=-1
 AND acceptance_datetime<=as_of AND knowledge_date<=as_of::DATE;

CREATE TEMP TABLE eligible_instance_occurrences AS
SELECT * FROM eligible_facts WHERE document_rank>=0
QUALIFY row_number() OVER (PARTITION BY accession,semantic_key
 ORDER BY primary_statement_occurrence DESC NULLS LAST,document_rank DESC,numeric_precision DESC,occurrence_rank DESC)=1;

CREATE TEMP TABLE selected_revised AS
SELECT * FROM eligible_facts
QUALIFY row_number() OVER (PARTITION BY semantic_key
 ORDER BY acceptance_datetime DESC,accession DESC,document_rank DESC,numeric_precision DESC,occurrence_rank DESC)=1;
