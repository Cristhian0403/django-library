# 📚 Library Management System

This is a web-based **Library Management System** built with **Django** and **Django REST Framework**, which allows authenticated users to **view books**, **borrow and return books**, and for admin users to **manage the catalog**.

## 🚀 Features

- User authentication (signup, login, logout)
- List available books
- Borrow and return books
- Track loan history
- Create, update, and delete books (admin only)
- RESTful API integration for book and loan management

## 🛠 Tech Stack

- Django
- Django REST Framework
- Bootstrap (for frontend templates)
- SQLite (default dev database) and Postgress in production
- HTML/CSS (Django templates)

## ⚙️ Setup Instructions

### 1. Clone the Repository
    git clone https://github.com/Cristhian0403/django-library.git

### 2. Create and Activate a Virtual Environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

### 3. Install Dependencies
pip install -r requirements.txt

### 4. Apply Migrations and Create Superuser
python manage.py migrate
python manage.py createsuperuser

### 5. Run the Development Server
python manage.py runserver

Visit http://127.0.0.1:8000 in your browser.


## 📂 Project Structure
```
django_library/
├── api/                    # REST API logic (ViewSets, serializers)
├── djangolibrary/          # Main project folder (settings, urls, wsgi)               
├── library/                # App containing models, views, forms
├── manage.py
```
