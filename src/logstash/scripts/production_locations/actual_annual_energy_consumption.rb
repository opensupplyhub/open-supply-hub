def filter(event)
    actual_annual_energy_consumption_value = event.get('actual_annual_energy_consumption_value')

    if !actual_annual_energy_consumption_value.nil?
      if actual_annual_energy_consumption_value.is_a?(Array)
        event.set('actual_annual_energy_consumption', actual_annual_energy_consumption_value)
      elsif actual_annual_energy_consumption_value.is_a?(String)
        begin
          parsed_value = JSON.parse(actual_annual_energy_consumption_value)
          if parsed_value.is_a?(Array)
            event.set('actual_annual_energy_consumption', parsed_value)
          end
        rescue JSON::ParserError
          # Skip if JSON parsing fails
        end
      end
    end

    return [event]
end

test 'actual_annual_energy_consumption filter with nil value' do
  in_event { { 'actual_annual_energy_consumption_value' => nil } }

  expect('does not set actual_annual_energy_consumption field') do |events|
    events.size == 1 &&
    events[0].get('actual_annual_energy_consumption').nil?
  end
end

test 'actual_annual_energy_consumption filter with valid array value' do
  consumption_data = [
    {"source" => "Electricity", "amount" => 100},
    {"source" => "Coal", "amount" => 200},
    {"source" => "Biomass", "amount" => 300}
  ]
  in_event { { 'actual_annual_energy_consumption_value' => consumption_data } }

  expect('sets actual_annual_energy_consumption field with the provided value') do |events|
    events.size == 1 &&
    events[0].get('actual_annual_energy_consumption') == consumption_data
  end
end

test 'actual_annual_energy_consumption filter with valid JSON string value' do
  consumption_json = '[{"source":"Electricity","amount":100},{"source":"Coal","amount":200}]'
  expected_data = [
    {"source" => "Electricity", "amount" => 100},
    {"source" => "Coal", "amount" => 200}
  ]
  in_event { { 'actual_annual_energy_consumption_value' => consumption_json } }

  expect('parses JSON string and sets actual_annual_energy_consumption field') do |events|
    events.size == 1 &&
    events[0].get('actual_annual_energy_consumption') == expected_data
  end
end