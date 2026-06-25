from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Ticket, Comment, AuditLog

User = get_user_model()


class AuditLogSerializer(serializers.ModelSerializer):
    changed_by = serializers.StringRelatedField()

    class Meta:
        model = AuditLog
        fields = ['id', 'changed_by', 'field', 'old_value', 'new_value', 'created_at']


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()

    class Meta:
        model = Comment
        fields = ['id', 'author', 'body', 'created_at']
        read_only_fields = ['author', 'created_at']


class TicketSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField()
    assigned_to = serializers.StringRelatedField()

    class Meta:
        model = Ticket
        fields = [
            'id', 'subject', 'description', 'status', 'priority',
            'created_by', 'assigned_to', 'created_at', 'updated_at',
        ]
        read_only_fields = ['status', 'created_by', 'assigned_to', 'created_at', 'updated_at']


class TicketStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Ticket.Status)

    def validate_status(self, new_status):
        ticket = self.context['ticket']
        if not ticket.can_transition_to(new_status):
            raise serializers.ValidationError(
                f"Cannot transition from '{ticket.status}' to '{new_status}'."
            )
        return new_status


class AssignTicketSerializer(serializers.Serializer):
    assigned_to = serializers.IntegerField()

    def validate_assigned_to(self, value):
        try:
            user = User.objects.get(pk=value)
        except User.DoesNotExist:
            raise serializers.ValidationError('User not found.')
        if not user.is_agent:
            raise serializers.ValidationError('Tickets can only be assigned to agents.')
        return user
