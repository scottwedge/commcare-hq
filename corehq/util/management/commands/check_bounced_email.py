from django.core.management.base import BaseCommand

from corehq.util.models import (
    BouncedEmail,
    PermanentBounceMeta,
    ComplaintBounceMeta,
)


class Command(BaseCommand):
    help = "Check on the bounced status of an email"

    def add_arguments(self, parser):
        parser.add_argument('bounced_email')
        parser.add_argument(
            '--show-details',
            action='store_true',
            default=False,
            help='Show extra details of bounced messages',
        )

    def handle(self, bounced_email, **options):
        is_bounced = BouncedEmail.objects.filter(email=bounced_email).exists()
        show_details = options['show_details']

        if not is_bounced:
            self.stdout.write(f'\n{bounced_email} is NOT bouncing. '
                              f'All clear!\n\n')
            return

        self.stdout.write('\n\n')
        self.stdout.write('*' * 200)
        self.stdout.write(f'! YES, {bounced_email} is marked as bounced\n')
        self.stdout.write('*' * 200)
        self.stdout.write('\n')

        permanent_bounces = PermanentBounceMeta.objects.filter(
            bounced_email__email=bounced_email).all()

        if permanent_bounces:
            self.stdout.write('The following Permanent Bounce '
                              'records were found:')
            self.stdout.write('\nSub-Type\tSNS Timestamp'
                              '\t\t\tCreated on HQ\t\t\tReason')
            self.stdout.write('.' * 200)
            for record in permanent_bounces:
                self.stdout.write(f'{record.sub_type}'
                                  f'\t\t{record.timestamp}'
                                  f'\t{record.created}'
                                  f'\t{record.reason}')
                if show_details:
                    for key, val in record.headers:
                        self.stdout.write(f'\t\t{key}:\t{val}')
                    self.stdout.write(f'\t\tdestination:\t{record.destination}')
            self.stdout.write('\n\n')

        complaints = ComplaintBounceMeta.objects.filter(
            bounced_email__email=bounced_email).all()

        if complaints:
            self.stdout.write('The following Complaint '
                              'records were found:')
            self.stdout.write('\nSNS Timestamp'
                              '\t\t\tCreated on HQ'
                              '\t\t\tFeedback Type'
                              '\t\tSub-Type'
                              '\tDestination')
            self.stdout.write('.' * 200)
            for record in complaints:
                self.stdout.write(f'{record.timestamp}'
                                  f'\t{record.created}'
                                  f'\t{record.feedback_type}'
                                  f'\t{record.sub_type}'
                                  f'\t{record.destination}')
                if show_details:
                    for key, val in record.headers:
                        self.stdout.write(f'\t\t{key}:\t{val}')
            self.stdout.write('\n\n')
