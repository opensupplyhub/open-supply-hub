require_relative 'countries'

def filter(event)
    alpha_2_country_code = event.get('country_value')
  
    country = {
        'name' => COUNTRY_NAMES[alpha_2_country_code],
        'alpha_2' => alpha_2_country_code,
        'alpha_3' => COUNTRY_ALPHA_3[alpha_2_country_code],
        'numeric' => COUNTRY_NUMERIC[alpha_2_country_code],
    }
    event.set('country', country)
  
    return [event]
end
