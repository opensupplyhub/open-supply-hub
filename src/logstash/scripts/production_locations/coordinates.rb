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
    'lon' => lng
  }

  # Set a new field named 'coordinates' within the event containing the coordinates data.
  event.set('coordinates', coordinates)

  # Return the modified event with the added coordinates field.
  return [event]
end

test 'coordinates filter with both latitude and longitude' do
  in_event {
    {
      'latitude' => 48.8566,
      'longitude' => 2.3522
    }
  }

  expect('sets coordinates with lat and lon keys') do |events|
    events.size == 1 &&
    events[0].get('coordinates') == { 'lat' => 48.8566, 'lon' => 2.3522 }
  end
end

test 'coordinates filter with missing longitude' do
  in_event {
    {
      'latitude' => 48.8566
    }
  }

  expect('does not set coordinates') do |events|
    events.size == 1 &&
    !events[0].to_hash.key?('coordinates')
  end
end

test 'coordinates filter with neither latitude nor longitude' do
  in_event {
    {}
  }

  expect('does not set coordinates') do |events|
    events.size == 1 &&
    !events[0].to_hash.key?('coordinates')
  end
end
