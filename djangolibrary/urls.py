"""
URL configuration for djangolibrary project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler404
from library import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.signout, name='logout'),
    path('signin/', views.signin, name='signin'),
    path('books/', views.books, name='books'),
    path('books/create/', views.create_book, name='create_book'),
    path('books/<int:book_id>/', views.detail_book, name='detail_book'),
    path('books/<int:book_id>/borrow', views.borrow_book, name='borrow_book'),
    path('books/<int:book_id>/return', views.return_book, name='return_book'),
    path('books/<int:book_id>/delete', views.delete_book, name='delete_book'),
]

handler404 = views.custom_page_not_found_view