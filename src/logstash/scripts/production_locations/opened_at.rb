def filter(event)
  opened_at_value = event.get('opened_at_value')

  if opened_at_value.nil?
      return [event]
  end

  # Normalize to year format (YYYY).
  # Accepts values like '2023-12-01' or ISO8601 '2023-12-01T10:30:00Z'.
  begin
    t = Time.parse(opened_at_value.to_s)
    event.set('opened_at', t.strftime('%Y'))
  rescue => e
    # If parsing fails, pass through original value (to avoid data loss)
    event.set('opened_at', opened_at_value)
  end

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
