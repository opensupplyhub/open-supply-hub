def filter(event)
    name_local_value = event.get('name_local_value')

    is_name_local_value_valid = !name_local_value.nil? && !name_local_value.strip.empty?
    event.set('local_name', name_local_value) if is_name_local_value_valid

    return [event]
end
