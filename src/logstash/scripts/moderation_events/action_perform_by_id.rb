def filter(event)
    action_perform_by_id_value = event.get('action_perform_by_id_value')

    is_action_perform_by_id_valid = !action_perform_by_id_value.nil? && !action_perform_by_id_value.to_s.strip.empty?
    event.set('action_perform_by_id', action_perform_by_id_value) if is_action_perform_by_id_valid

    return [event]
end

test 'action_perform_by_id filter with existing action_perform_by_id_value' do
    in_event {
        {
            'action_perform_by_id_value' => 123
        }
    }
  
    expect('returns an object with action_type set') do |events|
        is_action_perform_by_id_value_present = events[0].get('action_perform_by_id_value') == 123
        is_action_perform_by_id_present = events[0].get('action_perform_by_id') == 123

        is_action_perform_by_id_value_present && is_action_perform_by_id_present
    end
end

test 'action_perform_by_id filter with nil action_perform_by_id_value' do
    in_event {
        {
            'action_perform_by_id_value' => nil,
        }
    }
  
    expect('returns the same object') do |events|
        is_action_perform_by_id_value_nil = events[0].get('action_perform_by_id_value').nil?
        is_action_perform_by_id_present = events[0].to_hash.key?('action_perform_by_id')

        is_action_perform_by_id_value_nil && !is_action_perform_by_id_present
    end
end
