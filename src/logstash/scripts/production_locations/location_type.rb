def filter(event)
  # Get the location_type_value (assuming it's a field in the event).
  location_type_value = event.get('location_type_value')

  # Check if the value exists (avoids potential nil error).
  if !location_type_value || !location_type_value['matched_values']
    return [event]
  end

  # Extract processing types and remove null values.
  values = location_type_value['matched_values'].map { |value| value[2] if value[2] != nil }.compact.uniq

  # Set the location_type field only if there are non-null values.
  event.set('location_type', values) if values.any?

  return [event]
end

test 'location_type filter with valid matched_values' do
  in_event {
    {
      'location_type_value' => {
        'matched_values' => [
          ['a', 'b', 'value1'],
          ['c', 'd', 'value2'],
          ['e', 'f', 'value2'],
          ['g', 'h', nil]
        ]
      }
    }
  }

  expect('sets location_type with unique non-nil values') do |events|
    values = events[0].get('location_type')
    values.sort == ['value1', 'value2']
  end
end

test 'location_type filter with only nil matched values' do
  in_event {
    {
      'location_type_value' => {
        'matched_values' => [
          ['a', 'b', nil],
          ['c', 'd', nil]
        ]
      }
    }
  }
  expect('does not set location_type') do |events|
    !events[0].to_hash.key?('location_type')
  end
end

test 'location_type filter with missing matched_values key' do
  in_event {
    {
      'location_type_value' => {}
    }
  }

  expect('does not set location_type') do |events|
    !events[0].to_hash.key?('location_type')
  end
end

test 'location_type filter with missing location_type_value key' do
  in_event {
    {}
  }

  expect('does not set location_type') do |events|
    !events[0].to_hash.key?('location_type')
  end
end
