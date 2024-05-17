CREATE OR REPLACE PROCEDURE strip_all_triggers()
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    triggNameRecord RECORD;
    triggTableRecord RECORD;
BEGIN
    FOR triggNameRecord IN SELECT DISTINCT trigger_name FROM information_schema.triggers WHERE trigger_schema = 'public' LOOP
        FOR triggTableRecord IN SELECT DISTINCT event_object_table FROM information_schema.triggers WHERE trigger_name = triggNameRecord.trigger_name AND trigger_schema = 'public' LOOP
            RAISE NOTICE 'Dropping trigger: % on table: %', triggNameRecord.trigger_name, triggTableRecord.event_object_table;
            EXECUTE FORMAT('DROP TRIGGER %I ON public.%I;', triggNameRecord.trigger_name, triggTableRecord.event_object_table);
        END LOOP;
    END LOOP;
END;
$$;
