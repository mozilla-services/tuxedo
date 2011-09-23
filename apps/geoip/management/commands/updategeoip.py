import csv

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from geoip.models import IPBlock, Country


class Command(BaseCommand):
    args = '<file_path>'
    help = 'Updates geoip_ip_to_country table with content of a CSV file. \
        Should be downloaded from http://www.maxmind.com/app/geolitecountry .'
    output_transaction = True

    @transaction.commit_on_success
    def handle(self, *args, **options):
        if len(args) is not 1:
            raise CommandError('You need one file_path argument')

        IPBlock.objects.all().delete()
        with open(args[0]) as f:
            for row in csv.reader(f):
                ip_block = IPBlock(ip_start=row[2],
                                   ip_end=row[3],
                                   country=Country(row[4]))
                ip_block.save()
