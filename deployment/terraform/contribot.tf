#
# ContriBot DynamoDB state table
#
# One item per facility list (hash key list_id), plus a reserved __CURSOR__ item
# that stores last_list_id for O(1) resume. Facility-list items also store
# contributor_id, list_name, status, started_at, finished_at, and attempt_count.
# fetch_lists reads/advances the cursor and writes PENDING rows before process_list
# runs. retry_failed_lists scans FAILED rows and starts the Map without moving the cursor.
#

resource "aws_dynamodb_table" "contribot_state" {
  name         = "contribot${local.short}State"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "list_id"

  attribute {
    name = "list_id"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled = true
  }

  tags = merge(local.default_tags, {
    Name = "contribotState"
  })
}
