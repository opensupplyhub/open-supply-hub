CREATE TRIGGER trg_set_origin_source_contributor
BEFORE INSERT ON api_contributor
FOR EACH ROW
EXECUTE FUNCTION set_origin_source();

CREATE TRIGGER trg_set_origin_source_extendedfield
BEFORE INSERT ON api_extendedfield
FOR EACH ROW
EXECUTE FUNCTION set_origin_source();

CREATE TRIGGER trg_set_origin_source_facility
BEFORE INSERT ON api_facility
FOR EACH ROW
EXECUTE FUNCTION set_origin_source();

CREATE TRIGGER trg_set_origin_source_facilityactivityreport
BEFORE INSERT ON api_facilityactivityreport
FOR EACH ROW
EXECUTE FUNCTION set_origin_source();

CREATE TRIGGER trg_set_origin_source_facilityalias
BEFORE INSERT ON api_facilityalias
FOR EACH ROW
EXECUTE FUNCTION set_origin_source();

CREATE TRIGGER trg_set_origin_source_facilityclaim
BEFORE INSERT ON api_facilityclaim
FOR EACH ROW
EXECUTE FUNCTION set_origin_source();

CREATE TRIGGER trg_set_origin_source_facilitylist
BEFORE INSERT ON api_facilitylist
FOR EACH ROW
EXECUTE FUNCTION set_origin_source();

CREATE TRIGGER trg_set_origin_source_facilitylistitem
BEFORE INSERT ON api_facilitylistitem
FOR EACH ROW
EXECUTE FUNCTION set_origin_source();

CREATE TRIGGER trg_set_origin_source_facilitymatch
BEFORE INSERT ON api_facilitymatch
FOR EACH ROW
EXECUTE FUNCTION set_origin_source();

CREATE TRIGGER trg_set_origin_source_source
BEFORE INSERT ON api_source
FOR EACH ROW
EXECUTE FUNCTION set_origin_source();

CREATE TRIGGER trg_set_origin_source_facilitylocation
BEFORE INSERT ON api_facilitylocation
FOR EACH ROW
EXECUTE FUNCTION set_origin_source();

CREATE TRIGGER trg_set_origin_source_user
BEFORE INSERT ON api_user
FOR EACH ROW
EXECUTE FUNCTION set_origin_source();

CREATE TRIGGER trg_set_origin_source_producttype
BEFORE INSERT ON api_producttype
FOR EACH ROW
EXECUTE FUNCTION set_origin_source();

CREATE TRIGGER trg_set_origin_source_sector
BEFORE INSERT ON api_sector
FOR EACH ROW
EXECUTE FUNCTION set_origin_source();

CREATE TRIGGER trg_set_origin_source_sectorgroup
BEFORE INSERT ON api_sectorgroup
FOR EACH ROW
EXECUTE FUNCTION set_origin_source();

CREATE TRIGGER trg_set_origin_source_historicalcontributor
BEFORE INSERT ON api_historicalcontributor
FOR EACH ROW
EXECUTE FUNCTION set_origin_source();

CREATE TRIGGER trg_set_origin_source_historicalextendedfield
BEFORE INSERT ON api_historicalextendedfield
FOR EACH ROW
EXECUTE FUNCTION set_origin_source();

CREATE TRIGGER trg_set_origin_source_historicalfacility
BEFORE INSERT ON api_historicalfacility
FOR EACH ROW
EXECUTE FUNCTION set_origin_source();

CREATE TRIGGER trg_set_origin_source_historicalfacilityactivityreport
BEFORE INSERT ON api_historicalfacilityactivityreport
FOR EACH ROW
EXECUTE FUNCTION set_origin_source();

CREATE TRIGGER trg_set_origin_source_historicalfacilityalias
BEFORE INSERT ON api_historicalfacilityalias
FOR EACH ROW
EXECUTE FUNCTION set_origin_source();

CREATE TRIGGER trg_set_origin_source_historicalfacilityclaim
BEFORE INSERT ON api_historicalfacilityclaim
FOR EACH ROW
EXECUTE FUNCTION set_origin_source();

CREATE TRIGGER trg_set_origin_source_historicalfacilitymatch
BEFORE INSERT ON api_historicalfacilitymatch
FOR EACH ROW
EXECUTE FUNCTION set_origin_source();