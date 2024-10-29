require 'json'
require 'fileutils'

def filter(event)
    cleaned_data_value = event.get('cleaned_data_value')

    # Check whether the 'country_code' key exists.
    if !cleaned_data_value.nil? && cleaned_data_value.key?('country_code')
        # Country code Alpha-2 data.
        alpha_2_country_code = cleaned_data_value['country_code']

        # Define the path to the JSON file.
        json_countries_file_path = File.expand_path('../../../static_data/countries.json', __FILE__)

        # Read and parse the JSON file.
        json_countries_data = File.read(json_countries_file_path)
        countries = JSON.parse(json_countries_data)
        exact_country = countries[alpha_2_country_code]

        # Build country object.
        country = {
            'name' => exact_country['name'],
            'alpha_2' => alpha_2_country_code,
            'alpha_3' => exact_country['alpha_3'],
            'numeric' => exact_country['numeric'],
        }
        cleaned_data_value['country'] = country

        # Delete the no longer necessary standalone 'country_code' key.
        cleaned_data_value.delete('country_code')
    end

    event.set('cleaned_data', cleaned_data_value)
    return [event]
end

# test "Country filter" do

#     in_event { { 'country_value' => "UA" } }
  
#     expect("Get object data") do |events|
#       events.size == 1
#       events[0].get('country')['name'] == "Ukraine"
#       events[0].get('country')['alpha_2'] == "UA"
#       events[0].get('country')['alpha_3'] == "UKR"
#       events[0].get('country')['numeric'] == "804"
#     end
# end
