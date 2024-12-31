FROM python:3.10-slim AS base
WORKDIR /main

COPY requirements.txt /main/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /main/

EXPOSE 5000

CMD ["python3", "main.py"]

