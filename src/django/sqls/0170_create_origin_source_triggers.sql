CREATE TRIGGER trg_set_origin_source_contributor
AFTER INSERT ON api_contributor
FOR EACH ROW
EXECUTE FUNCTION set_origin_source();

CREATE TRIGGER trg_set_origin_source_extendedfield
AFTER INSERT ON api_extendedfield
FOR EACH ROW
EXECUTE FUNCTION set_origin_source();

CREATE TRIGGER trg_set_origin_source_facility
AFTER INSERT ON api_facility
FOR EACH ROW
EXECUTE FUNCTION set_origin_source();

CREATE TRIGGER trg_set_origin_source_facilityactivityreport
AFTER INSERT ON api_facilityactivityreport
FOR EACH ROW
EXECUTE FUNCTION set_origin_source();

CREATE TRIGGER trg_set_origin_source_facilityalias
AFTER INSERT ON api_facilityalias
FOR EACH ROW
EXECUTE FUNCTION set_origin_source();

CREATE TRIGGER trg_set_origin_source_facilityclaim
AFTER INSERT ON api_facilityclaim
FOR EACH ROW
EXECUTE FUNCTION set_origin_source();

CREATE TRIGGER trg_set_origin_source_facilitylist
AFTER INSERT ON api_facilitylist
FOR EACH ROW
EXECUTE FUNCTION set_origin_source();

CREATE TRIGGER trg_set_origin_source_facilitylistitem
AFTER INSERT ON api_facilitylistitem
FOR EACH ROW
EXECUTE FUNCTION set_origin_source();

CREATE TRIGGER trg_set_origin_source_facilitymatch
AFTER INSERT ON api_facilitymatch
FOR EACH ROW
EXECUTE FUNCTION set_origin_source();

CREATE TRIGGER trg_set_origin_source_source
AFTER INSERT ON api_source
FOR EACH ROW
EXECUTE FUNCTION set_origin_source();

CREATE TRIGGER trg_set_origin_source_facilitylocation
AFTER INSERT ON api_facilitylocation
FOR EACH ROW
EXECUTE FUNCTION set_origin_source();

CREATE TRIGGER trg_set_origin_source_user
AFTER INSERT ON api_user
FOR EACH ROW
EXECUTE FUNCTION set_origin_source();