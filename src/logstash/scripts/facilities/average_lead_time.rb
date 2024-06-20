def filter(event)
    average_lead_time_value = event.get('average_lead_time_value')
  
    is_average_lead_time_value_valid = !average_lead_time_value.nil? && !average_lead_time_value.strip.empty?
    event.set('average_lead_time', average_lead_time_value) if is_average_lead_time_value_valid
  
    return [event]
end
