from library.models import Book, BookLoan
from rest_framework import viewsets, permissions
from .serializers import BookSerializer, BookLoanSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import OuterRef, Subquery
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone


# ViewSet to manage CRUD operations for books
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()                                # All books in the database
    permission_classes = [permissions.IsAuthenticated]           # Requires user to be logged in
    serializer_class = BookSerializer                            # Serializer to convert Book objects


# ViewSet to manage book loans (borrowing and returning books)
class LoansViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]           # Requires authentication
    serializer_class = BookLoanSerializer                        # Serializer to convert BookLoan objects

    def get_queryset(self):
        """
        Return the most recent loan for each book the current user has interacted with.
        """
        user = self.request.user

        # Subquery: Get latest loan per book for the user
        latest_loan_subquery = BookLoan.objects.filter(
            user=user,
            book=OuterRef('book')
        ).order_by('-id')

        # Final queryset using Subquery to fetch the latest loans
        latest_loans = BookLoan.objects.filter(
            id__in=Subquery(latest_loan_subquery.values('id')[:1])
        ).select_related('book')

        return latest_loans

    @action(detail=False, methods=['post'], url_path='create-loan')
    def create_new_loan(self, request):
        """
        Custom action to create a new loan for a book.
        Ensures:
        - Book ID is provided
        - Book is in stock
        - User doesn't already have an active loan for that book
        """
        user = request.user
        book_id = request.data.get('book_id')

        if not book_id:
            return Response({'error': 'book_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Find the book or return 404 if not found
        book = get_object_or_404(Book, id=book_id)

        # Check if book is available
        if book.stock < 1:
            return Response({'error': 'This book is currently not available.'}, status=status.HTTP_400_BAD_REQUEST)

        # Prevent borrowing the same book more than once without returning
        existing_loan = BookLoan.objects.filter(user=user, book=book, return_date__isnull=True).first()
        if existing_loan:
            return Response({'error': "You already borrowed this book and haven't returned it."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the loan
        loan = BookLoan.objects.create(
            user=user,
            book=book,
            loan_date=timezone.now().date()
        )

        # Decrease book stock
        book.stock -= 1
        book.save()

        serializer = self.get_serializer(loan)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='return-loan')
    def return_loan(self, request):
        """
        Custom action to return a borrowed book.
        - Finds the current active loan for the user and book
        - Marks it as returned
        - Increments the book's stock
        """
        user = request.user
        book_id = request.data.get('book_id')

        # Look for an active loan (not yet returned)
        loan = BookLoan.objects.filter(user=user, book_id=book_id, return_date__isnull=True).first()
        
        if not loan:
            return Response({'error': 'You already returned this book or never borrowed it.'}, status=status.HTTP_400_BAD_REQUEST)

        # Mark loan as returned
        loan.return_date = timezone.now().date()
        loan.save()

        # Increase book stock
        book = loan.book
        book.stock += 1
        book.save()

        return Response(status=status.HTTP_200_OK)