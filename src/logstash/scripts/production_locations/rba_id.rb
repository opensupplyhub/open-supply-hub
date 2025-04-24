require 'json'

def filter(event)
  rba_id = event.get('rba_id_value')

  if rba_id
    begin
      parsed = JSON.parse(rba_id)
      if parsed['raw_value'] && !parsed['raw_value'].strip.empty?
        event.set('rba_id', parsed['raw_value'].strip)
      end
    rescue JSON::ParserError
    end
  end

  return [event]
end

test 'valid JSON sets trimmed raw_value correctly' do
  in_event do
    { 'rba_id_value' => '{"raw_value": " RBA-12345678 "}' }
  end

  expect('returns trimmed string') do |events|
    events[0].get('rba_id') == 'RBA-12345678'
  end
end

test 'invalid JSON does not set rba_id' do
  in_event do
    { 'rba_id_value' => '{invalid_json}' }
  end

  expect('field is not present') do |events|
    !events[0].include?('rba_id')
  end
end

test 'missing raw_value does not set rba_id' do
  in_event do
    { 'rba_id_value' => '{"something": "else"}' }
  end

  expect('field is not present') do |events|
    !events[0].include?('rba_id')
  end
end

test 'no input does not set rba_id' do
  in_event do
    {}
  end

  expect('field is not present') do |events|
    !events[0].include?('rba_id')
  end
end
