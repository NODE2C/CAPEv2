import json
import logging
import os

import requests

from lib.cuckoo.common.abstracts import Report
from lib.cuckoo.common.exceptions import CuckooReportError
from lib.cuckoo.common.path_utils import path_write_file

log = logging.getLogger(__name__)


class OLLAMA(Report):
    """Use a local Ollama instance to summarize analysis results."""

    order = 50

    def run(self, results):
        """Query a local Ollama instance for a human readable summary."""

        host = self.options.get("host", "http://192.168.1.183:11434")
        model = self.options.get("model", "deepseek-r1:latest")
        prompt = self.options.get(
            "prompt",
            "Provide a short explanation of this CAPE analysis output, predict the malware\u2019s behaviour and map findings to MITRE ATT&CK techniques.",
        )

        summary_prompt = f"{prompt}\n\nResults:\n" + json.dumps(results, default=str)[:10000]

        try:
            r = requests.post(
                f"{host}/api/generate",
                json={"model": model, "prompt": summary_prompt, "stream": False},
                timeout=60,
            )
            r.raise_for_status()
            data = r.json()
            summary = data.get("response")
        except Exception as e:
            raise CuckooReportError(f"Failed to query Ollama: {e}")

        results["ollama_summary"] = summary

        try:
            summary_path = os.path.join(self.reports_path, "ollama_summary.txt")
            path_write_file(summary_path, summary or "", mode="text")
        except Exception as e:
            raise CuckooReportError(f"Failed to store Ollama summary: {e}")
