import calendar
from datetime import date, timedelta
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class FamilyMember(models.Model):
    class Role(models.TextChoices):
        PARENT = 'parent', 'Parent'
        CHILD = 'child', 'Child'

    name = models.CharField(max_length=100, unique=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.CHILD)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_role_display()})"


class Chore(models.Model):
    class Frequency(models.TextChoices):
        DAILY = 'daily', 'Daily'
        WEEKLY = 'weekly', 'Weekly'
        MONTHLY = 'monthly', 'Monthly'

    class DayOfWeek(models.IntegerChoices):
        MONDAY = 0, 'Monday'
        TUESDAY = 1, 'Tuesday'
        WEDNESDAY = 2, 'Wednesday'
        THURSDAY = 3, 'Thursday'
        FRIDAY = 4, 'Friday'
        SATURDAY = 5, 'Saturday'
        SUNDAY = 6, 'Sunday'

    name = models.CharField(max_length=200)
    frequency = models.CharField(max_length=10, choices=Frequency.choices, default=Frequency.DAILY)
    assigned_to = models.ForeignKey(
        FamilyMember,
        on_delete=models.CASCADE,
        related_name='chores'
    )
    start_date = models.DateField(default=timezone.localdate)

    # Weekly / Monthly schedule options: specific day vs flexible within period
    is_flexible = models.BooleanField(
        default=True,
        help_text="If True, the chore is flexible within its weekly or monthly period."
    )
    specific_day_of_week = models.IntegerField(
        choices=DayOfWeek.choices,
        null=True,
        blank=True,
        help_text="Required for weekly chores if not flexible (0=Monday, 6=Sunday)."
    )
    specific_day_of_month = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        help_text="Day of the month (1-31) for monthly chores if not flexible."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_frequency_display()} - {self.assigned_to.name})"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.frequency == self.Frequency.WEEKLY and not self.is_flexible:
            if self.specific_day_of_week is None:
                raise ValidationError({'specific_day_of_week': 'Please select a specific day of the week for weekly recurring chores.'})
        if self.frequency == self.Frequency.MONTHLY and not self.is_flexible:
            if self.specific_day_of_month is None:
                raise ValidationError({'specific_day_of_month': 'Please select a day of the month (1-31) for monthly recurring chores.'})

    def generate_occurrences(self, until_date=None):
        """
        Generate occurrences from start_date up to until_date (default: today + 7 days).
        """
        if until_date is None:
            until_date = timezone.localdate() + timedelta(days=7)

        current = self.start_date
        today = timezone.localdate()

        if self.frequency == self.Frequency.DAILY:
            while current <= until_date:
                self._get_or_create_occurrence(current, today)
                current += timedelta(days=1)

        elif self.frequency == self.Frequency.WEEKLY:
            # Step week by week
            start_of_week = current - timedelta(days=current.weekday())
            while start_of_week <= until_date:
                if self.is_flexible:
                    # Due on the last day of the week (Sunday)
                    due_date = start_of_week + timedelta(days=6)
                else:
                    due_date = start_of_week + timedelta(days=self.specific_day_of_week)

                if due_date >= self.start_date and due_date <= until_date:
                    self._get_or_create_occurrence(due_date, today)
                start_of_week += timedelta(weeks=1)

        elif self.frequency == self.Frequency.MONTHLY:
            # Step month by month
            year = current.year
            month = current.month
            while date(year, month, 1) <= until_date:
                days_in_month = calendar.monthrange(year, month)[1]
                if self.is_flexible:
                    due_date = date(year, month, days_in_month)
                else:
                    target_day = min(self.specific_day_of_month or 1, days_in_month)
                    due_date = date(year, month, target_day)

                if due_date >= self.start_date and due_date <= until_date:
                    self._get_or_create_occurrence(due_date, today)

                if month == 12:
                    year += 1
                    month = 1
                else:
                    month += 1

    def _get_or_create_occurrence(self, due_date, today):
        initial_status = ChoreOccurrence.Status.OVERDUE if due_date < today else ChoreOccurrence.Status.TO_DO
        occurrence, created = ChoreOccurrence.objects.get_or_create(
            chore=self,
            due_date=due_date,
            defaults={'status': initial_status}
        )
        return occurrence


class ChoreOccurrence(models.Model):
    class Status(models.TextChoices):
        TO_DO = 'to_do', 'To do'
        PENDING_VALIDATION = 'pending_validation', 'Pending validation'
        OVERDUE = 'overdue', 'Overdue'
        VALIDATED = 'validated', 'Validated'

    chore = models.ForeignKey(
        Chore,
        on_delete=models.CASCADE,
        related_name='occurrences'
    )
    due_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TO_DO
    )
    was_overdue = models.BooleanField(
        default=False,
        help_text="Tracks whether the chore was completed after its due date."
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    completed_by = models.ForeignKey(
        FamilyMember,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='completed_occurrences'
    )
    validated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date', 'chore__name']
        constraints = [
            models.UniqueConstraint(fields=['chore', 'due_date'], name='unique_chore_occurrence_per_date')
        ]

    def __str__(self):
        return f"{self.chore.name} - {self.due_date} ({self.get_status_display()})"

    def refresh_overdue_status(self):
        """Update status to Overdue if due_date has passed and status is To do."""
        today = timezone.localdate()
        if self.status == self.Status.TO_DO and self.due_date < today:
            self.status = self.Status.OVERDUE
            self.save(update_fields=['status', 'updated_at'])

    def mark_completed(self, completed_by=None):
        """Mark as completed by family member; becomes pending validation."""
        today = timezone.localdate()
        if self.status == self.Status.OVERDUE or today > self.due_date:
            self.was_overdue = True

        self.status = self.Status.PENDING_VALIDATION
        self.completed_at = timezone.now()
        if completed_by:
            self.completed_by = completed_by
        self.save()

    def validate(self):
        """Admin validates the completed chore."""
        self.status = self.Status.VALIDATED
        self.validated_at = timezone.now()
        self.save()
