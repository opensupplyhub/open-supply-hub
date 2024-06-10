def filter(event)
    description_value = event.get('description_value')
  
    event.set('description', description_value) if !description_value.nil? && !description_value.strip.empty?
  
    return [event]
end
