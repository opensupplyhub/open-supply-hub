require 'json'

def filter(event)
  rba_id = event.get('rba_id_value')
  rba_id_value = ""

  if rba_id
    begin
      parsed = JSON.parse(rba_id)
      if parsed['raw_value']
        rba_id_value = parsed['raw_value'].strip
      end
    rescue JSON::ParserError => e
      rba_id_value = ""
    end
  end

  event.set('rba_id', rba_id_value)

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

test 'invalid JSON sets rba_id to empty string' do
  in_event do
    { 'rba_id_value' => '{invalid_json}' }
  end

  expect('returns empty string') do |events|
    events[0].get('rba_id') == ''
  end
end

test 'missing raw_value sets rba_id to empty string' do
  in_event do
    { 'rba_id_value' => '{"something": "else"}' }
  end

  expect('returns empty string') do |events|
    events[0].get('rba_id') == ''
  end
end

test 'no input sets rba_id to empty string' do
  in_event do
    {}
  end

  expect('returns empty string') do |events|
    events[0].get('rba_id') == ''
  end
end
