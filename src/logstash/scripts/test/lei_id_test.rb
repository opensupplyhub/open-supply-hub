require_relative 'test_helper'
require_relative '../production_locations/lei_id'

test 'filter parses valid JSON and sets trimmed raw_value' do
  in_event({ 'lei_id_value' => '{"raw_value": " 529900T8BM49AURSDO55 "}' })

  expect('sets trimmed raw_value correctly') do |events|
    events[0].get('lei_id') == '529900T8BM49AURSDO55'
  end
end

test 'filter handles invalid JSON' do
  in_event({ 'lei_id_value' => '{invalid_json}' })

  expect('sets lei_id to empty string') do |events|
    events[0].get('lei_id') == ''
  end
end

test 'filter handles missing raw_value key' do
  in_event({ 'lei_id_value' => '{"something": "else"}' })

  expect('sets lei_id to empty string') do |events|
    events[0].get('lei_id') == ''
  end
end

test 'filter handles missing input' do
  in_event({})

  expect('sets lei_id to empty string') do |events|
    events[0].get('lei_id') == ''
  end
end
