FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN python -m spacy download en_core_web_sm

COPY . .

# Expose the port the app runs on
EXPOSE 8080

CMD ["python", "test_api.py"]
