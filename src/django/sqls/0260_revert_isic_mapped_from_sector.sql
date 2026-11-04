/*Drops the three-argument functions of 0260. The migration then re-runs
0256_isic_mapped_from_taxonomy.sql, which restores the two-argument
functions, the trigger function and the update trigger without sector.*/
DROP FUNCTION IF EXISTS isic_mapped_codes(VARCHAR[], VARCHAR[], VARCHAR[]);
DROP FUNCTION IF EXISTS isic_mapped_entries(
	VARCHAR[], VARCHAR[], VARCHAR[]
);
