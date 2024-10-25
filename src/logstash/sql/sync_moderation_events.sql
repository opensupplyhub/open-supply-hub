SELECT
	ame.uuid AS moderation_id,
	ame.os_id,
	ame.contributor_id,
	(
	SELECT
		name
	FROM
		api_contributor ac
	WHERE
		id = ame.contributor_id) AS contributor_name,
	ame.claim_id,
	ame.cleaned_data::TEXT,
	ame.request_type,
	ame.source,
	ame.status,
	ame.status_change_date,
	ame.created_at,
	ame.updated_at
FROM
	api_moderationevent ame
WHERE
	ame.updated_at > :sql_last_value
	AND ame.updated_at < CURRENT_TIMESTAMP
ORDER BY
	ame.updated_at ASC