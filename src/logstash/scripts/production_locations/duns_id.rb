require 'json'

def filter(event)
  duns_id = event.get('duns_id_value')

  if duns_id
    begin
      parsed = JSON.parse(duns_id)
      if parsed['raw_value'] && !parsed['raw_value'].strip.empty?
        event.set('duns_id', parsed['raw_value'].strip)
      end
    rescue JSON::ParserError
    end
  end

  return [event]
end

test 'valid JSON sets trimmed raw_value correctly' do
  in_event do
    { 'duns_id_value' => '{"raw_value": " 15-048-3782 "}' }
  end

  expect('returns trimmed string') do |events|
    events[0].get('duns_id') == '15-048-3782'
  end
end

test 'invalid JSON does not set duns_id' do
  in_event do
    { 'duns_id_value' => '{invalid_json}' }
  end

  expect('field is not present') do |events|
    !events[0].include?('duns_id')
  end
end

test 'missing raw_value does not set duns_id' do
  in_event do
    { 'duns_id_value' => '{"something": "else"}' }
  end

  expect('field is not present') do |events|
    !events[0].include?('duns_id')
  end
end

test 'no input does not set duns_id' do
  in_event do
    {}
  end

  expect('field is not present') do |events|
    !events[0].include?('duns_id')
  end
end
