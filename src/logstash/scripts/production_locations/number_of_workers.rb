def filter(event)
    number_of_workers_value = event.get('number_of_workers_value')
  
    if !number_of_workers_value
      return [event]
    end
  
    event.set('number_of_workers', number_of_workers_value)
  
    return [event]
  end
