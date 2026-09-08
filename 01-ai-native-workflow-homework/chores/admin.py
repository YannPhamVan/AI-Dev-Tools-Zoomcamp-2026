from django.contrib import admin
from .models import FamilyMember, Chore, ChoreOccurrence


@admin.register(FamilyMember)
class FamilyMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'created_at')
    list_filter = ('role',)
    search_fields = ('name',)


@admin.register(Chore)
class ChoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'frequency', 'assigned_to', 'is_flexible', 'start_date')
    list_filter = ('frequency', 'is_flexible', 'assigned_to')
    search_fields = ('name',)


@admin.register(ChoreOccurrence)
class ChoreOccurrenceAdmin(admin.ModelAdmin):
    list_display = ('chore', 'due_date', 'status', 'was_overdue', 'completed_by', 'completed_at', 'validated_at')
    list_filter = ('status', 'was_overdue', 'due_date')
    search_fields = ('chore__name', 'completed_by__name')
