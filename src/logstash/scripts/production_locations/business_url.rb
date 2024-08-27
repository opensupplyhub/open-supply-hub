def filter(event)
    business_url_value = event.get('business_url_value')

    is_business_url_value_valid = !business_url_value.nil? && !business_url_value.strip.empty?
    event.set('business_url', business_url_value) if is_business_url_value_valid

    return [event]
end
