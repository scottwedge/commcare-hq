from django.test import TestCase
from corehq.apps.accounting import generator
from corehq.apps.accounting.models import SoftwarePlanEdition
from corehq.apps.accounting.tests.utils import DomainSubscriptionMixin
from corehq.apps.accounting.tests.base_tests import BaseAccountingTest
from corehq.apps.sms.api import incoming, send_sms_to_verified_number
from corehq.apps.sms.messages import MSG_OPTED_IN, MSG_OPTED_OUT, get_message
from corehq.apps.sms.mixin import VerifiedNumber
from corehq.apps.sms.models import PhoneBlacklist, SMS
from corehq.apps.sms.tests.util import setup_default_sms_test_backend, delete_domain_phone_numbers
from corehq.apps.domain.models import Domain
from corehq.form_processor.tests.utils import run_with_all_backends, FormProcessorTestUtils


class OptTestCase(BaseAccountingTest, DomainSubscriptionMixin):

    def setUp(self):
        super(OptTestCase, self).setUp()
        self.domain = 'opt-test'

        self.domain_obj = Domain(name=self.domain)
        self.domain_obj.sms_case_registration_enabled = True
        self.domain_obj.save()

        self.setup_subscription(self.domain_obj.name, SoftwarePlanEdition.ADVANCED)
        self.backend, self.backend_mapping = setup_default_sms_test_backend()

    def get_last_sms(self, phone_number):
        return SMS.objects.filter(domain=self.domain, phone_number=phone_number).order_by('-date')[0]

    @run_with_all_backends
    def test_opt_out_and_opt_in(self):
        self.assertEqual(PhoneBlacklist.objects.count(), 0)

        incoming('99912345678', 'join opt-test', 'GVI')
        v = VerifiedNumber.by_phone('99912345678')
        self.assertIsNotNone(v)

        incoming('99912345678', 'stop', 'GVI')
        self.assertEqual(PhoneBlacklist.objects.count(), 1)
        phone_number = PhoneBlacklist.objects.get(phone_number='99912345678')
        self.assertFalse(phone_number.send_sms)
        self.assertEqual(phone_number.domain, self.domain)
        self.assertIsNotNone(phone_number.last_sms_opt_out_timestamp)
        self.assertIsNone(phone_number.last_sms_opt_in_timestamp)

        sms = self.get_last_sms('+99912345678')
        self.assertEqual(sms.direction, 'O')
        self.assertEqual(sms.text, get_message(MSG_OPTED_OUT, context=('START',)))

        incoming('99912345678', 'start', 'GVI')
        self.assertEqual(PhoneBlacklist.objects.count(), 1)
        phone_number = PhoneBlacklist.objects.get(phone_number='99912345678')
        self.assertTrue(phone_number.send_sms)
        self.assertEqual(phone_number.domain, self.domain)
        self.assertIsNotNone(phone_number.last_sms_opt_out_timestamp)
        self.assertIsNotNone(phone_number.last_sms_opt_in_timestamp)

        sms = self.get_last_sms('+99912345678')
        self.assertEqual(sms.direction, 'O')
        self.assertEqual(sms.text, get_message(MSG_OPTED_IN, context=('STOP',)))

    @run_with_all_backends
    def test_sending_to_opted_out_number(self):
        self.assertEqual(PhoneBlacklist.objects.count(), 0)

        incoming('99912345678', 'join opt-test', 'GVI')
        v = VerifiedNumber.by_phone('99912345678')
        self.assertIsNotNone(v)

        send_sms_to_verified_number(v, 'hello')
        sms = self.get_last_sms('+99912345678')
        self.assertEqual(sms.direction, 'O')
        self.assertEqual(sms.text, 'hello')

        incoming('99912345678', 'stop', 'GVI')
        self.assertEqual(PhoneBlacklist.objects.count(), 1)
        phone_number = PhoneBlacklist.objects.get(phone_number='99912345678')
        self.assertFalse(phone_number.send_sms)

        send_sms_to_verified_number(v, 'hello')
        sms = self.get_last_sms('+99912345678')
        self.assertEqual(sms.direction, 'O')
        self.assertEqual(sms.text, 'hello')
        self.assertTrue(sms.error)
        self.assertEqual(sms.system_error_message, SMS.ERROR_PHONE_NUMBER_OPTED_OUT)

        incoming('99912345678', 'start', 'GVI')
        self.assertEqual(PhoneBlacklist.objects.count(), 1)
        phone_number = PhoneBlacklist.objects.get(phone_number='99912345678')
        self.assertTrue(phone_number.send_sms)

        send_sms_to_verified_number(v, 'hello')
        sms = self.get_last_sms('+99912345678')
        self.assertEqual(sms.direction, 'O')
        self.assertEqual(sms.text, 'hello')
        self.assertFalse(sms.error)
        self.assertIsNone(sms.system_error_message)

    def tearDown(self):
        FormProcessorTestUtils.delete_all_cases(self.domain)
        PhoneBlacklist.objects.all().delete()
        delete_domain_phone_numbers(self.domain)
        self.backend_mapping.delete()
        self.backend.delete()
        self.domain_obj.delete()
        self.teardown_subscription()
