select af.id,
  af.name,
  af.address,
  af.country_code,
  ST_Y(af.location) as latitude,
  ST_X(af.location) as longitude,
  af.is_closed,
  af.updated_at,
  af.created_at
  -- (
  --   select ae.value->>'raw_values'
  --   from api_extendedfield ae
  --   where ae.facility_id = af.id
  --     and ae.field_name = 'facility_type'
  --   order by created_at
  --   limit 1
  -- ) as facility_type,
  -- (
  --   select ae.value->>'raw_values'
  --   from api_extendedfield ae
  --   where ae.facility_id = af.id
  --     and ae.field_name = 'product_type'
  --   order by created_at
  --   limit 1
  -- ) as product_type,
  -- (
  --   select ae.value->>'raw_values'
  --   from api_extendedfield ae
  --   where ae.facility_id = af.id
  --     and ae.field_name = 'processing_type'
  --   order by created_at
  --   limit 1
  -- ) as processing_type,
  -- (
  --   select ae.value->>'name'
  --   from api_extendedfield ae
  --   where ae.facility_id = af.id
  --     and ae.field_name = 'parent_company'
  --   order by created_at
  --   limit 1
  -- ) as parent_company,
  -- (
  --   select ae.value
  --   from api_extendedfield ae
  --   where ae.facility_id = af.id
  --     and ae.field_name = 'number_of_workers'
  --   order by created_at
  --   limit 1
  -- ) as number_of_workers
from api_facility af
WHERE af.updated_at > :sql_last_value
  AND af.updated_at < CURRENT_TIMESTAMP
ORDER BY af.updated_at ASC
