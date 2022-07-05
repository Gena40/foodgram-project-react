FROM python:3.7-slim

COPY ./ /app

WORKDIR /app

RUN python -m pip install --upgrade pip

RUN pip3 install -r requirements.txt --no-cache-dir

RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "food_assistance.wsgi:application", "--bind", "0:8000" ]