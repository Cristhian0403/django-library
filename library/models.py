from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ROLE_CHOICES = (
        ('regular', 'Regular user'),
        ('admin', 'Administrator'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='regular')
    def __str__(self):
        return f'User {self.user.username}'

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    abstract = models.TextField(null=True, blank=True)
    publication_year = models.PositiveIntegerField()
    stock = models.PositiveIntegerField()
    borrowed_by = models.ManyToManyField(User, through='BookLoan', related_name='borrowed_books')

    def __str__(self):
        return f"{self.title} - {self.publication_year}"

class BookLoan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    loan_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"
