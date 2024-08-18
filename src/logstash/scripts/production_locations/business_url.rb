def filter(event)
    business_url = event.get('business_url')

    is_business_url_valid = !business_url.nil? && !business_url.strip.empty?
    event.set('business_url', business_url) if is_business_url_valid

    return [event]
end
