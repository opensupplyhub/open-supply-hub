require 'json'
require 'fileutils'

def filter(event)
    # Country code Alpha-2 data
    alpha_2_country_code = event.get('country_value')

    # Define the path to the JSON file
    json_countries_file_path = File.expand_path('../../../static-data/countries.json', __FILE__)

    # Read and parse the JSON file
    json_countries_data = File.read(json_countries_file_path)
    countries = JSON.parse(json_countries_data)
    exact_country = countries[alpha_2_country_code]

    # Build country object
    country = {
        'name' => exact_country["name"],
        'alpha_2' => alpha_2_country_code,
        'alpha_3' => exact_country["alpha_3"],
        'numeric' => exact_country["numeric"],
    }
    event.set('country', country)
  
    return [event]
end

test "Country filter" do

    in_event { { 'country_value' => "UA" } }
  
    expect("Get object data") do |events|
      events.size == 1
      events[0].get('country')['name'] == "Ukraine"
      events[0].get('country')['alpha_2'] == "UA"
      events[0].get('country')['alpha_3'] == "UKR"
      events[0].get('country')['numeric'] == "1"
    end
end
