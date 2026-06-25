from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from accounts.permissions import IsAgent
from .models import Ticket, Comment, AuditLog
from .serializers import (
    TicketSerializer,
    TicketStatusSerializer,
    AssignTicketSerializer,
    CommentSerializer,
    AuditLogSerializer,
)


class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_agent:
            return Ticket.objects.all()
        return Ticket.objects.filter(created_by=user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['patch'], permission_classes=[IsAgent])
    def set_status(self, request, pk=None):
        ticket = self.get_object()
        serializer = TicketStatusSerializer(data=request.data, context={'ticket': ticket})
        serializer.is_valid(raise_exception=True)
        old_status = ticket.status
        ticket.status = serializer.validated_data['status']
        ticket.save()
        AuditLog.objects.create(
            ticket=ticket,
            changed_by=request.user,
            field='status',
            old_value=old_status,
            new_value=ticket.status,
        )
        return Response(TicketSerializer(ticket).data)

    @action(detail=True, methods=['patch'], permission_classes=[IsAgent])
    def assign(self, request, pk=None):
        ticket = self.get_object()
        serializer = AssignTicketSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_agent = serializer.validated_data['assigned_to']
        old_agent = str(ticket.assigned_to) if ticket.assigned_to else ''
        ticket.assigned_to = new_agent
        ticket.save()
        AuditLog.objects.create(
            ticket=ticket,
            changed_by=request.user,
            field='assigned_to',
            old_value=old_agent,
            new_value=str(new_agent),
        )
        return Response(TicketSerializer(ticket).data)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']

    def _get_ticket(self):
        user = self.request.user
        qs = Ticket.objects.all() if user.is_agent else Ticket.objects.filter(created_by=user)
        return get_object_or_404(qs, pk=self.kwargs['ticket_pk'])

    def get_queryset(self):
        return Comment.objects.filter(ticket=self._get_ticket())

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, ticket=self._get_ticket())


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def _get_ticket(self):
        user = self.request.user
        qs = Ticket.objects.all() if user.is_agent else Ticket.objects.filter(created_by=user)
        return get_object_or_404(qs, pk=self.kwargs['ticket_pk'])

    def get_queryset(self):
        return AuditLog.objects.filter(ticket=self._get_ticket())
