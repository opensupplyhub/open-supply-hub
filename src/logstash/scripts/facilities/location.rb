def filter(event)
  # Get the latitude value from the event data (assuming it's a field named 'latitude')
  lat = event.get('latitude')

  # Get the longitude value from the event data (assuming it's a field named 'longitude')
  lon = event.get('longitude')

  # Check if both latitude and longitude are present (avoid creating empty location data)
  if !lat || !lon
    # If either is missing, return the event without modification
    return [event]
  end

  # Create a hash to store the location data (latitude and longitude)
  location = {
    'lat' => lat,
    'lon' => lon
  }

  # Set a new field named 'location' within the event containing the location data
  event.set('location', location)

  # Return the modified event with the added location field
  return [event]
end
