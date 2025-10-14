# Shared test helper module for date field filters.
module DateFieldTestHelper
  # Generates common date field filter tests.
  #
  # @param input_field [String] The input field name (e.g., 'opened_at_value')
  # @param output_field [String] The output field name (e.g., 'opened_at')
  # @param expected_format [String] The expected output format (e.g., '2023' or '2023-12')
  # @param format_description [String] Description of format (e.g., 'year' or 'year-month')
  def self.run_tests(input_field, output_field, expected_format, format_description)
    test "#{output_field} filter with ISO datetime value" do
      in_event { { input_field => '2023-12-01T10:30:00Z' } }

      expect("sets #{output_field} field as #{format_description}") do |events|
        events.size == 1 &&
        events[0].get(output_field) == expected_format
      end
    end

    test "#{output_field} filter with date string" do
      in_event { { input_field => '2023-12-01' } }

      expect("sets #{output_field} field as #{format_description}") do |events|
        events.size == 1 &&
        events[0].get(output_field) == expected_format
      end
    end

    test "#{output_field} filter with nil value" do
      in_event { { input_field => nil } }

      expect("does not set #{output_field} field when value is nil") do |events|
        events.size == 1 &&
        !events[0].to_hash.key?(output_field)
      end
    end
  end
end

