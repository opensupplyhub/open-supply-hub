def filter(event)
    percent_female_workers_value = event.get('percent_female_workers_value')
  
    event.set('percent_female_workers', percent_female_workers_value) if !percent_female_workers_value.nil?
  
    return [event]
end
