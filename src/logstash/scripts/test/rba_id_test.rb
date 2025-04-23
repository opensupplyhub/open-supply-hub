require_relative 'test_helper'
require_relative '../production_locations/rba_id'

test 'filter parses valid JSON and sets trimmed raw_value' do
  in_event({ 'rba_id_value' => '{"raw_value": " RBA-12345678 "}' })

  expect('sets trimmed raw_value correctly') do |events|
    events[0].get('rba_id') == 'RBA-12345678'
  end
end

test 'filter handles invalid JSON' do
  in_event({ 'rba_id_value' => '{invalid_json}' })

  expect('sets rba_id to empty string') do |events|
    events[0].get('rba_id') == ''
  end
end

test 'filter handles missing raw_value key' do
  in_event({ 'rba_id_value' => '{"something": "else"}' })

  expect('sets rba_id to empty string') do |events|
    events[0].get('rba_id') == ''
  end
end

test 'filter handles missing input' do
  in_event({})

  expect('sets rba_id to empty string') do |events|
    events[0].get('rba_id') == ''
  end
end
