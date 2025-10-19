require_relative 'date_filter_helpers'

def filter(event)
  # Normalize to YYYY-MM format.
  # Accepts values like '2023-12-01' or ISO8601 '2023-12-01T10:30:00Z'.
  normalize_date_field(event, 'closed_at_value', 'closed_at', '%Y-%m')
  [event]
end

define_date_filter_tests('closed_at_value', 'closed_at', '2023-12')
