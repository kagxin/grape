from django.core.management.base import BaseCommand, CommandError
from .grape_server import grape_main

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

#    def add_arguments(self, parser):
#        parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        grape_main()
