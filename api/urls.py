from rest_framework import routers
from .api import BookViewSet, LoansViewSet

router = routers.DefaultRouter()

router.register('books', BookViewSet, 'books')
router.register('loans', LoansViewSet, 'loans')

urlpatterns = router.urls