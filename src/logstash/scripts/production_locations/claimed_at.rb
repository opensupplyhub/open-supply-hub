def filter(event)
    claimed_at_value = event.get('claimed_at_value')
  
    if claimed_at_value.nil?
        return [event]
    end

    event.set('claimed_at', claimed_at_value)

    return [event]
end

test 'claimed_at filter with valid value' do
    in_event { { 'claimed_at_value' => '2023-12-01T10:30:00Z' } }
  
    expect('sets claimed_at field with the provided value') do |events|
        events.size == 1 &&
        events[0].get('claimed_at') == '2023-12-01T10:30:00Z'
    end
end

test 'claimed_at filter with nil value' do
    in_event { { 'claimed_at_value' => nil } }
  
    expect('does not set claimed_at field when value is nil') do |events|
        events.size == 1 &&
        !events[0].to_hash.key?('claimed_at')
    end
end
