def filter(event)
  backfilled_fields_value = event.get('backfilled_fields_value')

  is_backfilled_fields_value_valid = !backfilled_fields_value.nil? && !backfilled_fields_value.empty?
  event.set('backfilled_fields', backfilled_fields_value) if is_backfilled_fields_value_valid

  return [event]
end

test 'backfilled_fields filter with valid backfilled_fields_value' do
  in_event {
    {
      'backfilled_fields_value' => ['name', 'address', 'country'],
      'status' => 'PENDING'
    }
  }

  expect('returns an object with backfilled_fields set') do |events|
    is_value_present = events[0].get('backfilled_fields_value') == ['name', 'address', 'country']
    is_status_present = events[0].get('status') == 'PENDING'
    is_backfilled_fields_present = events[0].get('backfilled_fields') == ['name', 'address', 'country']

    is_value_present && is_status_present && is_backfilled_fields_present
  end
end

test 'backfilled_fields filter with nil backfilled_fields_value' do
  in_event {
    {
      'backfilled_fields_value' => nil,
      'status' => 'PENDING'
    }
  }

  expect('returns the same object without backfilled_fields') do |events|
    is_value_nil = events[0].get('backfilled_fields_value').nil?
    is_status_present = events[0].get('status') == 'PENDING'
    is_backfilled_fields_absent = !events[0].to_hash.key?('backfilled_fields')

    is_value_nil && is_status_present && is_backfilled_fields_absent
  end
end

test 'backfilled_fields filter with empty backfilled_fields_value' do
  in_event {
    {
      'backfilled_fields_value' => [],
      'status' => 'PENDING'
    }
  }

  expect('returns the same object without backfilled_fields') do |events|
    is_value_empty = events[0].get('backfilled_fields_value') == []
    is_status_present = events[0].get('status') == 'PENDING'
    is_backfilled_fields_absent = !events[0].to_hash.key?('backfilled_fields')

    is_value_empty && is_status_present && is_backfilled_fields_absent
  end
end
