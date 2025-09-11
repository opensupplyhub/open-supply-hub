import types
import pytest

# We will import the module under test; if the project uses Django settings, pytest-django should handle setup.
from api.moderation_event_actions.creation.location_contribution import (  # type: ignore
    processors as lc_processors_pkg,  # to target submodule paths for monkeypatching
)
from api.moderation_event_actions.creation.location_contribution.processors import (
    contribution_processor as contribution_processor_mod,  # base interface path
)
from api.moderation_event_actions.creation.location_contribution.processors import (
    permission_processor as permission_processor_mod,
    source_processor as source_processor_mod,
    production_location_data_processor as prod_loc_data_processor_mod,
    geocoding_processor as geocoding_processor_mod,
)
from api.moderation_event_actions.creation.location_contribution.processors.contribution_processor import (
    ContributionProcessor,  # type: ignore
)
from api.moderation_event_actions.creation.location_contribution import location_contribution as location_contribution_mod


LocationContribution = location_contribution_mod.LocationContribution


class DummyDTO:
    def __init__(self, payload=None):
        self.payload = payload or {}
    def __repr__(self):
        return "DummyDTO(%r)" % self.payload


class StubProcessor(ContributionProcessor):
    def __init__(self, name, side_effect=None, mutate=None):
        super().__init__()
        self.name = name
        self.calls = []
        self.side_effect = side_effect  # Optional exception to raise
        self.mutate = mutate  # Optional function(dto) -> dto

    def process(self, event_dto):
        self.calls.append(("process", event_dto))
        if self.side_effect:
            raise self.side_effect
        outgoing = self.mutate(event_dto) if self.mutate else event_dto
        return super().process(outgoing)  # will pass to next if any


def _install_stub_chain(monkeypatch, stubs):
    """
    Monkeypatch the concrete processors to return our stub instances in precise order:
    PermissionProcessor -> SourceProcessor -> ProductionLocationDataProcessor -> GeocodingProcessor
    """
    # Map concrete classes to stub factories
    monkeypatch.setattr(permission_processor_mod, "PermissionProcessor", lambda: stubs[0], raising=True)
    monkeypatch.setattr(source_processor_mod, "SourceProcessor", lambda: stubs[1], raising=True)
    monkeypatch.setattr(prod_loc_data_processor_mod, "ProductionLocationDataProcessor", lambda: stubs[2], raising=True)
    monkeypatch.setattr(geocoding_processor_mod, "GeocodingProcessor", lambda: stubs[3], raising=True)


def test_serialize_links_processors_in_correct_order_and_calls_process(monkeypatch):
    # Arrange
    p = StubProcessor("Permission")
    s = StubProcessor("Source")
    d = StubProcessor("ProductionLocation")
    g = StubProcessor("Geocoding")

    _install_stub_chain(monkeypatch, [p, s, d, g])

    dto = DummyDTO({"raw": True})
    lc = LocationContribution()

    # Act
    result = lc.serialize(dto)

    # Assert: first processor handles the call
    assert p.calls == [("process", dto)]
    # After calling first, it should propagate through .set_next chain into others via base class
    # Verify subsequent processors received the DTO (or mutated dto) in order
    assert ("process", dto) in s.calls or len(s.calls) == 1  # It should have been called once
    assert len(s.calls) == 1, "Source processor should be invoked exactly once"
    assert len(d.calls) == 1, "ProductionLocationDataProcessor should be invoked exactly once"
    assert len(g.calls) == 1, "GeocodingProcessor should be invoked exactly once"

    # The result should bubble from the last processor if they don't mutate/override
    # Our StubProcessor passes through by default; base class returns next.process(...) or dto
    assert result is dto


