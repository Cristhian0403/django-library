from rest_framework import serializers
from library.models import Book, BookLoan


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ('id', 'title', 'author', 'abstract','publication_year', 'stock') 
        

class BookLoanSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_id = serializers.IntegerField(source='book.id', read_only=True)
    book_author = serializers.CharField(source='book.author', read_only=True)

    class Meta:
        model = BookLoan
        fields = ['id', 'book_id', 'book_title', 'book_author', 'loan_date', 'return_date']