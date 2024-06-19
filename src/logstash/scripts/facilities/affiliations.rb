def filter(event)
    affiliations_value = event.get('affiliations_value')
  
    is_affiliations_value_valid = !affiliations_value.nil? && !affiliations_value.empty?
    event.set('affiliations', affiliations_value) if is_affiliations_value_valid
  
    return [event]
end
