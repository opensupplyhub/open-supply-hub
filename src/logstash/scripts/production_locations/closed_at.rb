def filter(event)
  closed_at = event.get('closed_at')

  if closed_at.nil?
    event.remove('closed_at')
  end

  [event]
end

test 'closed_at filter with valid value' do
    in_event { { 'closed_at' => '2023-12-01T10:30:00Z' } }
  
    expect('sets closed_at field with the provided value') do |events|
        events.size == 1 &&
        events[0].get('closed_at') == '2023-12-01T10:30:00Z'
    end
end

test 'closed_at filter with nil value' do
    in_event { { 'closed_at' => nil } }
  
    expect('does not set closed_at field when value is nil') do |events|
        events.size == 1 &&
        !events[0].to_hash.key?('closed_at')
    end
end
