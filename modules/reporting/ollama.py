import json
import logging

import requests

from lib.cuckoo.common.abstracts import Report

log = logging.getLogger(__name__)


class OLLAMA(Report):
    """Use a local Ollama instance to summarize analysis results."""

    order = 50

    def run(self, results):
        host = self.options.get("host", "http://192.168.1.183:11434")
        model = self.options.get("model", "deepseek-r1:latest")
        prompt = self.options.get(
            "prompt",
            "Provide a short explanation of this CAPE analysis output, predict the malware\u2019s behaviour and map findings to MITRE ATT&CK techniques.",
        )
        try:
            summary_prompt = f"{prompt}\n\nResults:\n" + json.dumps(results, default=str)[:10000]
            r = requests.post(
                f"{host}/api/generate",
                json={"model": model, "prompt": summary_prompt, "stream": False},
                timeout=60,
            )
            r.raise_for_status()
            data = r.json()
            results["ollama_summary"] = data.get("response")
        except Exception as e:
            log.error("Ollama query failed: %s", e)
            results["ollama_summary_error"] = str(e)
