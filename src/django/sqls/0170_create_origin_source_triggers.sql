CREATE TRIGGER trg_set_origin_source_contributor
BEFORE INSERT ON api_contributor
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