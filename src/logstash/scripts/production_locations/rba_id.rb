require 'json'

def filter(event)
  rba_id = event.get('rba_id_value')
  rba_id_value = ""

    if rba_id
      begin
        parsed = JSON.parse(rba_id)
        if parsed['raw_value']
          rba_id_value = parsed['raw_value'].strip
        end
      rescue JSON::ParserError => e
        rba_id_value = ""
      end
    end

    event.set('rba_id', rba_id_value)

    return [event]
  end
