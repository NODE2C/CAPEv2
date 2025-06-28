=======
OpenAI
=======

CAPE can request a short summary of analysis results using the OpenAI API. The
summary will be saved as ``ai_summary.txt`` in the analysis reports folder.

Configuration
=============

Add the following section to ``integrations.conf`` and supply your API key::

    [openai]
    enabled = yes
    api_key = sk-...

.. warning::
   AI-generated summaries may be inaccurate.
