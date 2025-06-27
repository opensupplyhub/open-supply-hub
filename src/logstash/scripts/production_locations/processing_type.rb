def filter(event)
  # Get the processing_type_value (assuming it's a field in the event).
  processing_type_value = event.get('processing_type_value')

  # Check if the value exists (avoids potential nil error).
  if !processing_type_value || !processing_type_value['matched_values']
    return [event]
  end

  # Extract processing types and remove null values.
  values = processing_type_value['matched_values'].map { |value| value[3] if value[3] != nil }.compact.uniq

  # Set the processing_type field only if there are non-null values.
  event.set('processing_type', values) if values.any?

  return [event]
end 

test 'processing_type filter with valid matched_values' do
  in_event {
    {
      'processing_type_value' => {
        'matched_values' => [
          ['a', 'b', 'c', 'value1'],
          ['d', 'e', 'f', 'value2'],
          ['g', 'h', 'i', 'value1'],
          ['j', 'k', 'l', nil]
        ]
      }
    }
  }

  expect('sets processing_type with unique non-nil values') do |events|
    values = events[0].get('processing_type')
    values.sort == ['value1', 'value2']
  end
end

test 'processing_type filter with only nil matched values' do
  in_event {
    {
      'processing_type_value' => {
        'matched_values' => [
          ['a', 'b', nil],
          ['c', 'd', nil]
        ]
      }
    }
  }
  expect('does not set processing_type') do |events|
    !events[0].to_hash.key?('processing_type')
  end
end

test 'processing_type filter with missing matched_values key' do
  in_event {
    {
      'processing_type_value' => {}
    }
  }

  expect('does not set processing_type') do |events|
    !events[0].to_hash.key?('processing_type')
  end
end

test 'processing_type filter with missing processing_type_value key' do
  in_event {
    {}
  }

  expect('does not set processing_type') do |events|
    !events[0].to_hash.key?('processing_type')
  end
end
