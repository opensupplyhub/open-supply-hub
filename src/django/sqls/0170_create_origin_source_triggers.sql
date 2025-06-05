CREATE TRIGGER trg_set_origin_source_contributor
BEFORE INSERT ON api_contributor
FOR EACH ROW
EXECUTE FUNCTION set_origin_source();

CREATE TRIGGER trg_set_origin_source_facility
BEFORE INSERT ON api_facility
FOR EACH ROW
EXECUTE FUNCTION set_origin_source();