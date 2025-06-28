import types
from unittest.mock import patch

from modules.reporting.aisummary import AISummary, integrations_conf


def test_ai_summary(tmp_path):
    integrations_conf.openai.enabled = True
    integrations_conf.openai.api_key = "dummy"
    reporter = AISummary()
    reporter.reports_path = tmp_path
    results = {"target": {"file": {"name": "test.exe"}}, "info": {"score": 5}, "signatures": [{"name": "sig1"}]}

    fake_resp = types.SimpleNamespace(choices=[types.SimpleNamespace(message=types.SimpleNamespace(content="summary"))])

    with patch("openai.chat.completions.create", return_value=fake_resp) as mock_call:
        reporter.run(results)
        mock_call.assert_called_once()
        assert (tmp_path / "ai_summary.txt").read_text() == "summary"
