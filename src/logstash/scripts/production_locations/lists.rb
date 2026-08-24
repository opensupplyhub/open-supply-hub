def filter(event)
    lists_value = event.get('lists_value')

    if lists_value.nil?
        return [event]
    end

    event.set('lists', lists_value)

    return [event]
end
