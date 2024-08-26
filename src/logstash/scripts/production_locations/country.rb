require 'json'
require 'fileutils'

def filter(event)
    # Country code Alpha-2 data
    alpha_2_country_code = event.get('country_value')

    # Define the path to the JSON file's
    json_names_file_path = File.expand_path('../../data/country_names.json', __FILE__)
    json_alpha3_file_path = File.expand_path('../../data/country_alpha_3.json', __FILE__)
    json_numeric_file_path = File.expand_path('../../data/country_numeric.json', __FILE__)

    # Read and parse the JSON file's
    json_names_data = File.read(json_names_file_path)
    country_names = JSON.parse(json_names_data)

    json_alpha3_data = File.read(json_alpha3_file_path)
    country_alpha3 = JSON.parse(json_alpha3_data)

    json_numeric_data = File.read(json_numeric_file_path)
    country_numeric = JSON.parse(json_numeric_data)

    # Build country object
    country = {
        'name' => country_names[alpha_2_country_code],
        'alpha_2' => alpha_2_country_code,
        'alpha_3' => country_alpha3[alpha_2_country_code],
        'numeric' => country_numeric[alpha_2_country_code],
    }
    event.set('country', country)
  
    return [event]
end
