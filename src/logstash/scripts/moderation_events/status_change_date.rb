def filter(event)
    status_change_date_value = event.get('status_change_date_value')

    is_status_change_date_value_valid = !status_change_date_value.nil?
    event.set('status_change_date', status_change_date_value) if is_status_change_date_value_valid

    return [event]
end