def filter(event)
  # Get the location_type_value (assuming it's a field in the event).
  location_type_value = event.get('location_type_value')

  # Check if the value exists (avoids potential nil error).
  if !location_type_value || !location_type_value['matched_values']
    return [event]
  end

  # Extract processing types and remove null values.
  values = location_type_value['matched_values'].map { |value| value[3] if value[3] != nil }.compact

  # Set the location_type field only if there are non-null values.
  event.set('location_type', values) if values.any?

  return [event]
end
