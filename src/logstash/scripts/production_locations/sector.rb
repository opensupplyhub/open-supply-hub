def filter(event)
    sector_value = event.get('sector_value')
  
    if sector_value.nil?
        return [event]
    end

    redundant_sector_value = 'Unspecified'
    filtered_sector_value = sector_value.select { |value| value != redundant_sector_value }

    event.set('sector', filtered_sector_value) if !filtered_sector_value.empty?

    return [event]
end

test 'sector filter drops the redundant Unspecified value' do
  in_event {
    {
      'sector_value' => ['Apparel', 'Unspecified', 'Agriculture']
    }
  }

  expect('sets sector with Unspecified filtered out') do |events|
    events.size == 1 &&
    events[0].get('sector') == ['Apparel', 'Agriculture']
  end
end

test 'sector filter with only Unspecified values' do
  in_event {
    {
      'sector_value' => ['Unspecified']
    }
  }

  expect('does not set sector when nothing remains after filtering') do |events|
    events.size == 1 &&
    !events[0].to_hash.key?('sector')
  end
end

test 'sector filter with nil sector_value' do
  in_event {
    {
      'sector_value' => nil
    }
  }

  expect('does not set sector') do |events|
    events.size == 1 &&
    !events[0].to_hash.key?('sector')
  end
end
