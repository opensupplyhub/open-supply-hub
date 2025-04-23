require_relative 'test_helper'
require_relative '../production_locations/duns_id'

test 'filter parses valid JSON and sets trimmed raw_value' do
  in_event({ 'duns_id_value' => '{"raw_value": " 15-048-3782 "}' })

  expect('sets trimmed raw_value correctly') do |events|
    events[0].get('duns_id') == '15-048-3782'
  end
end

test 'filter handles invalid JSON' do
  in_event({ 'duns_id_value' => '{invalid_json}' })

  expect('sets duns_id to empty string') do |events|
    events[0].get('duns_id') == ''
  end
end

test 'filter handles missing raw_value key' do
  in_event({ 'duns_id_value' => '{"something": "else"}' })

  expect('sets duns_id to empty string') do |events|
    events[0].get('duns_id') == ''
  end
end

test 'filter handles missing input' do
  in_event({})

  expect('sets duns_id to empty string') do |events|
    events[0].get('duns_id') == ''
  end
end
