import unittest
from django.core.exceptions import ValidationError
from .models import Lead, LeadState


class LeadModelTests(unittest.TestCase):

    def setUp(self):
        self.new_state = LeadState.objects.get_or_create(pk=LeadState.STATE_NEW, name="New")[0]
        self.in_progress_state = LeadState.objects.get_or_create(pk=LeadState.STATE_IN_PROGRESS, name="In Progress")[0]
        self.postponed_state = LeadState.objects.get_or_create(pk=LeadState.STATE_POSTPONED, name="Postponed")[0]
        self.done_state = LeadState.objects.get_or_create(pk=LeadState.STATE_DONE, name="Done")[0]

    def test_1_to_2_transition(self):
        lead = Lead.objects.create(name="Test Lead", state=self.new_state)
        lead.state = self.in_progress_state
        lead.save(update_fields=['state'])
        self.assertEqual(lead.state.pk, LeadState.STATE_IN_PROGRESS)

    def test_2_to_3_transition(self):
        lead = Lead.objects.create(name="Test Lead", state=self.in_progress_state)
        lead.state = self.postponed_state
        lead.save(update_fields=['state'])
        self.assertEqual(lead.state.pk, LeadState.STATE_POSTPONED)

    def test_2_to_4_transition(self):
        lead = Lead.objects.create(name="Test Lead", state=self.in_progress_state)
        lead.state = self.done_state
        lead.save(update_fields=['state'])
        self.assertEqual(lead.state.pk, LeadState.STATE_DONE)

    def test_3_to_4_transition(self):
        lead = Lead.objects.create(name="Test Lead", state=self.postponed_state)
        lead.state = self.done_state
        lead.save(update_fields=['state'])
        self.assertEqual(lead.state.pk, LeadState.STATE_DONE)

    def test_3_to_2_transition(self):
        lead = Lead.objects.create(name="Test Lead", state=self.postponed_state)
        lead.state = self.in_progress_state
        lead.save(update_fields=['state'])
        self.assertEqual(lead.state.pk, LeadState.STATE_IN_PROGRESS)

    def test_invalid_state_transition(self):
        lead = Lead.objects.create(name="Test Lead", state=self.new_state)
        lead.state = self.done_state
        with self.assertRaises(ValidationError):
            lead.save(update_fields=['state'])

