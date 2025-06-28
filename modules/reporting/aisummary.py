import logging
import os

from lib.cuckoo.common.abstracts import Report
from lib.cuckoo.common.config import Config
from lib.cuckoo.common.exceptions import CuckooReportError
from lib.cuckoo.common.path_utils import path_write_file

try:
    import openai

    HAVE_OPENAI = True
except ImportError:  # pragma: no cover - dependency is optional
    HAVE_OPENAI = False

integrations_conf = Config("integrations")
log = logging.getLogger(__name__)


class AISummary(Report):
    """Generate an OpenAI summary of analysis results.

    AI-generated summaries may contain inaccuracies.
    """

    order = 9999

    def run(self, results):
        if not HAVE_OPENAI:
            log.error("openai dependency is missing")
            return

        if not integrations_conf.openai.enabled:
            return

        if not integrations_conf.openai.api_key:
            log.error("OpenAI API key not configured")
            return

        openai.api_key = integrations_conf.openai.api_key

        selected = {
            "target": results.get("target"),
            "score": results.get("info", {}).get("score"),
            "signatures": [s.get("name") for s in results.get("signatures", [])],
        }
        try:
            resp = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": str(selected)}],
                max_tokens=150,
            )
            summary = resp.choices[0].message.content.strip()
            path_write_file(os.path.join(self.reports_path, "ai_summary.txt"), summary)
        except Exception as e:  # pragma: no cover - protective catch
            raise CuckooReportError(f"Failed to generate AI summary: {e}")
