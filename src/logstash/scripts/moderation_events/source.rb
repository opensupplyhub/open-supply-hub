def filter(event)
    source_value = event.get('source_value')

    is_source_value_valid = !source_value.nil? && !source_value.strip.empty?
    event.set('source', source_value) if is_source_value_valid

    return [event]
end