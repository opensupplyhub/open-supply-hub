def filter(event)
    action_type_value = event.get('action_type_value')

    is_action_type_value_valid = !action_type_value.nil? && !action_type_value.strip.empty?
    event.set('action_type', action_type_value) if is_action_type_value_valid

    return [event]
end

test 'action_type filter with valid action_type_value' do
    in_event {
        {
            'action_type_value' => 'MATCHED',
            'status' => 'APPROVED'
        }
    }
  
    expect('returns an object with action_type set') do |events|
        is_action_type_value_present = events[0].get('action_type_value') == 'MATCHED'
        is_status_present = events[0].get('status') == 'APPROVED'
        is_action_type_present = events[0].get('action_type') == 'MATCHED'

        is_action_type_value_present && is_status_present && is_action_type_present
    end
end

test 'action_type filter with nil action_type_value' do
    in_event {
        {
            'action_type_value' => nil,
            'status' => 'PENDING'
        }
    }
  
    expect('returns the same object') do |events|
        is_action_type_value_nil = events[0].get('action_type_value').nil?
        is_status_present = events[0].get('status') == 'PENDING'
        is_action_type_present = events[0].to_hash.key?('action_type')

        is_action_type_value_nil && is_status_present && !is_action_type_present
    end
end
