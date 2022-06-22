FROM python:3.7-slim

ENV SECRET_KEY 'q&pf)9i(g(8#j%awos*$uggm8r%*h#-m^(9x#%ce991^mfhvpu'

COPY ./ /app

WORKDIR /app/

RUN pip3 install -r requirements.txt --no-cache-dir

RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "food_assistance.wsgi:application", "--bind", "0:8000" ]