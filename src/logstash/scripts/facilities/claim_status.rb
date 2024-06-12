def filter(event)
    claim_statuses = {
        'claimed' => 'claimed',
        'unclaimed' => 'unclaimed',
        'pending' => 'pending'
    }
    claim_status_value = event.get('claim_status_value')

    if claim_status_value&.include?('APPROVED')
        event.set('claim_status', claim_statuses['claimed'])
        return [event]
    
    if claim_status_value&.include?('PENDING')
        event.set('claim_status', claim_statuses['pending'])
        return [event]

    event.set('claim_status', claim_statuses['unclaimed'])
    return [event]
end
