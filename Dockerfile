FROM python:3.11.6-alpine

COPY ./requirements.txt /requirements.txt
WORKDIR /
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]