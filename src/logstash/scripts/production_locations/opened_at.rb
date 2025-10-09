def filter(event)
  opened_at_value = event.get('opened_at_value')

  if opened_at_value.nil?
      return [event]
  end

  event.set('opened_at', opened_at_value)

  return [event]
end

test 'opened_at filter with valid value' do
  in_event { { 'opened_at_value' => '2023-12-01T10:30:00Z' } }

  expect('sets opened_at field with the provided value') do |events|
      events.size == 1 &&
      events[0].get('opened_at') == '2023-12-01T10:30:00Z'
  end
end

test 'opened_at filter with nil value' do
  in_event { { 'opened_at_value' => nil } }

  expect('does not set opened_at field when value is nil') do |events|
      events.size == 1 &&
      !events[0].to_hash.key?('opened_at')
  end
end