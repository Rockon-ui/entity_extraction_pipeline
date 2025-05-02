# Dockerfile for GLiNER-based entity extractor
FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --force-reinstall -r requirements.txt

# Do NOT copy extractor.py if you're mounting it at runtime
COPY extractor.py .

CMD ["python", "extractor.py"]
