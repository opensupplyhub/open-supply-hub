require_relative 'date_formatter_helper'

def filter(event)
  # Normalize to year-month format (YYYY-MM).
  DateFormatterHelper.format_date_field(event, 'closed_at_value', 'closed_at', '%Y-%m')
  return [event]
end

test 'closed_at filter with ISO datetime value' do
  in_event { { 'closed_at_value' => '2023-12-01T10:30:00Z' } }

  expect('sets closed_at field as year-month') do |events|
      events.size == 1 &&
      events[0].get('closed_at') == '2023-12'
  end
end

test 'closed_at filter with date string' do
  in_event { { 'closed_at_value' => '2023-12-01' } }

  expect('sets closed_at field as year-month') do |events|
      events.size == 1 &&
      events[0].get('closed_at') == '2023-12'
  end
end

test 'closed_at filter with nil value' do
  in_event { { 'closed_at_value' => nil } }

  expect('does not set closed_at field when value is nil') do |events|
      events.size == 1 &&
      !events[0].to_hash.key?('closed_at')
  end
end
