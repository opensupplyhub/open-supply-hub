def filter(event)
  # Get the product_type_value (assuming it's a field in the event)
  product_type_value = event.get('product_type_value')

  # Check if the value exists (avoids potential nil error)
  if !product_type_value || !product_type_value['raw_values']
    return [event]
  end

  # Trim whitespace from raw_values
  values = product_type_value['raw_values'].map(&:strip)  # Use strip to remove leading/trailing whitespace

  # Extract processing types using map (assuming values is now an array of strings)
  event.set('product_type', values) if values.length > 0

  return [event]
end
