FROM python:3.7-slim

COPY ./ /app

WORKDIR /app/food_assistance/

RUN pip3 install -r requirements.txt --no-cache-dir

CMD ["gunicorn", "food_assistance.wsgi:application", "--bind", "0:8000" ]