def filter(event)
    estimated_annual_throughput_value = event.get('estimated_annual_throughput_value')

    event.set('estimated_annual_throughput', estimated_annual_throughput_value) if !estimated_annual_throughput_value.nil?

    return [event]
end

test 'estimated_annual_throughput filter with nil value' do
  in_event { { 'estimated_annual_throughput_value' => nil } }

  expect('does not set estimated_annual_throughput field') do |events|
    events.size == 1 &&
    events[0].get('estimated_annual_throughput').nil?
  end
end

test 'estimated_annual_throughput filter with valid value' do
  in_event { { 'estimated_annual_throughput_value' => 1000 } }

  expect('sets estimated_annual_throughput field with the provided value') do |events|
    events.size == 1 &&
    events[0].get('estimated_annual_throughput') == 1000
  end
end
