# Shared helper module for date formatting in Logstash filters.
module DateFormatterHelper
  # Formats a date field from event input to specified format.
  #
  # @param event [LogStash::Event] The event object.
  # @param input_field [String] The field name to read the date value from.
  # @param output_field [String] The field name to write the formatted date to.
  # @param format [String] The strftime format string (e.g., '%Y', '%Y-%m').
  # @return [LogStash::Event] The modified event
  def self.format_date_field(event, input_field, output_field, format)
    input_value = event.get(input_field)

    if input_value.nil?
      return event
    end

    # Parse and format the date.
    # Accepts values like '2023-12-01' or ISO8601 '2023-12-01T10:30:00Z'.
    begin
      t = Time.parse(input_value.to_s)
      event.set(output_field, t.strftime(format))
    rescue => e
      # If parsing fails, pass through original value (to avoid data loss).
      event.set(output_field, input_value)
    end

    event
  end
end

