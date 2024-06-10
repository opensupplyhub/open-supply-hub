def filter(event)
    url_value = event.get('url_value')
  
    event.set('url', url_value) if !url_value.nil? && !url_value.strip.empty?
  
    return [event]
end
