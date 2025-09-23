def filter(event)
  closed_at_value = event.get('closed_at_value')

  if closed_at_value.nil?
      return [event]
  end

  event.set('closed_at', closed_at_value)

  return [event]
end

test 'closed_at filter with valid value' do
  in_event { { 'closed_at_value' => '2023-12-01T10:30:00Z' } }

  expect('sets closed_at field with the provided value') do |events|
      events.size == 1 &&
      events[0].get('closed_at') == '2023-12-01T10:30:00Z'
  end
end

test 'closed_at filter with nil value' do
  in_event { { 'closed_at_value' => nil } }

  expect('does not set closed_at field when value is nil') do |events|
      events.size == 1 &&
      !events[0].to_hash.key?('closed_at')
  end
end
