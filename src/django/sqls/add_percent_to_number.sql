CREATE OR REPLACE FUNCTION add_percent_to_number(total_count numeric, filtered_count numeric)
RETURNS text AS $$
DECLARE
BEGIN
    IF total_count = 0 THEN
        RETURN '0%';
    ELSE
        RETURN round(100.0 * filtered_count / total_count, 2) || '%';
    END IF;
END;
$$ LANGUAGE plpgsql;