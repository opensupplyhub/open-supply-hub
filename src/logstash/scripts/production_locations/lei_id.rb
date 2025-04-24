require 'json'

def filter(event)
  lei_id = event.get('lei_id_value')
  lei_id_value = ""

  if lei_id
    begin
      parsed = JSON.parse(lei_id)
      if parsed['raw_value']
        lei_id_value = parsed['raw_value'].strip
      end
    rescue JSON::ParserError => e
      lei_id_value = ""
    end
  end

  event.set('lei_id', lei_id_value)

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

test 'invalid JSON sets lei_id to empty string' do
  in_event do
    { 'lei_id_value' => '{invalid_json}' }
  end

  expect('returns empty string') do |events|
    events[0].get('lei_id') == ''
  end
end

test 'missing raw_value sets lei_id to empty string' do
  in_event do
    { 'lei_id_value' => '{"something": "else"}' }
  end

  expect('returns empty string') do |events|
    events[0].get('lei_id') == ''
  end
end

test 'no input sets lei_id to empty string' do
  in_event do
    {}
  end

  expect('returns empty string') do |events|
    events[0].get('lei_id') == ''
  end
end
