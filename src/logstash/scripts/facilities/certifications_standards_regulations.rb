def filter(event)
    certifications_standards_regulations_value = event.get('certifications_standards_regulations_value')
  
    is_certifications_standards_regulations_value_valid = !certifications_standards_regulations_value.nil? && !certifications_standards_regulations_value.empty?
    event.set('certifications_standards_regulations', certifications_standards_regulations_value) if is_certifications_standards_regulations_value_valid
  
    return [event]
end
