/*
OSDEV-3430 revert: restores perform_facility_claim_indexing to its
previous definition (without facility_type / processing_type).
*/

CREATE OR REPLACE
PROCEDURE perform_facility_claim_indexing(facility_identifier TEXT)
LANGUAGE plpgsql
AS $body$

BEGIN
UPDATE
	api_facilityindex afin
SET
	(
	approved_claim_ids,
	sector,
	approved_claim,
	claim_info,
	extended_fields,
	claim_sectors,
	updated_at) =
(
	SELECT
COALESCE((SELECT array_agg(approved_claim_id) FROM index_approved_claim_ids(af.id)),'{}'), -- approved_claim_ids
COALESCE((SELECT array_agg(DISTINCT(sector)) FROM index_sector(af.id)), '{}'), -- sector
COALESCE((SELECT approved_claim FROM index_approved_claim(af.id))), -- approved_claim
COALESCE((SELECT claim_info FROM index_claim_info(af.id))), -- claim_info
COALESCE((SELECT array_agg(extended_field) FROM index_extended_fields(af.id)), '{}'), -- extended_fields
COALESCE((SELECT array_agg(claim_sector) FROM index_claim_sectors(af.id)), '{}'), -- claim_sectors
now() -- updated_at
FROM api_facility af
WHERE
af.id = afin.id)
WHERE
afin.id = facility_identifier;
END;

$body$;
