from datetime import timedelta
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Chore, ChoreOccurrence, FamilyMember


class ChoresAppTests(TestCase):
    def setUp(self):
        self.parent = FamilyMember.objects.create(name='TestParent', role=FamilyMember.Role.PARENT)
        self.child = FamilyMember.objects.create(name='TestChild', role=FamilyMember.Role.CHILD)
        self.today = timezone.localdate()

    def test_family_member_creation(self):
        self.assertEqual(self.parent.role, 'parent')
        self.assertEqual(self.child.role, 'child')
        self.assertIn('TestParent', str(self.parent))

    def test_daily_chore_occurrence_generation(self):
        start = self.today - timedelta(days=2)
        chore = Chore.objects.create(
            name='Daily Test Chore',
            frequency=Chore.Frequency.DAILY,
            assigned_to=self.child,
            start_date=start
        )
        chore.generate_occurrences(until_date=self.today + timedelta(days=1))
        # start, start+1, start+2(today), start+3(tomorrow) -> 4 occurrences
        self.assertEqual(chore.occurrences.count(), 4)

    def test_overdue_detection_and_completion_flag(self):
        past_due = self.today - timedelta(days=3)
        chore = Chore.objects.create(
            name='Clean Room',
            frequency=Chore.Frequency.DAILY,
            assigned_to=self.child,
            start_date=past_due
        )
        chore.generate_occurrences(until_date=past_due)
        occ = chore.occurrences.get(due_date=past_due)

        # Occurrence was generated with past due date -> should be overdue
        self.assertEqual(occ.status, ChoreOccurrence.Status.OVERDUE)

        # Mark completed by child
        occ.mark_completed(completed_by=self.child)
        occ.refresh_from_db()

        self.assertEqual(occ.status, ChoreOccurrence.Status.PENDING_VALIDATION)
        self.assertTrue(occ.was_overdue, "Completed chore after due date must identify as was_overdue")
        self.assertEqual(occ.completed_by, self.child)

        # Administrator validates
        occ.validate()
        occ.refresh_from_db()

        self.assertEqual(occ.status, ChoreOccurrence.Status.VALIDATED)
        self.assertTrue(occ.was_overdue, "Validated chore must retain was_overdue flag")
        self.assertIsNotNone(occ.validated_at)

    def test_on_time_completion_not_overdue(self):
        chore = Chore.objects.create(
            name='Do Homework',
            frequency=Chore.Frequency.DAILY,
            assigned_to=self.child,
            start_date=self.today
        )
        chore.generate_occurrences(until_date=self.today)
        occ = chore.occurrences.get(due_date=self.today)

        self.assertEqual(occ.status, ChoreOccurrence.Status.TO_DO)
        occ.mark_completed(completed_by=self.child)
        occ.refresh_from_db()

        self.assertEqual(occ.status, ChoreOccurrence.Status.PENDING_VALIDATION)
        self.assertFalse(occ.was_overdue)

    def test_dashboard_view(self):
        chore = Chore.objects.create(
            name='Take out trash',
            frequency=Chore.Frequency.DAILY,
            assigned_to=self.child,
            start_date=self.today
        )
        response = self.client.get(reverse('chores:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Take out trash')
        self.assertContains(response, 'To Do')
        self.assertContains(response, 'Overdue')
        self.assertContains(response, 'Pending Validation')
        self.assertContains(response, 'Validated')

    def test_chore_crud_views(self):
        # Create chore
        create_url = reverse('chores:chore_create')
        post_data = {
            'name': 'Feed the cat',
            'frequency': Chore.Frequency.DAILY,
            'assigned_to': self.child.pk,
            'start_date': self.today.strftime('%Y-%m-%d'),
            'is_flexible': True,
        }
        res = self.client.post(create_url, post_data)
        self.assertEqual(res.status_code, 302)
        chore = Chore.objects.get(name='Feed the cat')
        self.assertIsNotNone(chore)
        self.assertGreater(chore.occurrences.count(), 0)

        # Update chore
        edit_url = reverse('chores:chore_edit', kwargs={'pk': chore.pk})
        res = self.client.post(edit_url, {
            'name': 'Feed the hungry cat',
            'frequency': Chore.Frequency.DAILY,
            'assigned_to': self.parent.pk,
            'start_date': self.today.strftime('%Y-%m-%d'),
            'is_flexible': True,
        })
        self.assertEqual(res.status_code, 302)
        chore.refresh_from_db()
        self.assertEqual(chore.name, 'Feed the hungry cat')
        self.assertEqual(chore.assigned_to, self.parent)

        # Delete chore
        delete_url = reverse('chores:chore_delete', kwargs={'pk': chore.pk})
        res = self.client.post(delete_url)
        self.assertEqual(res.status_code, 302)
        self.assertFalse(Chore.objects.filter(pk=chore.pk).exists())

    def test_complete_and_validate_workflow_post(self):
        chore = Chore.objects.create(
            name='Water plants',
            frequency=Chore.Frequency.DAILY,
            assigned_to=self.child,
            start_date=self.today
        )
        chore.generate_occurrences(until_date=self.today)
        occ = chore.occurrences.get(due_date=self.today)

        # Complete via POST
        complete_url = reverse('chores:mark_completed', kwargs={'pk': occ.pk})
        res = self.client.post(complete_url, {'completed_by': self.child.pk})
        self.assertEqual(res.status_code, 302)
        occ.refresh_from_db()
        self.assertEqual(occ.status, ChoreOccurrence.Status.PENDING_VALIDATION)

        # Validate via POST
        validate_url = reverse('chores:validate_chore', kwargs={'pk': occ.pk})
        res = self.client.post(validate_url)
        self.assertEqual(res.status_code, 302)
        occ.refresh_from_db()
        self.assertEqual(occ.status, ChoreOccurrence.Status.VALIDATED)
