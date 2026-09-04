/*
OSDEV-3430 (follow-up to OSDEV-3428). index_facility_type /
index_processing_type (0231, OSDEV-3189) count extended fields attached
to an APPROVED claim as well as fields backed by an active match, so
the facility_type and processing_type columns of api_facilityindex also
depend on api_facilityclaim. perform_facility_claim_indexing was never
updated for that dependency: a claim approval or revocation that does
not touch extended fields left both columns stale. This file re-creates
the procedure with the two columns added.
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
	facility_type,
	processing_type,
	updated_at) =
(
	SELECT
COALESCE((SELECT array_agg(approved_claim_id) FROM index_approved_claim_ids(af.id)),'{}'), -- approved_claim_ids
COALESCE((SELECT array_agg(DISTINCT(sector)) FROM index_sector(af.id)), '{}'), -- sector
COALESCE((SELECT approved_claim FROM index_approved_claim(af.id))), -- approved_claim
COALESCE((SELECT claim_info FROM index_claim_info(af.id))), -- claim_info
COALESCE((SELECT array_agg(extended_field) FROM index_extended_fields(af.id)), '{}'), -- extended_fields
COALESCE((SELECT array_agg(claim_sector) FROM index_claim_sectors(af.id)), '{}'), -- claim_sectors
COALESCE((SELECT array_agg(DISTINCT(facility_type)) FROM index_facility_type(af.id)), '{}'), -- facility_type
COALESCE((SELECT array_agg(DISTINCT(processing_type)) FROM index_processing_type(af.id)), '{}'), -- processing_type
now() -- updated_at
FROM api_facility af
WHERE
af.id = afin.id)
WHERE
afin.id = facility_identifier;
END;

$body$;
