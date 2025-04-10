require "json"

def filter(event)
  geocode_value = event.get('geocode_value')

  if geocode_value.nil? || geocode_value.empty?
      return [event]
  end

  geocode_value_parsed = JSON.parse(geocode_value)

  if geocode_value_parsed.nil? || geocode_value.empty?
    return [event]
  end

  if !geocode_value_parsed.key?('data')
    return [event]
  end

  data = geocode_value_parsed['data']

  if !data.key?('results')
    return [event]
  end

  results = data['results']

  if results.empty?
    return [event]
  end

  location_type = results[0]['geometry']['location_type']
  formatted_address = results[0]['formatted_address']

  event.set('geocoded_location_type', location_type)
  event.set('geocoded_address', formatted_address)

  return [event]
end
