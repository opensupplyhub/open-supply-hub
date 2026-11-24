# Runs the inline logstash script-test DSL tests embedded in the Ruby
# filter scripts under src/logstash/scripts/**/*.rb.
#
# Logstash's ruby filter plugin supports inline tests
# (test / in_event / expect blocks), but it only executes them when a
# pipeline loads the script with script-level testing enabled - which no
# CI job and no deployed pipeline ever does. This runner executes those
# same tests with a plain Ruby interpreter (stdlib only, no gems) so they
# run on every pull request.
#
# Event shim scope: the scripts only ever call event.get(key),
# event.set(key, value), event.to_hash and event.include?(key) with
# top-level string keys. Bracketed field references like '[a][b]' are NOT
# implemented because no script uses them; if one ever does, extend
# LogstashTestEvent accordingly.
#
# Usage: ruby src/logstash/tests/run_filter_tests.rb
# (or the wrapper: scripts/run_logstash_filter_tests)

# Ratchet: the number of filter scripts that define no inline tests must
# not exceed this ceiling. Lower it as tests are added; never raise it.
NO_TEST_CEILING = 15

# load(path, module) - the isolation mechanism below - only exists from
# Ruby 3.1; on older rubies it degrades to load(path, true) and every
# script lands in a throwaway module, so no tests would run at all.
if Gem::Version.new(RUBY_VERSION) < Gem::Version.new('3.1')
  abort "run_filter_tests.rb needs Ruby 3.1+ (found #{RUBY_VERSION}); " \
        'use scripts/run_logstash_filter_tests, which falls back to docker.'
end

require 'json'
# The scripts rely on Time.parse without requiring 'time' themselves
# (logstash's JRuby runtime preloads it), so load it here.
require 'time'

SCRIPTS_DIR = File.expand_path('../scripts', __dir__)

# --- Minimal logstash-compatible Event -------------------------------------

class LogstashTestEvent
  def initialize(data = {})
    @data = data
  end

  def get(key)
    @data[key]
  end

  def set(key, value)
    @data[key] = value
    value
  end

  def to_hash
    @data
  end

  def include?(key)
    @data.key?(key)
  end
end

def deep_dup(value)
  case value
  when Hash
    value.each_with_object({}) { |(k, v), h| h[deep_dup(k)] = deep_dup(v) }
  when Array
    value.map { |v| deep_dup(v) }
  when String
    value.dup
  else
    value
  end
end

# --- The script-test DSL ----------------------------------------------------
#
# Defined at the top level (i.e. as private methods on Object) so they are
# reachable from every context a script runs in: the wrapped-load toplevel,
# blocks defined there, and helper methods pulled in via require_relative
# (e.g. define_date_filter_tests in date_filter_helpers.rb).

$registered_tests = nil # collects {name:, block:} while a script loads
$current_test = nil     # collects in_event/expect while a test block runs

def test(name, &block)
  raise 'test called outside of a script load' if $registered_tests.nil?

  $registered_tests << { name: name, block: block }
end

def in_event(&block)
  $current_test[:in_events] = [block.call]
end

def in_events(&block)
  $current_test[:in_events] = block.call
end

def expect(description, &block)
  $current_test[:expects] << { description: description, block: block }
end

# --- Loading and running ----------------------------------------------------

# Loads one filter script in isolation: `load` with a fresh wrap module
# keeps each script's `def filter` (plus helper methods and constants) off
# the global namespace so definitions never collide across scripts.
# `require_relative` calls inside a script (shared helpers) still work
# because requires are global and idempotent.
def load_script(path)
  wrap_module = Module.new
  $registered_tests = []
  load(path, wrap_module)
  tests = $registered_tests
  $registered_tests = nil
  context = Object.new
  context.extend(wrap_module)
  [context, tests]
end

def run_test(context, test_entry)
  $current_test = { in_events: [{}], expects: [] }
  test_entry[:block].call
  input_events = $current_test[:in_events].map do |hash|
    LogstashTestEvent.new(deep_dup(hash))
  end
  results = input_events.flat_map { |event| context.send(:filter, event) }
  failures = []
  $current_test[:expects].each do |expectation|
    passed = expectation[:block].call(results)
    failures << "expect failed: #{expectation[:description]}" unless passed
  rescue StandardError => error
    failures << "expect raised #{error.class}: #{error.message} " \
                "(#{expectation[:description]})"
  end
  failures
ensure
  $current_test = nil
end

total_tests = 0
total_failures = 0
untested_scripts = []
helper_scripts = []

script_paths = Dir.glob(File.join(SCRIPTS_DIR, '**', '*.rb')).sort
if script_paths.empty?
  warn "No scripts found under #{SCRIPTS_DIR}"
  exit 1
end

script_paths.each do |path|
  relative_path = path.sub("#{SCRIPTS_DIR}/", '')

  begin
    context, tests = load_script(path)
  rescue StandardError, ScriptError => error
    puts "== #{relative_path}"
    puts "  ERROR failed to load: #{error.class}: #{error.message}"
    total_failures += 1
    next
  end

  unless context.respond_to?(:filter, true)
    # Shared helper (e.g. date_filter_helpers.rb), not a filter script:
    # it is never loaded by a pipeline directly, so it is neither run
    # nor counted against the no-test ratchet.
    helper_scripts << relative_path
    next
  end

  if tests.empty?
    untested_scripts << relative_path
    next
  end

  puts "== #{relative_path} (#{tests.size} tests)"
  tests.each do |test_entry|
    total_tests += 1
    begin
      failures = run_test(context, test_entry)
    rescue StandardError => error
      failures = ["test raised #{error.class}: #{error.message}"]
    end
    if failures.empty?
      puts "  PASS #{test_entry[:name]}"
    else
      total_failures += 1
      puts "  FAIL #{test_entry[:name]}"
      failures.each { |failure| puts "       #{failure}" }
    end
  end
end

puts
puts "#{total_tests} tests, #{total_failures} failures"

unless helper_scripts.empty?
  puts "Skipped shared helpers (no filter defined): #{helper_scripts.join(', ')}"
end

puts
if untested_scripts.empty?
  puts 'Every filter script defines inline tests.'
else
  puts "Filter scripts with NO inline tests (#{untested_scripts.size}, " \
       "ceiling #{NO_TEST_CEILING}):"
  untested_scripts.each { |script| puts "  - #{script}" }
end

if untested_scripts.size > NO_TEST_CEILING
  puts
  puts "FAIL: #{untested_scripts.size} scripts without tests exceeds the " \
       "ceiling of #{NO_TEST_CEILING}. Add inline tests to new scripts " \
       '(see location_type.rb for the style); never raise the ceiling.'
  exit 1
end

# The scripts directory always carries tested filter scripts, so running
# zero tests means the harness itself broke (bad glob, load semantics,
# misclassification as helpers) - never a clean pass.
if total_tests.zero?
  puts
  puts 'FAIL: no tests were executed; the harness found no runnable ' \
       'filter tests, which indicates a harness defect, not a clean tree.'
  exit 1
end

exit 1 if total_failures.positive?
