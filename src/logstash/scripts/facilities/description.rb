def filter(event)
    description_value = event.get('description_value')
  
    is_description_value_valid = !description_value.nil? && !description_value.strip.empty?
    event.set('description', description_value) if is_description_value_valid
  
    return [event]
end
