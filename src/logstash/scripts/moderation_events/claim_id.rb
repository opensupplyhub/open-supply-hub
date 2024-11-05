def filter(event)
    claim_id_value = event.get('claim_id_value')

    is_claim_id_value_valid = !claim_id_value.nil?
    event.set('claim_id', claim_id_value) if is_claim_id_value_valid

    return [event]
end

test 'claim_id filter with valid claim_id_value' do
    in_event {
        {
            'claim_id_value' => 12,
            'status' => 'PENDING'
        }
    }
  
    expect('returns an object with claim_id set') do |events|
        is_claim_id_value_present = events[0].get('claim_id_value') == 12
        is_status_present = events[0].get('status') == 'PENDING'
        is_claim_id_present = events[0].get('claim_id') == 12

        is_claim_id_value_present && is_status_present && is_claim_id_present
    end
end

test 'claim_id filter with nil claim_id_value' do
    in_event {
        {
            'claim_id_value' => nil,
            'status' => 'PENDING'
        }
    }
  
    expect('returns the same object') do |events|
        is_claim_id_value_nil = events[0].get('claim_id_value').nil?
        is_status_present = events[0].get('status') == 'PENDING'
        is_claim_id_present = events[0].to_hash.key?('claim_id')

        is_claim_id_value_nil && is_status_present && !is_claim_id_present
    end
end
