def filter(event)
    os_id_value = event.get('os_id_value')

    is_os_id_value_valid = !os_id_value.nil?
    event.set('os_id', os_id_value) if is_os_id_value_valid

    return [event]
end