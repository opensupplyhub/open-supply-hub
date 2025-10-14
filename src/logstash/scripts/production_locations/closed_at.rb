require_relative 'date_formatter_helper'
require_relative 'date_field_test_helper'

def filter(event)
  # Normalize to year-month format (YYYY-MM).
  DateFormatterHelper.format_date_field(event, 'closed_at_value', 'closed_at', '%Y-%m')
  return [event]
end

DateFieldTestHelper.run_tests('closed_at_value', 'closed_at', '2023-12', 'year-month')
