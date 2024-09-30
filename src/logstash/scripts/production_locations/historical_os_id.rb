def filter(event)
    historical_os_id_value = event.get('historical_os_id_value')

    if historical_os_id_value.nil?
        return [event]
    end

    event.set('historical_os_id', historical_os_id_value)

    return [event]
end