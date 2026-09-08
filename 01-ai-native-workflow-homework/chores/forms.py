from django import forms
from .models import Chore, FamilyMember, ChoreOccurrence


class ChoreForm(forms.ModelForm):
    class Meta:
        model = Chore
        fields = [
            'name',
            'frequency',
            'assigned_to',
            'start_date',
            'is_flexible',
            'specific_day_of_week',
            'specific_day_of_month',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Wash the dishes'}),
            'frequency': forms.Select(attrs={'class': 'form-select', 'id': 'id_frequency'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_flexible': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_is_flexible'}),
            'specific_day_of_week': forms.Select(attrs={'class': 'form-select', 'id': 'id_specific_day_of_week'}),
            'specific_day_of_month': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 31, 'id': 'id_specific_day_of_month'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        frequency = cleaned_data.get('frequency')
        is_flexible = cleaned_data.get('is_flexible')
        specific_day_of_week = cleaned_data.get('specific_day_of_week')
        specific_day_of_month = cleaned_data.get('specific_day_of_month')

        if frequency == Chore.Frequency.WEEKLY and not is_flexible:
            if specific_day_of_week is None:
                self.add_error('specific_day_of_week', 'Please select a specific day of the week.')

        if frequency == Chore.Frequency.MONTHLY and not is_flexible:
            if specific_day_of_month is None:
                self.add_error('specific_day_of_month', 'Please enter a day of the month (1-31).')

        return cleaned_data


class CompleteChoreForm(forms.Form):
    completed_by = forms.ModelChoiceField(
        queryset=FamilyMember.objects.all(),
        required=False,
        empty_label="Select who completed it (optional)",
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
