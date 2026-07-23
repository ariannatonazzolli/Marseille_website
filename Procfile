release: cd django_app && python manage.py collectstatic --noinput && python manage.py migrate
web: cd django_app && gunicorn Marseille_website.wsgi

