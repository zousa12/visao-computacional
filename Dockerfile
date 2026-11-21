FROM python:3.12.14-slim

WORKDIR /app
ENV HISTORY_DB_PATH=/app/data/history.sqlite3

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt && python -m pip check

COPY app.py challenge_ui.py answer_validation.py session_progress.py image_input.py transformations.py history_store.py history_ui.py ./
COPY test_transformations.py test_scaling.py test_mirroring.py test_rgb.py test_feedback.py test_progress.py test_image_input.py test_app.py test_interface.py test_session_ui.py test_flow.py test_support.py test_history.py test_history_ui.py ./
RUN python -m unittest discover -v

EXPOSE 8501
CMD ["python", "-m", "streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
