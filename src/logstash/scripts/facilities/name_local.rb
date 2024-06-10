def filter(event)
    name_local_value = event.get('name_local_value')
  
    event.set('name_local', name_local_value) if !name_local_value.nil? && !name_local_value.strip.empty?
  
    return [event]
end
