def filter(event)
    status_change_date_value = event.get('status_change_date_value')

    is_status_change_date_value_valid = !status_change_date_value.nil?
    if is_status_change_date_value_valid
        event.set('status_change_date', status_change_date_value)
    end

    return [event]
end

test 'status_change_date filter with valid status_change_date_value' do
    in_event {
        {
            'status_change_date_value' => '2024-10-24T14:54:39.024924Z',
            'status' => 'PENDING'
        }
    }
  
    expect('returns an object with status_change_date set') do |events|
        is_status_change_date_value_present = (
            events[0].get('status_change_date_value') ==
            '2024-10-24T14:54:39.024924Z'
        )
        is_status_present = events[0].get('status') == 'PENDING'
        is_status_change_date_present = (
            events[0].get('status_change_date') ==
            '2024-10-24T14:54:39.024924Z'
        )

        result = (
            is_status_change_date_value_present &&
            is_status_present &&
            is_status_change_date_present
        )

        result
    end
end

test 'status_change_date filter with nil status_change_date_value' do
    in_event {
        {
            'status_change_date_value' => nil,
            'status' => 'PENDING'
        }
    }
  
    expect('returns the same object') do |events|
        is_status_change_date_value_nil = (
            events[0].get('status_change_date_value').nil?
        )
        is_status_present = events[0].get('status') == 'PENDING'
        is_status_change_date_present = (
            events[0].to_hash.key?('status_change_date')
        )

        result = (
            is_status_change_date_value_nil &&
            is_status_present &&
            !is_status_change_date_present
        )

        result
    end
end
