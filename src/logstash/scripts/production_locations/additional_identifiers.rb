require 'json'

def filter(event)
  rba_id = event.get('rba_id_value')
  duns_id = event.get('duns_id_value')
  lei_id = event.get('lei_id_value')

  rba_id_value = ""
  duns_id_value = ""
  lei_id_value = ""

  if rba_id && rba_id['raw_value']
    rba_id_value = JSON.parse(rba_id)['raw_value'].strip
  end

  if duns_id && duns_id['raw_value']
    duns_id_value = JSON.parse(duns_id)['raw_value'].strip
  end

  if lei_id && lei_id['raw_value']
    lei_id_value = JSON.parse(lei_id)['raw_value'].strip
  end

  additional_identifiers = {
    'rba_id' => rba_id_value,
    'duns_id' => duns_id_value,
    'lei_id' => lei_id_value
  }

  event.set('additional_identifiers', additional_identifiers)

  return [event]
end
