def filter(event)
    alpha_2_country_code = event.get('country_value')
  
    country = {
        'alpha_2' => alpha_2_country_code,
    }
    event.set('country', country)
  
    return [event]
end
