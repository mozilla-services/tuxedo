import csv
import urllib
from zipfile import ZipFile

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from geoip.models import IPBlock, Country

GEOIP_URL = "http://geolite.maxmind.com/download/geoip/database/GeoIPCountryCSV.zip"
GEOIP_FILENAME = "GeoIPCountryWhois.csv"


class Command(BaseCommand):
    args = '<file_path>'
    help = 'Updates geoip_ip_to_country table with content of a CSV file. \
        Should be downloaded from http://www.maxmind.com/app/geolitecountry .'
    output_transaction = True

    @transaction.commit_on_success
    def handle(self, *args, **options):
        if len(args) is 0:
            print "Downloading %s" % GEOIP_URL
            filename, headers = urllib.urlretrieve(GEOIP_URL)
            print "%s downloaded" % GEOIP_URL
            geozip = ZipFile(filename)
            f = geozip.open(GEOIP_FILENAME)
        elif len(args) is 1:
            f = open(args[0])
        else:
            raise CommandError('You need zero or one file_path argument')

        print "Deleting previous records"
        IPBlock.objects.all().delete()
        print "Previous records deleted"
        print "Inserting new records"
        for row in csv.reader(f):
            ip_block = IPBlock(ip_start=row[2],
                               ip_end=row[3],
                               country=Country(row[4]))
            ip_block.save()
        print "New records inserted"

        f.close()
        if 'geozip' in locals():
            geozip.close()
