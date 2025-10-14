require_relative 'date_formatter_helper'
require_relative 'date_field_test_helper'

def filter(event)
  # Normalize to year format (YYYY).
  DateFormatterHelper.format_date_field(event, 'opened_at_value', 'opened_at', '%Y')
  return [event]
end

DateFieldTestHelper.run_tests('opened_at_value', 'opened_at', '2023', 'year')
