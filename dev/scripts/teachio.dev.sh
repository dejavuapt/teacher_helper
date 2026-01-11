#!/bin/bash
echo "[LOG] RUN DEVELOPMENT SCRIPT"
uv run --env-file $STAGE_ENV -m $RUNNING_MODULE $@