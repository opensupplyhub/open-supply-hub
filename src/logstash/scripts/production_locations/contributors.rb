def filter(event)
    contributors_value = event.get('contributors_value')
  
    if !contributors_value
      return [event]
    end
  
    event.set('contributors', contributors_value)
  
    return [event]
  end
