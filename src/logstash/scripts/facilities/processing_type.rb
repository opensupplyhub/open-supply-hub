def filter(event)
  # Get the processing_type_value (assuming it's a field in the event).
  processing_type_value = event.get('processing_type_value')

  # Check if the value exists (avoids potential nil error).
  if !processing_type_value || !processing_type_value['matched_values']
    return [event]
  end

  # Extract processing types and remove null values.
  values = processing_type_value['matched_values'].map { |value| value[3] if value[3] != nil }.compact

  # Set the processing_type field only if there are non-null values.
  event.set('processing_type', values) if values.any?

  return [event]
end
