from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import ChoreForm
from .models import Chore, ChoreOccurrence, FamilyMember


def dashboard(request):
    today = timezone.localdate()

    # Generate occurrences for all active chores up to 7 days ahead
    for chore in Chore.objects.all():
        chore.generate_occurrences()

    # Automatically refresh overdue status for past-due 'to_do' occurrences
    ChoreOccurrence.objects.filter(
        status=ChoreOccurrence.Status.TO_DO,
        due_date__lt=today
    ).update(status=ChoreOccurrence.Status.OVERDUE)

    todo_list = ChoreOccurrence.objects.filter(
        status=ChoreOccurrence.Status.TO_DO
    ).select_related('chore', 'chore__assigned_to').order_date_asc() if hasattr(ChoreOccurrence.objects, 'order_date_asc') else ChoreOccurrence.objects.filter(
        status=ChoreOccurrence.Status.TO_DO
    ).select_related('chore', 'chore__assigned_to').order_by('due_date')

    overdue_list = ChoreOccurrence.objects.filter(
        status=ChoreOccurrence.Status.OVERDUE
    ).select_related('chore', 'chore__assigned_to').order_by('due_date')

    pending_list = ChoreOccurrence.objects.filter(
        status=ChoreOccurrence.Status.PENDING_VALIDATION
    ).select_related('chore', 'chore__assigned_to', 'completed_by').order_by('-completed_at')

    validated_list = ChoreOccurrence.objects.filter(
        status=ChoreOccurrence.Status.VALIDATED
    ).select_related('chore', 'chore__assigned_to', 'completed_by').order_by('-validated_at')[:20]

    family_members = FamilyMember.objects.all()

    context = {
        'today': today,
        'todo_list': todo_list,
        'overdue_list': overdue_list,
        'pending_list': pending_list,
        'validated_list': validated_list,
        'family_members': family_members,
    }
    return render(request, 'chores/dashboard.html', context)


def mark_completed(request, pk):
    if request.method == 'POST':
        occurrence = get_object_or_404(ChoreOccurrence, pk=pk)
        member_id = request.POST.get('completed_by')
        completed_by = None
        if member_id:
            completed_by = FamilyMember.objects.filter(pk=member_id).first()
        elif occurrence.chore.assigned_to:
            completed_by = occurrence.chore.assigned_to

        occurrence.mark_completed(completed_by=completed_by)
        messages.success(request, f'Chore "{occurrence.chore.name}" marked as completed and is pending validation.')
    return redirect('chores:dashboard')


def validate_chore(request, pk):
    if request.method == 'POST':
        occurrence = get_object_or_404(ChoreOccurrence, pk=pk)
        occurrence.validate()
        messages.success(request, f'Chore "{occurrence.chore.name}" has been validated!')
    return redirect('chores:dashboard')


class ChoreListView(ListView):
    model = Chore
    template_name = 'chores/chore_list.html'
    context_object_name = 'chores'

    def get_queryset(self):
        return Chore.objects.select_related('assigned_to').order_by('name')


class ChoreCreateView(CreateView):
    model = Chore
    form_class = ChoreForm
    template_name = 'chores/chore_form.html'
    success_url = reverse_lazy('chores:chore_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.generate_occurrences()
        messages.success(self.request, f'Chore "{self.object.name}" created successfully!')
        return response


class ChoreUpdateView(UpdateView):
    model = Chore
    form_class = ChoreForm
    template_name = 'chores/chore_form.html'
    success_url = reverse_lazy('chores:chore_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.generate_occurrences()
        messages.success(self.request, f'Chore "{self.object.name}" updated successfully!')
        return response


class ChoreDeleteView(DeleteView):
    model = Chore
    template_name = 'chores/chore_confirm_delete.html'
    success_url = reverse_lazy('chores:chore_list')

    def delete(self, request, *args, **kwargs):
        chore = self.get_object()
        messages.success(request, f'Chore "{chore.name}" deleted successfully.')
        return super().delete(request, *args, **kwargs)
