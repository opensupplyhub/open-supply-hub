def filter(event)
  opened_at = event.get('opened_at')

  if opened_at.nil?
    event.remove('opened_at')
  end

  [event]
end

test 'opened_at filter with valid value' do
    in_event { { 'opened_at' => '2023-12-01T10:30:00Z' } }
  
    expect('sets opened_at field with the provided value') do |events|
        events.size == 1 &&
        events[0].get('opened_at') == '2023-12-01T10:30:00Z'
    end
end

test 'opened_at filter with nil value' do
    in_event { { 'opened_at' => nil } }
  
    expect('does not set opened_at field when value is nil') do |events|
        events.size == 1 &&
        !events[0].to_hash.key?('opened_at')
    end
end
