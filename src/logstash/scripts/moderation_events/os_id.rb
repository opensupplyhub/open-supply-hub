def filter(event)
    os_id_value = event.get('os_id_value')

    is_os_id_value_valid = !os_id_value.nil?
    event.set('os_id', os_id_value) if is_os_id_value_valid

    return [event]
end

test 'os_id filter with valid os_id_value' do
    in_event {
        {
            'os_id_value' => 'ES20242927JKGKW',
            'status' => 'PENDING'
        }
    }
  
    expect('returns an object with os_id set') do |events|
        is_os_id_value_present = (
            events[0].get('os_id_value') == 'ES20242927JKGKW'
        )
        is_status_present = events[0].get('status') == 'PENDING'
        is_os_id_present = events[0].get('os_id') == 'ES20242927JKGKW'

        is_os_id_value_present && is_status_present && is_os_id_present
    end
end

test 'os_id filter with nil os_id_value' do
    in_event {
        {
            'os_id_value' => nil,
            'status' => 'PENDING'
        }
    }
  
    expect('returns the same object') do |events|
        is_os_id_value_nil = events[0].get('os_id_value').nil?
        is_status_present = events[0].get('status') == 'PENDING'
        is_os_id_present = events[0].to_hash.key?('os_id')

        is_os_id_value_nil && is_status_present && !is_os_id_present
    end
end
