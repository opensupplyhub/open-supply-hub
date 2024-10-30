def filter(event)
    claim_id_value = event.get('claim_id_value')

    is_claim_id_value_valid = !claim_id_value.nil?
    event.set('claim_id', claim_id_value) if is_claim_id_value_valid

    return [event]
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