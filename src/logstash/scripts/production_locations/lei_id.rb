require 'json'

def filter(event)
  lei_id = event.get('lei_id_value')

  if lei_id
    begin
      parsed = JSON.parse(lei_id)
      if parsed['raw_value'] && !parsed['raw_value'].strip.empty?
        event.set('lei_id', parsed['raw_value'].strip)
      end
    rescue JSON::ParserError
    end
  end

  return [event]
end

test 'valid JSON sets trimmed raw_value correctly' do
  in_event do
    { 'lei_id_value' => '{"raw_value": " 529900T8BM49AURSDO55 "}' }
  end

  expect('returns trimmed string') do |events|
    events[0].get('lei_id') == '529900T8BM49AURSDO55'
  end
end

test 'invalid JSON does not set lei_id' do
  in_event do
    { 'lei_id_value' => '{invalid_json}' }
  end

  expect('field is not present') do |events|
    !events[0].include?('lei_id')
  end
end

test 'missing raw_value does not set lei_id' do
  in_event do
    { 'lei_id_value' => '{"something": "else"}' }
  end

  expect('field is not present') do |events|
    !events[0].include?('lei_id')
  end
end

test 'no input does not set lei_id' do
  in_event do
    {}
  end

  expect('field is not present') do |events|
    !events[0].include?('lei_id')
  end
end
