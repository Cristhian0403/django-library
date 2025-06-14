# Import Django's built-in modules for user management, messaging, request handling, etc.
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.db import IntegrityError

# Import custom forms, models, and configuration
from .forms import BookForm
from .models import Book, Profile
from .config import API_BASE_URL
import requests  # Used to make HTTP requests to external/internal APIs

# View for displaying the homepage with a list of books from an external API
@login_required
def home(request):
    url = f'{API_BASE_URL}/api/books/'
    cookies = {
        'sessionid': request.COOKIES.get('sessionid')  # Pass session cookie for authentication
    }
    response = requests.get(url, cookies=cookies)
    data = []
    if response.status_code == 200:
        data = response.json()
    else:
        data = []

    return render(request, 'home.html', {
        'books': data  # Render the list of books in the template
    })

# View to list current book loans from the API
@login_required
def books(request):
    cookies = {
        'sessionid': request.COOKIES.get('sessionid')
    }
    url = f'{API_BASE_URL}/api/loans/'
    response = requests.get(url, cookies=cookies)

    loans = response.json() if response.status_code == 200 else []
    return render(request, 'books.html', {
        'loans': loans
    })

# View to borrow a book by sending a POST request to the API
@login_required
def borrow_book(request, book_id):
    url = f'{API_BASE_URL}/api/loans/create-loan/'
    csrf_token = request.COOKIES.get('csrftoken')
    headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf_token,
        'Referer': API_BASE_URL
    }

    cookies = {
        'sessionid': request.COOKIES.get('sessionid'),
        'csrftoken': csrf_token
    }

    payload = {
        'book_id': book_id
    }

    response = requests.post(url, json=payload, cookies=cookies, headers=headers)

    if response.status_code == 201:
        messages.success(request, "Loan created successfully.")
        return redirect('books')

    # Handle possible errors
    try:
        loans = response.json()
    except ValueError:
        messages.warning(request, "Unexpected error occurred.")
        return redirect('books')

    if isinstance(loans, dict) and 'error' in loans:
        messages.warning(request, loans['error'])

    return redirect('books')

# View to return a borrowed book by sending a POST request to the API
@login_required
def return_book(request, book_id):
    url = f'{API_BASE_URL}/api/loans/return-loan/'
    csrf_token = request.COOKIES.get('csrftoken')
    headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf_token,
        'Referer': API_BASE_URL
    }

    cookies = {
        'sessionid': request.COOKIES.get('sessionid'),
        'csrftoken': csrf_token
    }

    payload = {
        'book_id': book_id
    }

    response = requests.post(url, json=payload, cookies=cookies, headers=headers)

    if response.status_code == 200:
        messages.success(request, "Book returned successfully.")
        return redirect('books')

    try:
        loans = response.json()
    except ValueError:
        messages.warning(request, "Unexpected error occurred.")
        return redirect('books')

    if isinstance(loans, dict) and 'error' in loans:
        messages.warning(request, loans['error'])

    return redirect('books')

# View to create a new book by submitting a form to the API
@login_required
def create_book(request):
    if request.method == 'GET':
        return render(request, 'create_book.html', {
            'form': BookForm
        })
    else:
        url = f'{API_BASE_URL}/api/books/'
        csrf_token = request.COOKIES.get('csrftoken')
        headers = {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrf_token,
            'Referer': API_BASE_URL
        }

        cookies = {
            'sessionid': request.COOKIES.get('sessionid'),
            'csrftoken': csrf_token
        }

        payload = request.POST.dict()
        response = requests.post(url, json=payload, cookies=cookies, headers=headers)

        if response.status_code == 201:
            messages.success(request, "Book created successfully.")
            return redirect('home')

        try:
            response = response.json()
        except ValueError:
            messages.warning(request, "Unexpected error occurred.")

        if isinstance(response, dict) and 'error' in response:
            messages.warning(request, response['error'])

        return render(request, 'create_book.html', {
            'form': BookForm,
        })

# View to delete a book by making a DELETE request to the API
@login_required
def delete_book(request, book_id):
    url = f'{API_BASE_URL}/api/books/{book_id}/'
    csrf_token = request.COOKIES.get('csrftoken')

    headers = {
        'X-CSRFToken': csrf_token,
        'Content-Type': 'application/json',
        'Referer': API_BASE_URL
    }

    cookies = {
        'sessionid': request.COOKIES.get('sessionid'),
        'csrftoken': csrf_token
    }

    try:
        response = requests.delete(url, headers=headers, cookies=cookies)

        if response.status_code == 204:
            messages.success(request, "Book deleted successfully.")
        elif response.status_code == 404:
            messages.error(request, "Book not found.")
        else:
            messages.error(request, f"Unexpected response: {response.status_code} - {response.text}")

    except requests.RequestException as e:
        messages.error(request, f"Request failed: {str(e)}")

    return redirect('home')

# View to view and update details of a specific book
@login_required
def detail_book(request, book_id):
    url = f'{API_BASE_URL}/api/books/{book_id}'
    cookies = {
        'sessionid': request.COOKIES.get('sessionid')
    }
    response = requests.get(url, cookies=cookies)

    if response.status_code == 200:
        data = response.json()
        book = Book(**data)
        form = BookForm(instance=book)

        if request.method == 'GET':
            return render(request, 'detail_book.html', {'book': book, 'form': form})

        # PATCH request to update the book
        url = f'{API_BASE_URL}/api/books/{book_id}/'
        csrf_token = request.COOKIES.get('csrftoken')

        headers = {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrf_token,
            'Referer': API_BASE_URL
        }

        cookies = {
            'sessionid': request.COOKIES.get('sessionid'),
            'csrftoken': csrf_token,
        }

        payload = request.POST.dict()
        response = requests.patch(url, json=payload, headers=headers, cookies=cookies)

        if response.status_code == 200:
            updated_data = response.json()
            form = BookForm(initial=updated_data)
            messages.success(request, "Book updated successfully.")
        else:
            messages.error(request, "Error updating book:" + response.content)

        return render(request, 'detail_book.html', {'book': book, 'form': form})

# View to handle user signup using Django's built-in form
def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm
        })
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                user.save()
                Profile.objects.create(user=user)
                login(request, user)  # Log the user in after successful registration
                return redirect('home')
            except IntegrityError:
                messages.warning(request, "User already exist.")
            except ValueError:
                messages.warning(request, "Invalid data provided. Please check your inputs.")
        else:
            messages.warning(request, "Password do not match")

        return render(request, 'signup.html', {
            'form': UserCreationForm
        })

# View to handle user logout
@login_required
def signout(request):
    logout(request)
    return redirect(home)

# View to handle user login
def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'User or Password is incorrect'
            })
        else:
            login(request, user)
            return redirect('home')

# Custom 404 handler to redirect authenticated or unauthenticated users accordingly
def custom_page_not_found_view(request, exception):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        return redirect('signin')
