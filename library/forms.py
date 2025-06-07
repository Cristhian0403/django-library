from django import forms
from .models import Book


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'abstract', 'publication_year', 'stock']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title'}),
            'author': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter author'}),
            'abstract': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter abstract'}),
            'publication_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 2024'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Available copies'}),
        }