def test_serialize_propagates_mutations_through_chain(monkeypatch):
    # Arrange: each step mutates DTO reference to verify propagation
    def m1(x): return DummyDTO({**x.payload, "perm": "ok"})
    def m2(x): return DummyDTO({**x.payload, "source": "user"})
    def m3(x): return DummyDTO({**x.payload, "normalized": True})
    def m4(x): return DummyDTO({**x.payload, "geocoded": {"lat": 1.0, "lng": 2.0}})

    p = StubProcessor("Permission", mutate=m1)
    s = StubProcessor("Source", mutate=m2)
    d = StubProcessor("ProductionLocation", mutate=m3)
    g = StubProcessor("Geocoding", mutate=m4)

    _install_stub_chain(monkeypatch, [p, s, d, g])

    dto = DummyDTO({"raw": True})
    lc = LocationContribution()

    # Act
    result = lc.serialize(dto)

    # Assert
    assert isinstance(result, DummyDTO)
    assert result.payload == {
        "raw": True,
        "perm": "ok",
        "source": "user",
        "normalized": True,
        "geocoded": {"lat": 1.0, "lng": 2.0},
    }


def test_serialize_returns_first_processor_result_even_if_next_is_none(monkeypatch):
    # Arrange: create only first processor, with no next; it should return its processed dto
    def mutate(x): return DummyDTO({**x.payload, "only": "first"})
    p = StubProcessor("Permission", mutate=mutate)

    # Monkeypatch constructors: subsequent processors still constructed but we disconnect by not setting next on p
    # To simulate "no next", we replace __setup_location_data_processors to return just p (no linking).
    def fake_setup():
        return p
    monkeypatch.setattr(location_contribution_mod.LocationContribution, "_LocationContribution__setup_location_data_processors", staticmethod(fake_setup), raising=True)

    dto = DummyDTO({"raw": True})
    lc = LocationContribution()

    # Act
    result = lc.serialize(dto)

    # Assert: Only first processor processed, and result came from it
    assert p.calls == [("process", dto)]
    assert result.payload == {"raw": True, "only": "first"}


def test_serialize_stops_on_exception_and_bubbles_error(monkeypatch):
    # Arrange: second processor fails
    p = StubProcessor("Permission")
    failing_exc = ValueError("invalid source")
    s = StubProcessor("Source", side_effect=failing_exc)
    d = StubProcessor("ProductionLocation")
    g = StubProcessor("Geocoding")

    _install_stub_chain(monkeypatch, [p, s, d, g])

    dto = DummyDTO({"raw": True})
    lc = LocationContribution()

    # Act / Assert
    with pytest.raises(ValueError) as ei:
        lc.serialize(dto)

    assert "invalid source" in str(ei.value)
    # First two should have been called; downstream should not
    assert len(p.calls) == 1
    assert len(s.calls) == 1
    assert len(d.calls) == 0
    assert len(g.calls) == 0


def test_internal_chain_wiring_uses_set_next_in_declared_order(monkeypatch):
    """
    Verifies that __setup_location_data_processors links processors in declared order:
      Permission -> Source -> ProductionLocationData -> Geocoding
    We assert that each stub's 'next' attribute is set to the subsequent stub.
    """
    p = StubProcessor("Permission")
    s = StubProcessor("Source")
    d = StubProcessor("ProductionLocation")
    g = StubProcessor("Geocoding")

    recorded_set_next = []
    # Wrap set_next to record exact linkage order while preserving behavior
    def wrap_set_next(self, nxt):
        recorded_set_next.append((self.name, getattr(nxt, "name", type(nxt).__name__)))
        return super(StubProcessor, self.__class__).set_next(self, nxt)

    monkeypatch.setattr(StubProcessor, "set_next", wrap_set_next, raising=True)
    _install_stub_chain(monkeypatch, [p, s, d, g])

    # Call the internal setup directly via name-mangled accessor
    setup = getattr(LocationContribution, "_LocationContribution__setup_location_data_processors")
    first = setup()

    # Assert: first is head of chain
    assert first is p
    # Assert linkage order captured
    assert recorded_set_next == [
        ("Permission", "Source"),
        ("Source", "ProductionLocation"),
        ("ProductionLocation", "Geocoding"),
    ]