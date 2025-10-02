require 'json'
require 'fileutils'

def filter(event)
    # Country code Alpha-2 data
    alpha_2_country_code = event.get('country_value')

    # Guard: skip if missing
    return [event] if alpha_2_country_code.nil?

    # Define the path to the JSON file
    json_countries_file_path = File.expand_path('../../../static_data/countries.json', __FILE__)

    # Read and parse the JSON file
    json_countries_data = File.read(json_countries_file_path)
    countries = JSON.parse(json_countries_data)
    exact_country = countries[alpha_2_country_code]

    # Guard: skip if unknown code
    return [event] unless exact_country.is_a?(Hash)

    # Build country object
    country = {
        'name' => exact_country['name'],
        'alpha_2' => alpha_2_country_code,
        'alpha_3' => exact_country['alpha_3'],
        'numeric' => exact_country['numeric'],
    }
    event.set('country', country)

    return [event]
end

# Avoid executing test DSL in Logstash runtime
if defined?(test)
  test 'country filter' do
      in_event { { 'country_value' => 'UA' } }

      expect('gets object data') do |events|
          result = (
              events.size == 1 &&
              events[0].get('country')['name'] == 'Ukraine' &&
              events[0].get('country')['alpha_2'] == 'UA' &&
              events[0].get('country')['alpha_3'] == 'UKR' &&
              events[0].get('country')['numeric'] == '804'
          )

          result
      end
  end
end