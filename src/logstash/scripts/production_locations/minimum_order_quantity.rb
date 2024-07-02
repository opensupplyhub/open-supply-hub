def filter(event)
    minimum_order_quantity_value = event.get('minimum_order_quantity_value')
  
    is_minimum_order_quantity_value_valid = !minimum_order_quantity_value.nil? && !minimum_order_quantity_value.strip.empty?
    event.set('minimum_order_quantity', minimum_order_quantity_value) if is_minimum_order_quantity_value_valid
  
    return [event]
end
