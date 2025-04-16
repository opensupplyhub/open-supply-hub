SELECT
	ame.uuid AS moderation_id,
	ame.os_id AS os_id_value,
	ame.contributor_id,
	ac.name AS contributor_name,
	ame.claim_id AS claim_id_value,
	ame.cleaned_data::TEXT AS cleaned_data_value,
	ame.request_type,
	ame.source AS source_value,
	ame.action_type AS action_type_value,
	ame.action_perform_by_id AS action_perform_by_id_value,
	ame.status,
	ame.status_change_date AS status_change_date_value,
	ame.created_at,
	ame.updated_at
FROM
	api_moderationevent ame
LEFT JOIN api_contributor AS ac
ON
	ac.id = ame.contributor_id
WHERE
	ame.updated_at > :sql_last_value
	AND ame.updated_at < CURRENT_TIMESTAMP
ORDER BY
	ame.updated_at ASC
