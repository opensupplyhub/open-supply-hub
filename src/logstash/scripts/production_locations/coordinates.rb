def filter(event)
  # Get the latitude value from the event data (assuming it's a field named 'latitude').
  lat = event.get('latitude')

  # Get the longitude value from the event data (assuming it's a field named 'longitude').
  lng = event.get('longitude')

  # Check if both latitude and longitude are present (avoid creating empty coordinates data).
  if !lat || !lng
    # If either is missing, return the event without modification.
    return [event]
  end

  # Create a hash to store the coordinates data (latitude and longitude).
  coordinates = {
    'lat' => lat,
    'lng' => lng
  }

  # Set a new field named 'coordinates' within the event containing the coordinates data.
  event.set('coordinates', coordinates)

  # Return the modified event with the added coordinates field.
  return [event]
end
