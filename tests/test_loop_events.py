from tonesoul.loop.config import LoopConfig, LoopResult
from tonesoul.loop.events import (
    AIResponseEvent,
    ErrorEvent,
    IterationCompleteEvent,
    IterationStartEvent,
    LoopCancelledEvent,
    LoopCompleteEvent,
    LoopEvent,
    LoopFailedEvent,
    LoopStartEvent,
    PromiseDetectedEvent,
    ToolExecutionEvent,
    ToolExecutionStartEvent,
    VowDeclarationEvent,
)


def test_base_and_loop_lifecycle_events_to_dict():
    base = LoopEvent(event_type="custom")
    started = LoopStartEvent(config=LoopConfig(max_iterations=3, timeout_ms=15))
    completed = LoopCompleteEvent(result=LoopResult(state="complete", iterations=2, duration_ms=9))

    assert base.to_dict() == {"event_type": "custom"}
    assert started.to_dict() == {"event_type": "loop_start", "max_iterations": 3, "timeout_ms": 15}
    assert completed.to_dict() == {"event_type": "loop_complete", "iterations": 2, "duration_ms": 9}


def test_loop_failed_and_error_events_include_error_fields():
    failed = LoopFailedEvent(
        error=ValueError("boom"),
        result=LoopResult(state="failed", iterations=4, duration_ms=11),
    )
    error = ErrorEvent(error=RuntimeError("bad"), iteration=7, recoverable=False)

    assert failed.to_dict() == {"event_type": "loop_failed", "error": "boom", "iterations": 4}
    assert error.to_dict() == {
        "event_type": "error",
        "error": "bad",
        "iteration": 7,
        "recoverable": False,
    }


def test_iteration_start_event_serializes_iteration_fields():
    event = IterationStartEvent(iteration=2, max_iterations=5)

    assert event.to_dict() == {
        "event_type": "iteration_start",
        "iteration": 2,
        "max_iterations": 5,
    }


def test_non_overridden_events_keep_base_to_dict_shape():
    assert LoopCancelledEvent(
        result=LoopResult(state="cancelled", iterations=1, duration_ms=2)
    ).to_dict() == {"event_type": "loop_cancelled"}
    assert IterationCompleteEvent(iteration=2, duration_ms=12).to_dict() == {
        "event_type": "iteration_complete"
    }
    assert AIResponseEvent(text="hello", iteration=1).to_dict() == {"event_type": "ai_response"}
    assert ToolExecutionStartEvent(
        tool_name="search", parameters={"q": "x"}, iteration=1
    ).to_dict() == {"event_type": "tool_execution_start"}
    assert ToolExecutionEvent(
        tool_name="search",
        parameters={"q": "x"},
        result="ok",
        duration_ms=5,
        iteration=1,
    ).to_dict() == {"event_type": "tool_execution"}
    assert PromiseDetectedEvent(
        phrase="I promise", source="ai_response", iteration=2
    ).to_dict() == {"event_type": "promise_detected"}
    assert VowDeclarationEvent(vow_id="v1", declared=True, iteration=3).to_dict() == {
        "event_type": "vow_declaration"
    }
