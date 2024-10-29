def filter(event)
    claim_id_value = event.get('claim_id_value')

    is_claim_id_value_valid = !claim_id_value.nil?
    event.set('claim_id', claim_id_value) if is_claim_id_value_valid

    return [event]
end