def filter(event)
    sector_value = event.get('sector_value')
  
    if sector_value.nil? then
        return [event]
    end

    redundant_sector_value = 'Unspecified'
    filtered_sector_value = sector_value.select { |value| value != redundant_sector_value }

    event.set('sector', filtered_sector_value) if !filtered_sector_value.empty?()
  
    return [event]
end
