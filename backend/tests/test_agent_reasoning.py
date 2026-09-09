import pytest
from agent.recall_agent import recall_agent

def test_sql_query_formulation():
    movie_id = "movie_kitchen_mystery"

    # 1. Earliest event
    q1 = "Where was the envelope first seen?"
    sql1 = recall_agent.formulate_focused_sql(movie_id, q1)
    assert "has(objects, 'brown envelope')" in sql1
    assert "ORDER BY start_seconds ASC" in sql1
    assert "LIMIT 3" in sql1

    # 2. Who picked up / moved
    q2 = "Who picked up the envelope?"
    sql2 = recall_agent.formulate_focused_sql(movie_id, q2)
    assert "has(objects, 'brown envelope')" in sql2
    assert "object_moved" in sql2 or "object_placed" in sql2

    # 3. Where did it end up / hidden
    q3 = "Where did the envelope end up?"
    sql3 = recall_agent.formulate_focused_sql(movie_id, q3)
    assert "ORDER BY start_seconds DESC" in sql3

    # 4. After Maya left
    q4 = "What changed after Maya left?"
    sql4 = recall_agent.formulate_focused_sql(movie_id, q4)
    assert "Maya" in sql4
    assert "character_exited" in sql4

    # 5. Still on the table
    q5 = "Was the envelope still on the table?"
    sql5 = recall_agent.formulate_focused_sql(movie_id, q5)
    assert "wooden dining table" in sql5 or "brown envelope" in sql5

def test_deterministic_temporal_synthesis():
    rows = [
        {
            "event_id": "evt_03",
            "start_seconds": 7.0,
            "end_seconds": 11.0,
            "characters": ["Maya"],
            "objects": ["brown envelope", "wooden dining table"],
            "location": "kitchen dining table",
            "action": "places brown envelope on table",
            "visual_description": "Maya carefully places the brown envelope flat on the table.",
            "confidence": 0.99
        }
    ]

    ans, conf, supp = recall_agent._deterministic_synthesis("Where was the envelope first seen?", rows)
    assert "table" in ans.lower()
    assert "00:07" in ans or "00:00" in ans or "maya" in ans.lower()
    assert conf >= 0.9
    assert len(supp) > 0
    assert supp[0].event_id == "evt_03"
