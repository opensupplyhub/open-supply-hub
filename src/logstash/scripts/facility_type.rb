def filter(event)
  # Get the facility_type_value value (assuming it's a field in the event)
  facility_type_value = event.get('facility_type_value')

  # Check if the value exists (avoids potential nil error)
  if !facility_type_value || !facility_type_value["matched_values"]
    return [event]
  end

  # Extract processing types and remove null values
  values = facility_type_value["matched_values"].map { |value| value[3] if value[3] != nil }.compact

  # Set the facility_type field only if there are non-null values
  event.set('facility_type', values) if values.any?

  return [event]
end
