# Shared helper for normalizing date fields in Logstash filters.
#
# @param event [LogStash::Event] The event object to modify
# @param source_key [String] The key to read the date value from
# @param target_key [String] The key to write the normalized date to
# @param format [String] The strftime format string (e.g., '%Y-%m', '%Y')
# @return [void]
def normalize_date_field(event, source_key, target_key, format)
  value = event.get(source_key)
  return if value.nil?

  begin
    t = Time.parse(value.to_s)
    event.set(target_key, t.strftime(format))
  rescue StandardError => error
    # Log parse failure and set to nil to avoid OpenSearch format mismatch.
    logger.warn("Failed to parse #{source_key}: '#{value}'. Error: #{error.message}")
    event.set(target_key, nil)
  end
end

# Generates standard test cases for date filter fields.
#
# @param source_key [String] The key to read the date value from
# @param target_key [String] The key to write the normalized date to
# @param expected_format [String] The expected output format (e.g., '2023-12', '2023')
# @return [void]
def define_date_filter_tests(source_key, target_key, expected_format)
  test "#{target_key} filter with ISO datetime value" do
    in_event { { source_key => '2023-12-01T10:30:00Z' } }

    expect("sets #{target_key} field to normalized date") do |events|
        events.size == 1 &&
        events[0].get(target_key) == expected_format
    end
  end

  test "#{target_key} filter with date string" do
    in_event { { source_key => '2023-12-01' } }

    expect("normalizes #{target_key} field") do |events|
        events.size == 1 &&
        events[0].get(target_key) == expected_format
    end
  end

  test "#{target_key} filter with nil value" do
    in_event { { source_key => nil } }

    expect("does not set #{target_key} field when value is nil") do |events|
        events.size == 1 &&
        !events[0].to_hash.key?(target_key)
    end
  end

  test "#{target_key} filter with invalid date string" do
    in_event { { source_key => 'invalid-date' } }

    expect("sets #{target_key} to nil and logs parse error") do |events|
        events.size == 1 &&
        events[0].get(target_key).nil?
    end
  end
end

