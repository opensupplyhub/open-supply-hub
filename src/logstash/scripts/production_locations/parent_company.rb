def filter(event)
  # Get the parent_company_value (assuming it's a field in the event).
  parent_company_value = event.get('parent_company_value')

  # Check if the value exists (avoids potential nil error).
  if !parent_company_value || !parent_company_value['raw_value']
    return [event]
  end

  # Trim whitespace from raw_value
  value = parent_company_value['raw_value'].strip  # Use strip to remove leading/trailing whitespace.

  # Set the parent_company field if the trimmed value is not empty.
  event.set('parent_company', value) if !value.empty?

  return [event]
end

test 'parent_company filter trims whitespace from raw_value' do
  in_event {
    {
      'parent_company_value' => {
        'raw_value' => '  Example Group Ltd.  '
      }
    }
  }

  expect('sets parent_company with the trimmed value') do |events|
    events.size == 1 &&
    events[0].get('parent_company') == 'Example Group Ltd.'
  end
end

test 'parent_company filter with a whitespace-only raw_value' do
  in_event {
    {
      'parent_company_value' => {
        'raw_value' => '   '
      }
    }
  }

  expect('does not set parent_company') do |events|
    events.size == 1 &&
    !events[0].to_hash.key?('parent_company')
  end
end

test 'parent_company filter with missing raw_value key' do
  in_event {
    {
      'parent_company_value' => {}
    }
  }

  expect('does not set parent_company') do |events|
    events.size == 1 &&
    !events[0].to_hash.key?('parent_company')
  end
end

test 'parent_company filter with missing parent_company_value key' do
  in_event {
    {}
  }

  expect('does not set parent_company') do |events|
    events.size == 1 &&
    !events[0].to_hash.key?('parent_company')
  end
end
