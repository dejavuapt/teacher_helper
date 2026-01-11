#!/bin/bash

ENV="prod"
PROJECT_NAME="teachio"
ENTRY_POINT="main"

while [ $# -gt 0 ]
do
    case $1 in
        --dev) 
            ENV="dev" 
            shift
            ;;
        --prod) 
            ENV="prod" 
            shift
            ;;
        *) 
            break
            ;;
    esac
done

SCRIPT_DIR="./${ENV}/scripts/${PROJECT_NAME}.${ENV}.sh"
if [ ! -f "$SCRIPT_DIR" ]
then
    echo "[LOG] Script not found: $SCRIPT_DIR"
    exit 1
fi

if [ "$ENV" == "dev" ]
then
    uv sync 
else
    uv sync --no-dev
fi

export STAGE_ENV="${ENV}/.env"
export RUNNING_MODULE="app.${ENTRY_POINT}"
bash "$SCRIPT_DIR" "$@"
