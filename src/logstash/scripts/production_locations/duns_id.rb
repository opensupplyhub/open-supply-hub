require 'json'

def filter(event)
  duns_id = event.get('duns_id_value')
  duns_id_value = ""

  if duns_id
    begin
      parsed = JSON.parse(duns_id)
      if parsed['raw_value']
        duns_id_value = parsed['raw_value'].strip
      end
    rescue JSON::ParserError => e
      duns_id_value = ""
    end
  end

  event.set('duns_id', duns_id_value)

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

test 'invalid JSON sets duns_id to empty string' do
  in_event do
    { 'duns_id_value' => '{invalid_json}' }
  end

  expect('returns empty string') do |events|
    events[0].get('duns_id') == ''
  end
end

test 'missing raw_value sets duns_id to empty string' do
  in_event do
    { 'duns_id_value' => '{"something": "else"}' }
  end

  expect('returns empty string') do |events|
    events[0].get('duns_id') == ''
  end
end

test 'no input sets duns_id to empty string' do
  in_event do
    {}
  end

  expect('returns empty string') do |events|
    events[0].get('duns_id') == ''
  end
end
