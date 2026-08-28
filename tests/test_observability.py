from app.observability import JsonFormatter


def test_json_formatter_includes_structured_request_fields():
    import logging

    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="ignored message",
        args=(),
        exc_info=None,
    )
    record.event = "chat_request_completed"
    record.method = "POST"
    record.path = "/chat"
    record.status = "success"
    record.agent = "knowledge"
    record.duration_ms = 12.5

    output = JsonFormatter().format(record)

    assert '"event": "chat_request_completed"' in output
    assert '"agent": "knowledge"' in output
    assert '"duration_ms": 12.5' in output