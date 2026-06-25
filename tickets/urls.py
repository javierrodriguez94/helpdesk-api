from rest_framework_nested import routers
from .views import TicketViewSet, CommentViewSet, AuditLogViewSet

router = routers.SimpleRouter()
router.register(r'tickets', TicketViewSet, basename='ticket')

tickets_router = routers.NestedSimpleRouter(router, r'tickets', lookup='ticket')
tickets_router.register(r'comments', CommentViewSet, basename='ticket-comments')
tickets_router.register(r'history', AuditLogViewSet, basename='ticket-history')

urlpatterns = router.urls + tickets_router.urls
