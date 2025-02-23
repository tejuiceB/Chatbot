# Django Project Setup Commands

1. Install Django using pip:
```bash
pip install django
```

2. Create a new Django project:
```bash
django-admin startproject chatbot
```

3. Navigate to the project directory:
```bash
cd chatbot
```

4. Create a new app within your project:
```bash
python manage.py startapp myapp
```

5. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Create a superuser (admin account):
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

The server will start at http://127.0.0.1:8000/

Note: After creating your app, don't forget to:
1. Add your app to INSTALLED_APPS in settings.py
2. Set up your URLs in urls.py
3. Create your models in models.py
4. Create your views in views.py
