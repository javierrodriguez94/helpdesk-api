from django.contrib import admin
from .models import Ticket, Comment, AuditLog


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'subject', 'status', 'priority', 'created_by', 'assigned_to', 'created_at']
    list_filter = ['status', 'priority']
    search_fields = ['subject', 'description']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'ticket', 'author', 'created_at']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'ticket', 'changed_by', 'field', 'old_value', 'new_value', 'created_at']
    list_filter = ['field']
