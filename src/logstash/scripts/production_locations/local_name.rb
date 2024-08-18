def filter(event)
    local_name_value = event.get('local_name')

    is_local_name_value_valid = !local_name_value.nil? && !local_name_value.strip.empty?
    event.set('local_name', local_name_value) if is_local_name_value_valid

    return [event]
end
