require 'json'

# Simple test DSL
def test(description, &block)
  puts "\n🧪 Test: #{description}"
  block.call
end

def in_event(data = {}, &block)
  @event = MockEvent.new(data)
  @events = filter(@event)
end

def expect(desc, &condition)
  if condition.call(@events)
    puts "✅ #{desc}"
  else
    puts "❌ #{desc}"
    puts "   Got: #{@events[0].to_h.inspect}"
  end
end

# Mock Logstash-style Event
class MockEvent
  def initialize(data = {})
    @data = data
  end

  def get(key)
    @data[key]
  end

  def set(key, value)
    @data[key] = value
  end

  def to_h
    @data
  end
end
