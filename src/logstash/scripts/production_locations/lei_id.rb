require 'json'

def filter(event)
  lei_id = event.get('lei_id_value')
  lei_id_value = ""

  if lei_id
    begin
      parsed = JSON.parse(lei_id)
      if parsed['raw_value']
        lei_id_value = parsed['raw_value'].strip
      end
    rescue JSON::ParserError => e
      lei_id_value = ""
    end
  end

  event.set('lei_id', lei_id_value)

  return [event]
end
