require 'json'
require 'fileutils'

def filter(event)
    cleaned_data_value = event.get('cleaned_data_value')

    # Check whether the 'country_code' key exists.
    if cleaned_data_value.key?('country_code')
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

test 'country filter with valid country_code' do
    in_event {
        {
            'cleaned_data_value' => {
                'country_code' => 'YE'
            },
            'status' => 'RESOLVED'
        }
    }
  
    expect('removes country_code key') do |events|
        events.size == 1 && !events[0].get('cleaned_data').key?('country_code')
    end

    expect('returns event object with country object inside') do |events|
      events[0].get('cleaned_data')['country']['name'] == 'Yemen'
      events[0].get('cleaned_data')['country']['alpha_2'] == 'YE'
      events[0].get('cleaned_data')['country']['alpha_3'] == 'YEM'
      events[0].get('cleaned_data')['country']['numeric'] == '887'
    end

    expect('returns the event object with other non-country-related fields unchanged') do |events|
        events[0].get('status') == 'RESOLVED'
    end
end

test 'country filter with an object that lacks country_code' do
    in_event {
        {
            'cleaned_data_value' => {
                'name' => 'FUTURE FASHION'
            },
            'status' => 'RESOLVED'
        }
    }
  
    expect('returns the same object') do |events|
        events[0].get('cleaned_data').key?('name')
        events[0].get('status') == 'RESOLVED'
        !events[0].get('cleaned_data').key?('country')
    end
end
