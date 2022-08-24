<img src="static/image/logo.png" width="100" style="display:block" />

# Publiso

Publiso is an online ebook store and reader platform. [Visit Website](https://publizo.herokuapp.com/)

## Screenshot

![Website Screenshot](https://github.com/pulimoodan/publiso/blob/master/Screenshot%20(41).png)

## Installation

Download publiso source code as zip and unzip it into a directory.
Install virtual environment.
For Linux:
```
   $	sudo apt-get install python-pip
   $	pip install virtualenv
   $	virtualenv virtualenv_name
   $	source virtualenv_name/bin/activate
```
For Windows:
```
   $	pip install virtualenv
   $	virtualenv myenv
   $	myenv\Scripts\activate.bat
```
Then, install required packages
```
   $	pip install -r requirements.txt
```

### Initialization

Create a `.env` file in the project directory:
```
   EMAIL_HOST_NAME = 'your email'
   EMAIL_HOST_PASSWORD = 'your password'
```
Also make sure to edit port and smtp server in the `settings.py`
```
   EMAIL_BACKEND = 'your backend'
   EMAIL_HOST = 'your smtp'
   EMAIL_USE_TLS = True or False
   EMAIL_PORT = your port
```
At last create a db.sqlite3 in the same directory and run:
```
   $	python manage.py makemigrations
   $	python manage.py migrate
```

Don't forget to create a superuser:
```
   $	python manage.py createsuperuser
```

### Run

```
   $	python manage.py runserver
```

Add some books, authors and categories at : http://127.0.0.1:8000/admin and you are ready to go.
