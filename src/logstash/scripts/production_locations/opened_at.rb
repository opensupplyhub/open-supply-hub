require_relative 'date_formatter_helper'

def filter(event)
  # Normalize to year format (YYYY).
  DateFormatterHelper.format_date_field(event, 'opened_at_value', 'opened_at', '%Y')
  return [event]
end

test 'opened_at filter with ISO datetime value' do
  in_event { { 'opened_at_value' => '2023-12-01T10:30:00Z' } }

  expect('sets opened_at field as year') do |events|
      events.size == 1 &&
      events[0].get('opened_at') == '2023'
  end
end

test 'opened_at filter with date string' do
  in_event { { 'opened_at_value' => '2023-12-01' } }

  expect('sets opened_at field as year') do |events|
      events.size == 1 &&
      events[0].get('opened_at') == '2023'
  end
end

test 'opened_at filter with nil value' do
  in_event { { 'opened_at_value' => nil } }

  expect('does not set opened_at field when value is nil') do |events|
      events.size == 1 &&
      !events[0].to_hash.key?('opened_at')
  end
end
