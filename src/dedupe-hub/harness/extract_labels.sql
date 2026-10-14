-- Extract moderator-adjudicated pairs for the matcher harness, stratified by
-- country so no single country dominates the training draw.
--
-- Why cap per country. The 2026-08 sample was drawn without country control and
-- came out 43.8% Mexico / 0.1% Korea, while production upload volume is 6.6%
-- Mexico and 22.8% Korea. Making that mix explicit rather than accidental is
-- worth doing for any future extraction.
--
-- READ THIS BEFORE ASSUMING THE CAP FIXES ANYTHING. The hypothesis that Korea
-- underperforms BECAUSE it is under-represented in training was tested and
-- REFUTED. Rebalancing the training draw to a 4,000-per-country cap made every
-- country worse, not better:
--
--                           auto     decisions   new facilities
--   KOREA
--     production            96.0%           29             0.8%
--     retrain (MX-heavy)    89.7%          135             0.8%
--     retrain (stratified)  52.7%          773             0.7%
--   BANGLADESH
--     production            50.8%          173            27.3%
--     retrain (MX-heavy)    66.5%          129            20.2%
--     retrain (stratified)  53.3%          317            17.8%
--
-- Stratification cost Bangladesh its entire auto-match gain and took Korea from
-- bad to unusable. The model did not learn Korea; it learned to be uniformly
-- less confident. The volume/training mismatch was a correlation, not a cause.
--
-- Separately, Korea's apparent regression at a fixed 0.8 threshold is itself a
-- threshold artifact rather than a model deficit: at equal auto-match rate the
-- two models agree on 98.6% of items and pick a different facility on zero.
--
-- So: cap the EXTRACTION to keep the mix deliberate, but do not rebalance the
-- training DRAW by country expecting it to recover a weak country. The two are
-- different decisions and only the first is safe.
--
-- The imbalance is not a sampling bug, it is structural: CONFIRMED/REJECTED
-- rows exist only where a human was asked, and humans are asked only where the
-- matcher was unsure. Korea has 228,704 match rows but 798 human adjudications
-- because production already auto-matches 96% of Korean uploads. So countries
-- the matcher handles well are invisible to retraining, and a retrain can
-- quietly regress them. Capping per country cannot create Korean labels, but
-- it stops Mexico from crowding out every country that does have some.
--
-- :per_country is the cap. Countries with fewer labels contribute all they have.
--
--   psql -v per_country=4000 -f extract_labels.sql

\set per_country :per_country

copy (
    with adjudicated as (
        select
            m.id              as match_id,
            m.status,
            m.confidence,
            i.country_code,
            coalesce(nullif(i.clean_name, ''), i.name)       as item_clean_name,
            i.name                                           as item_name,
            coalesce(nullif(i.clean_address, ''), i.address) as item_clean_address,
            i.address                                        as item_address,
            lower(i.country_code)                            as item_country,
            f.name                                           as fac_name,
            f.address                                        as fac_address,
            lower(f.country_code)                            as fac_country,
            -- deterministic ordering so reruns reproduce the same draw
            row_number() over (
                partition by i.country_code
                order by md5(m.id::text)
            ) as rn
        from api_facilitymatch m
        join api_facilitylistitem i on i.id = m.facility_list_item_id
        join api_facility f         on f.id = m.facility_id
        where m.status in ('CONFIRMED', 'REJECTED')
          and coalesce(nullif(i.clean_name, ''), i.name) is not null
          and f.name is not null
          and i.country_code is not null
    )
    select
        match_id, status, confidence,
        item_clean_name, item_name, item_clean_address, item_address, item_country,
        fac_name, fac_address, fac_country
    from adjudicated
    where rn <= :per_country
) to stdout with csv header;
