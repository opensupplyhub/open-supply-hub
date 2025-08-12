require "json"

def safe_parse_geocode(event)
  geocode_value = event.get('geocode_value')
  return nil if geocode_value.nil? || geocode_value.empty?

  begin
    JSON.parse(geocode_value)
  rescue JSON::ParserError
    nil
  end
end

def first_result(parsed)
  return nil unless parsed&.key?('data')
  data = parsed['data']
  return nil unless data&.key?('results')
  results = data['results']
  return nil if results.nil? || results.empty?

  results[0]
end

def filter(event)
  parsed = safe_parse_geocode(event)
  return [event] if parsed.nil?

  result = first_result(parsed)
  return [event] if result.nil?

  geometry = result['geometry']
  location_type = geometry&.dig('location_type') if geometry
  formatted_address = result['formatted_address']

  event.set('geocoded_location_type', location_type) if location_type
  event.set('geocoded_address', formatted_address) if formatted_address

  [event]
end
