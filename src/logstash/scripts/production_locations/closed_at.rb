def filter(event)
  closed_at_value = event.get('closed_at_value')

  if closed_at_value.nil?
      return [event]
  end

  # Normalize to YYYY-MM format.
  # Accepts values like '2023-12-01' or ISO8601 '2023-12-01T10:30:00Z'.
  begin
    t = Time.parse(closed_at_value.to_s)
    event.set('closed_at', t.strftime('%Y-%m'))
  rescue => e
    # If parsing fails, pass through original value (to avoid data loss).
    event.set('closed_at', closed_at_value)
  end

  return [event]
end

test 'closed_at filter with ISO datetime value' do
  in_event { { 'closed_at_value' => '2023-12-01T10:30:00Z' } }

  expect('sets closed_at field as strict date') do |events|
      events.size == 1 &&
      events[0].get('closed_at') == '2023-12'
  end
end

test 'closed_at filter with date string' do
  in_event { { 'closed_at_value' => '2023-12-01' } }

  expect('keeps closed_at field as date') do |events|
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
