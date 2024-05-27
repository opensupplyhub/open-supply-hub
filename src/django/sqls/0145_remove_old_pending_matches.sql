CREATE OR REPLACE PROCEDURE remove_old_pending_matches()
LANGUAGE plpgsql
AS $$
BEGIN
    -- Delete the matches that have status as PENDING and updated_at more than 30 days ago
    DELETE FROM api_facilitymatch
    WHERE api_facilitymatch.status = 'PENDING' 
    AND api_facilitymatch.updated_at < (NOW() - interval '1 month');

    DELETE FROM api_facilitymatchtemp 
    WHERE api_facilitymatchtemp.status = 'PENDING'
    AND api_facilitymatchtemp.updated_at < (NOW() - interval '1 month');
    
END;
$$;
