def filter(event)
  # Get the parent_company_value (assuming it's a field in the event)
  parent_company_value = event.get('parent_company_value')

  # Check if the value exists (avoids potential nil error)
  if !parent_company_value || !parent_company_value['raw_value']
    return [event]
  end

  # Trim whitespace from raw_value
  value = parent_company_value['raw_value'].strip  # Use strip to remove leading/trailing whitespace

  # Set the parent_company field if the trimmed value is not empty
  event.set('parent_company', value) if !value.empty?

  return [event]
end
