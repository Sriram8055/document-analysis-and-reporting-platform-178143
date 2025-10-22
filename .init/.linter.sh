#!/bin/bash
cd /home/kavia/workspace/code-generation/document-analysis-and-reporting-platform-178143/document_backend
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

