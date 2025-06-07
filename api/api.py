from library.models import Book, BookLoan
from rest_framework import viewsets, permissions
from .serializers import BookSerializer, BookLoanSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import OuterRef, Subquery
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BookSerializer

class LoansViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BookLoanSerializer
    def get_queryset(self):
        user = self.request.user

        latest_loan_subquery = BookLoan.objects.filter(
            user=user,
            book=OuterRef('book')
        ).order_by('-id')

        latest_loans = BookLoan.objects.filter(
            id__in=Subquery(latest_loan_subquery.values('id')[:1])
        ).select_related('book')

        return latest_loans

    @action(detail=False, methods=['post'], url_path='create-loan')
    def create_new_loan(self, request):
        user = request.user
        book_id = request.data.get('book_id')

        if not book_id:
            return Response({'error': 'book_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        book = get_object_or_404(Book, id=book_id)

        if book.stock < 1:
            return Response({'error': 'This book is currently not available.'}, status=status.HTTP_400_BAD_REQUEST)

        existing_loan = BookLoan.objects.filter(user=user, book=book, return_date__isnull=True).first()
        if existing_loan:
            return Response({'error': "You already borrowed this book and haven't returned it."}, status=status.HTTP_400_BAD_REQUEST)

        loan = BookLoan.objects.create(
            user=user,
            book=book,
            loan_date=timezone.now().date()
        )

        book.stock -= 1
        book.save()

        serializer = self.get_serializer(loan)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'], url_path='return-loan')
    def return_loan(self, request):
        user = request.user
        book_id = request.data.get('book_id')
        loan = BookLoan.objects.filter(user=user, book_id=book_id, return_date__isnull=True).first()
        
        if not loan:
            return Response({'error': 'You already returned this book or never borrowed it.'}, status=status.HTTP_400_BAD_REQUEST)
            
        loan.return_date = timezone.now().date()
        loan.save()

        book = loan.book
        book.stock += 1
        book.save()

        return Response(status=status.HTTP_200_OK)