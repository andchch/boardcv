#!/bin/bash

exec python bg.py &
exec streamlit run Start.py --server.port=8501 --server.address=0.0.0.0
