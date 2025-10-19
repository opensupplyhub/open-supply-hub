require_relative 'date_filter_helpers'

def filter(event)
  # Normalize to YYYY format.
  # Accepts values like '2023-12-01' or ISO8601 '2023-12-01T10:30:00Z'.
  normalize_date_field(event, 'opened_at_value', 'opened_at', '%Y')
  [event]
end

define_date_filter_tests('opened_at_value', 'opened_at', '2023')