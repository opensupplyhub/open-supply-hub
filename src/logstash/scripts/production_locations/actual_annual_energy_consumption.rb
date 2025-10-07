require 'json'

def filter(event)
    actual_annual_energy_consumption_value = event.get('actual_annual_energy_consumption_value')

    # First, attempt to build from discrete energy_* fields if present.
    energy_sources = [
      ['Coal', 'energy_coal_value'],
      ['Natural gas', 'energy_natural_gas_value'],
      ['Diesel', 'energy_diesel_value'],
      ['Kerosene', 'energy_kerosene_value'],
      ['Biomass', 'energy_biomass_value'],
      ['Charcoal', 'energy_charcoal_value'],
      ['Animal waste', 'energy_animal_waste_value'],
      ['Electricity', 'energy_electricity_value']
    ]

    built_array = []
    energy_sources.each do |source_name, field_key|
      value = event.get(field_key)
      next if value.nil?

      numeric_amount = nil

      if value.is_a?(Numeric)
        numeric_amount = value.to_f
      elsif value.is_a?(String)
        str = value.strip
        unless str.empty?
          begin
            normalized = str.gsub(',', '')
            numeric_amount = Float(normalized)
          rescue StandardError
            if defined?(@logger) && @logger
              @logger.warn(
                "actual_annual_energy_consumption: skipping malformed string value",
                field: field_key,
                value: value
              )
            end
          end
        end
      else
        if defined?(@logger) && @logger
          @logger.warn(
            "actual_annual_energy_consumption: skipping non-numeric value",
            field: field_key,
            value_class: value.class.to_s
          )
        end
      end

      if !numeric_amount.nil?
        built_array << { 'source' => source_name, 'amount' => numeric_amount }
      end
    end

    if built_array.any?
      event.set('actual_annual_energy_consumption', built_array)
    elsif !actual_annual_energy_consumption_value.nil?
      # Fallback to existing array/string field from SQL.
      if actual_annual_energy_consumption_value.is_a?(Array)
        event.set('actual_annual_energy_consumption', actual_annual_energy_consumption_value)
      elsif actual_annual_energy_consumption_value.is_a?(String)
        begin
          parsed_value = JSON.parse(actual_annual_energy_consumption_value)
          if parsed_value.is_a?(Array)
            event.set('actual_annual_energy_consumption', parsed_value)
          end
        rescue JSON::ParserError
          # Skip if JSON parsing fails.
        end
      end
    end

    return [event]
end

test 'actual_annual_energy_consumption filter with nil value and no discrete fields' do
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

test 'actual_annual_energy_consumption builds from discrete energy_* fields' do
  in_event do
    {
      'energy_coal_value' => 100,
      'energy_diesel_value' => 200,
      'energy_animal_waste_value' => 300
    }
  end

  expect('sets array from discrete fields in specified order') do |events|
    arr = events[0].get('actual_annual_energy_consumption')
    arr == [
      { 'source' => 'Coal', 'amount' => 100 },
      { 'source' => 'Diesel', 'amount' => 200 },
      { 'source' => 'Animal waste', 'amount' => 300 }
    ]
  end
end