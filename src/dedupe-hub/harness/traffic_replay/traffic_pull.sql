-- Pull a random sample of real uploads, and the facility index to search them against. OSDEV-3277 traffic test.
--
-- Unlike the labeled-pairs extract, the sample is NOT limited to uploads that reached a moderator: it takes
-- uploads the system handled by itself as well (auto-matched, new facility) and ones sent to review, because
-- the labeled pairs only exist for what the old model found uncertain.
--
-- Two files come out:
--   traffic_sample.csv  one row per sampled upload: item_id, country, name, address, the recorded item
--                       status, the facility production linked it to, whether that upload created the
--                       facility, and the item's match rows ("<id>:<status>;...")
--   traffic_index.csv   what dedupe-hub indexes at train time (get_canonical_items), MINUS anything that
--                       belongs to a sampled upload: the facility each sampled upload created and each
--                       sampled upload's own match spelling. Without that, an upload would find itself.
--
-- Usage (from the folder you want the CSVs in):
--   psql -q -U <user> -d <database> -v per_country=400 -v n_countries=12 -v since=2025-01-01 \
--        -f traffic_pull.sql
-- per_country: uploads sampled from each country; n_countries: the busiest N countries since `since`.
-- The draw uses a fixed seed, so running it again on the same data gives the same sample.
--
-- NOT RUN. Written from the table and column names in src/dedupe-hub/api/app/database/models; check the
-- first rows of both files before relying on them.
\set ON_ERROR_STOP on

select setseed(0.3277);

create temp table traffic_sample as
with usable as (
    select li.id as item_id,
           lower(li.country_code) as country,
           li.name,
           li.address,
           li.status as item_status,
           li.facility_id as recorded_facility,
           coalesce(f.created_from_id = li.id, false) as created_facility
    from api_facilitylistitem li
    left join api_facility f on f.id = li.facility_id
    where li.status in ('MATCHED', 'POTENTIAL_MATCH', 'CONFIRMED_MATCH')
      and li.created_at >= :'since'
      and coalesce(li.name, '') <> ''
      and coalesce(li.country_code, '') <> ''
      and coalesce(f.is_candidate, false) is false
), busiest as (
    select country from usable group by country order by count(*) desc limit :n_countries
), ranked as (
    select u.*, row_number() over (partition by u.country order by random()) as rn
    from usable u
    where u.country in (select country from busiest)
)
select item_id, country, name, address, item_status, recorded_facility, created_facility
from ranked
where rn <= :per_country;

\copy (select s.*, (select string_agg(m.id::text || ':' || m.status, ';' order by m.id) from api_facilitymatch m where m.facility_list_item_id = s.item_id) as matches from traffic_sample s order by country, item_id) to 'traffic_sample.csv' csv header

-- 'facility' rows carry the facility's own record; 'match' rows are one confirmed spelling each
-- (dedupe-hub gives those the synthetic id <facility>_MATCH-<match id>).
\copy (select 'facility' as kind, f.id as facility_id, null::int as match_id, lower(f.country_code) as country, f.name, f.address from api_facility f where f.is_candidate is false and f.created_from_id not in (select item_id from traffic_sample) union all select 'match', m.facility_id, m.id, lower(li.country_code), li.name, li.address from api_facilitymatch m join api_facilitylistitem li on li.id = m.facility_list_item_id join api_facility f on f.id = m.facility_id where m.status = 'CONFIRMED' and f.is_candidate is false and li.id not in (select item_id from traffic_sample) and f.created_from_id not in (select item_id from traffic_sample)) to 'traffic_index.csv' csv header
