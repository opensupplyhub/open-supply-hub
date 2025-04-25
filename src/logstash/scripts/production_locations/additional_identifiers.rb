require 'json'

ID_FIELD_MAP = {
  'duns_id_value' => 'duns_id',
  'lei_id_value' => 'lei_id',
  'rba_id_value' => 'rba_id',
}

def filter(event)
  ID_FIELD_MAP.each do |input_field, output_field|
    id_value = event.get(input_field)

    if id_value
      begin
        parsed = JSON.parse(id_value)
        if parsed['raw_value'] && !parsed['raw_value'].strip.empty?
          event.set(output_field, parsed['raw_value'].strip)
        end
      rescue JSON::ParserError
      end
    end
  end

  return [event]
end

# Test cases for each ID field
ID_FIELD_MAP.each do |input_field, output_field|
  test "valid JSON sets trimmed #{output_field} correctly" do
    in_event do
      { input_field => '{"raw_value": " 1234567890 "}' }
    end

    expect("returns trimmed string for #{output_field}") do |events|
      events[0].get(output_field) == '1234567890'
    end
  end

  test "invalid JSON does not set #{output_field}" do
    in_event do
      { input_field => '{invalid_json}' }
    end

    expect("field is not present for #{output_field}") do |events|
      !events[0].include?(output_field)
    end
  end

  test "missing raw_value does not set #{output_field}" do
    in_event do
      { input_field => '{"something": "else"}' }
    end

    expect("field is not present for #{output_field}") do |events|
      !events[0].include?(output_field)
    end
  end

  test "no input does not set #{output_field}" do
    in_event do
      {}
    end

    expect("field is not present for #{output_field}") do |events|
      !events[0].include?(output_field)
    end
  end
end
