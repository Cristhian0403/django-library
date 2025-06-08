from django.db import models
from django.contrib.auth.models import User

# Extends the built-in User model with an additional role field
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # One-to-one relationship with User
    ROLE_CHOICES = (
        ('regular', 'Regular user'),      # Default user
        ('admin', 'Administrator'),       # Admin with elevated permissions
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='regular')  # Role field

    def __str__(self):
        return f'User {self.user.username}'  # Display user info in admin panel

# Represents a book in the system
class Book(models.Model):
    title = models.CharField(max_length=200)              # Title of the book
    author = models.CharField(max_length=100)             # Author name
    abstract = models.TextField(null=True, blank=True)    # Optional description or summary
    publication_year = models.PositiveIntegerField()      # Year of publication
    stock = models.PositiveIntegerField()                 # Number of available copies
    borrowed_by = models.ManyToManyField(
        User,
        through='BookLoan',                               # Link to BookLoan model
        related_name='borrowed_books'                     # Enables user.borrowed_books
    )

    def __str__(self):
        return f"{self.title} - {self.publication_year}"  # Display format

# Represents a loan of a book to a user
class BookLoan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User who borrowed the book
    book = models.ForeignKey(Book, on_delete=models.CASCADE)  # Book being borrowed
    loan_date = models.DateField(auto_now_add=True)           # Date when loan was created
    return_date = models.DateField(null=True, blank=True)     # Optional return date

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"     # Display format
