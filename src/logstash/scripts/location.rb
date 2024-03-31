def filter(event)
  lat = event.get('latitude')
  lon = event.get('longitude')

  if !lat || !lon
    return [event]
  end

  event.set('location', {
    'lat' => lat,
    'lon' => lon
  })

  return [event]
end
