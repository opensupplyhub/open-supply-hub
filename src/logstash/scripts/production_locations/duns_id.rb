require 'json'

def filter(event)
  duns_id = event.get('duns_id_value')
  duns_id_value = ""

  if duns_id
    begin
      parsed = JSON.parse(duns_id)
      if parsed['raw_value']
        duns_id_value = parsed['raw_value'].strip
      end
    rescue JSON::ParserError => e
      duns_id_value = ""
    end
  end

  event.set('duns_id', duns_id_value)

  return [event]
end
