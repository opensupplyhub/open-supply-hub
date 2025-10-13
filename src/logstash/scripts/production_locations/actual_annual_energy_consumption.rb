require 'json'

ENERGY_SOURCES = [
  ['Coal', 'energy_coal_value'],
  ['Natural gas', 'energy_natural_gas_value'],
  ['Diesel', 'energy_diesel_value'],
  ['Kerosene', 'energy_kerosene_value'],
  ['Biomass', 'energy_biomass_value'],
  ['Charcoal', 'energy_charcoal_value'],
  ['Animal waste', 'energy_animal_waste_value'],
  ['Electricity', 'energy_electricity_value'],
  ['Other', 'energy_other_value']
]

def parse_numeric_value(value, field_key)
  return value.to_i if value.is_a?(Numeric)
  return nil unless value.is_a?(String)

  str = value.strip
  return nil if str.empty?

  begin
    # Normalize common thousands separators and non-breaking spaces.
    normalized = str.gsub(/[\u00A0,]/, '')
    Integer(normalized)
  rescue StandardError
    if defined?(@logger) && @logger
      @logger.warn(
        "actual_annual_energy_consumption: skipping malformed non-integer value",
        field: field_key,
        value: value
      )
    end
    nil
  end
end

def log_invalid_value(field_key, value)
  return unless defined?(@logger) && @logger
  @logger.warn(
    "actual_annual_energy_consumption: skipping non-numeric value",
    field: field_key,
    value_class: value.class.to_s
  )
end

def build_from_discrete(event)
  built_array = []
  ENERGY_SOURCES.each do |source_name, field_key|
    value = event.get(field_key)
    next if value.nil?

    numeric_amount = parse_numeric_value(value, field_key)
    if numeric_amount.nil?
      # Log non-numeric, non-string values for visibility.
      log_invalid_value(field_key, value) unless value.is_a?(Numeric) || value.is_a?(String)
      next
    end

    built_array << { 'source' => source_name, 'amount' => numeric_amount }
  end
  built_array
end

def coerce_aec_array(items)
  return [] unless items.is_a?(Array)
  items.map do |item|
    next nil unless item.is_a?(Hash)
    amount = parse_numeric_value(item['amount'], 'fallback_amount')
    source = item['source']
    next nil if amount.nil? || source.nil?
    { 'source' => source, 'amount' => amount }
  end.compact
end

def set_from_fallback(event, fallback)
  return if fallback.nil?

  if fallback.is_a?(Array)
    event.set('actual_annual_energy_consumption', coerce_aec_array(fallback))
    return
  end

  if fallback.is_a?(String)
    begin
      parsed_value = JSON.parse(fallback)
      if parsed_value.is_a?(Array)
        event.set('actual_annual_energy_consumption', coerce_aec_array(parsed_value))
      end
    rescue JSON::ParserError
      # Skip if JSON parsing fails.
    end
  end
end

def filter(event)
    fallback_value = event.get('actual_annual_energy_consumption_value')

    built_array = build_from_discrete(event)
    if built_array.any?
      event.set('actual_annual_energy_consumption', built_array)
    else
      set_from_fallback(event, fallback_value)
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