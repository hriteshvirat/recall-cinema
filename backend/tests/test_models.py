import pytest
from backend.app.models import VisualEvent, MovieMetadata, ExtractionResult, AskResponse, SupportingEvent, TraceStep

def test_visual_event_validation():
    event = VisualEvent(
        event_id="evt_01",
        movie_id="movie_test",
        start_seconds=4.0,
        end_seconds=8.0,
        event_type="object_placed",
        characters=["Maya"],
        objects=["brown envelope", "wooden dining table"],
        location="kitchen dining table",
        action="places envelope on table",
        visual_description="Maya sets down a sealed brown envelope.",
        confidence=0.95
    )
    assert event.event_id == "evt_01"
    assert event.start_seconds == 4.0
    assert event.confidence == 0.95
    assert "Maya" in event.characters

def test_extraction_result():
    event = VisualEvent(
        event_id="evt_02",
        movie_id="movie_test",
        start_seconds=10.0,
        end_seconds=15.0,
        event_type="character_entered",
        characters=["Daniel"],
        objects=[],
        location="kitchen door",
        action="enters",
        visual_description="Daniel walks into the kitchen.",
        confidence=0.9
    )
    result = ExtractionResult(movie_id="movie_test", events=[event])
    assert len(result.events) == 1
    assert result.events[0].characters == ["Daniel"]

def test_ask_response_structure():
    supp = SupportingEvent(
        event_id="evt_01",
        start_seconds=4.0,
        end_seconds=8.0,
        description="Envelope placed on table"
    )
    trace = TraceStep(
        stage="ClickHouse MCP run_query",
        detail="Queried 3 rows",
        mcp_tool="run_query",
        sql_query="SELECT * FROM visual_events",
        rows_returned=3,
        duration_ms=12.5
    )
    resp = AskResponse(
        answer="The envelope was placed on the table at 00:04.",
        confidence=0.95,
        supporting_events=[supp],
        trace=[trace]
    )
    assert resp.confidence == 0.95
    assert len(resp.supporting_events) == 1
    assert resp.trace[0].rows_returned == 3
