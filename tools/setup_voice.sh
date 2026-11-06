#!/usr/bin/env bash
# Sets up the open-source narration voice (Kokoro, Apache 2.0) in a Python 3.12 environment.
# Usage: tools/setup_voice.sh DIR    (then: DIR/bin/python tools/voice_kokoro.py ...)
set -euo pipefail
DIR=${1:?usage: tools/setup_voice.sh DIR}
uv venv -q -p python3.12 "$DIR"
uv pip install -q -p "$DIR/bin/python" torch --index-url https://download.pytorch.org/whl/cpu
uv pip install -q -p "$DIR/bin/python" "kokoro>=0.9" soundfile numpy
uv pip install -q -p "$DIR/bin/python" "en_core_web_sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl"
"$DIR/bin/python" -c "import kokoro; print('kokoro', kokoro.__version__, 'ready')"
