import json
import logging
import os

import requests

from lib.cuckoo.common.abstracts import Processing
from lib.cuckoo.common.exceptions import CuckooProcessingError
from lib.cuckoo.common.path_utils import path_write_file

log = logging.getLogger(__name__)


class Ollama(Processing):
    """Query a local Ollama instance for a summary of analysis results."""

    order = 99

    def run(self):
        self.key = "ollama"

        host = self.options.get("host", "http://192.168.1.183:11434")
        model = self.options.get("model", "deepseek-r1:latest")
        prompt = self.options.get(
            "prompt",
            (
                "Provide a short explanation of this CAPE analysis output, "
                "predict the malware's behaviour and map findings to MITRE ATT&CK techniques."
            ),
        )

        summary_prompt = f"{prompt}\n\nResults:\n" + json.dumps(self.results, default=str)[:10000]

        try:
            r = requests.post(
                f"{host}/api/generate",
                json={"model": model, "prompt": summary_prompt, "stream": False},
                timeout=60,
            )
            r.raise_for_status()
            summary = r.json().get("response")
        except Exception as e:
            raise CuckooProcessingError(f"Failed to query Ollama: {e}")

        try:
            summary_path = os.path.join(self.analysis_path, "ollama_summary.txt")
            path_write_file(summary_path, summary or "", mode="text")
        except Exception as e:
            raise CuckooProcessingError(f"Failed to store Ollama summary: {e}")

        return {"summary": summary}
