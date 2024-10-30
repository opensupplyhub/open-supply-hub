def filter(event)
    source_value = event.get('source_value')

    is_source_value_valid = !source_value.nil? && !source_value.strip.empty?
    event.set('source', source_value) if is_source_value_valid

    return [event]
end

test 'source filter with valid source_value' do
    in_event {
        {
            'source_value' => 'SLC',
            'status' => 'PENDING'
        }
    }
  
    expect('returns an object with source set') do |events|
        is_source_value_present = events[0].get('source_value') == 'SLC'
        is_status_present = events[0].get('status') == 'PENDING'
        is_source_present = events[0].get('source') == 'SLC'

        is_source_value_present && is_status_present && is_source_present
    end
end

test 'source filter with nil source_value' do
    in_event {
        {
            'source_value' => nil,
            'status' => 'PENDING'
        }
    }
  
    expect('returns the same object') do |events|
        is_source_value_nil = events[0].get('source_value').nil?
        is_status_present = events[0].get('status') == 'PENDING'
        is_source_present = events[0].to_hash.key?('source')

        is_source_value_nil && is_status_present && !is_source_present
    end
end
