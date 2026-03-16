#!/bin/bash

export PYTHONPATH=$PYTHONPATH:.

poetry run fastapi dev studies_api/app.py