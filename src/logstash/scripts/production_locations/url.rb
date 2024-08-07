def filter(event)
    url_value = event.get('url_value')

    is_url_value_valid = !url_value.nil? && !url_value.strip.empty?
    event.set('business_url', url_value) if is_url_value_valid

    return [event]
end
