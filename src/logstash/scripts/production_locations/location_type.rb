def filter(event)
  # Get the location_type_value (assuming it's a field in the event).
  location_type_value = event.get('location_type_value')

  # Check if the value exists (avoids potential nil error).
  if !location_type_value || !location_type_value['matched_values']
    return [event]
  end

  # Extract facility types, preferring the matched taxonomy value (index 2)
  # but falling back to the raw submitted value (index 3) when matching was
  # skipped - e.g. claim-sourced facility types always skip matching, so
  # index 2 is always nil for them and they would otherwise be silently
  # dropped from search. Mirrors the fallback in index_facility_type() (SQL).
  values = location_type_value['matched_values'].map { |value| value[2] || value[3] }.compact.uniq

  # Set the location_type field only if there are non-null values.
  event.set('location_type', values) if values.any?

  return [event]
end

test 'location_type filter with valid matched_values' do
  in_event {
    {
      'location_type_value' => {
        'matched_values' => [
          ['a', 'b', 'value1', 'raw1'],
          ['c', 'd', 'value2', 'raw2'],
          ['e', 'f', 'value2', 'raw2'],
          ['g', 'h', nil, 'raw3']
        ]
      }
    }
  }

  expect('sets location_type with unique non-nil values, falling back to the raw value when unmatched') do |events|
    values = events[0].get('location_type')
    values.sort == ['raw3', 'value1', 'value2']
  end
end

test 'location_type filter falls back to the raw value when matching was skipped' do
  # Mirrors real claim-sourced data: claims always skip taxonomy matching,
  # so the matched-value slot (index 2) is nil and only the raw submitted
  # value (index 3) is available.
  in_event {
    {
      'location_type_value' => {
        'matched_values' => [
          ['PROCESSING_TYPE', 'SKIPPED_MATCHING', nil, 'Final product assembly']
        ]
      }
    }
  }

  expect('sets location_type from the raw value') do |events|
    events[0].get('location_type') == ['Final product assembly']
  end
end

test 'location_type filter with no matched or raw values' do
  in_event {
    {
      'location_type_value' => {
        'matched_values' => [
          ['a', 'b', nil, nil],
          ['c', 'd', nil, nil]
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
