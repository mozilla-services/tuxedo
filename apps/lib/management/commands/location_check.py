import httplib
from optparse import make_option
import sys
from urlparse import urlparse

from django.conf import settings
from django.core.management.base import NoArgsCommand, CommandError

from mirror.models import Location, OS, Product


class Command(NoArgsCommand):
    help = ('Find and delete locations that are not present on a '
            'reference mirror')
    __doc__ = help
    option_list = NoArgsCommand.option_list + (
        make_option('-p', '--product', action='store', dest='product',
                    default='', help='(Part of) the product name to limit '
                                     'the check to'),
        make_option('-o', '--os', action='store', dest='os',
                    default='', help='(Part of) the platform name to limit '
                                     'the check to'),
        make_option('-m', '--mirror', action='store', dest='mirror',
                    default=settings.REFERENCE_BASEURL,
                    help='mirror base URL to check locations against'),
        make_option('-f', '--full-run', action='store_true', dest='full',
                    default=False,
                    help='Run all locations. If false (default), will run the '
                         'locations with product__checknow=True only'),
    )

    def handle_noargs(self, **options):
        if not options['mirror']:
            raise CommandError("No base URL was specified.")
        else:
            baseurl = options['mirror']

        filter_for = {}
        if options['product']:
            products = Product.objects.filter(
                name__icontains=options['product']
            )
            filter_for['product__in'] = [p.id for p in products]
        if options['os']:
            oses = OS.objects.filter(name__icontains=options['os'])
            filter_for['os__in'] = [o.id for o in oses]
        if not options['full']:
            filter_for['product__checknow'] = True
        locations = Location.objects.filter(**filter_for)

        print ("Checking %d locations against %s ..."
               % (len(locations), baseurl))
        conn = httplib.HTTPConnection(urlparse(baseurl).netloc)

        linecount = 0
        failed = []

        for location in locations:
            url = ''.join((baseurl, location.path))
            parsed = urlparse(url)
            conn.request('HEAD', parsed.path)
            res = conn.getresponse()

            sys.stdout.write('.')
            linecount += 1
            if linecount >= 80:
                linecount = 0
                sys.stdout.write("\n")

            if 400 <= res.status < 500:
                linecount = 0
                print
                print "Unavailable (%d): %s" % (res.status, location.path)
                failed.append(location)

            sys.stdout.flush()

        print
        print
        print ("Found %d unavailable location(s) on reference mirror."
               % len(failed))
        if failed:
            print
            print
            confirm = ''
            while confirm not in ('yes', 'no'):
                confirm = raw_input('Do you want to delete these locations? '
                                    '(Enter yes or no): ')
            if confirm == 'yes':
                for location in failed:
                    print "Deleting %s..." % location.path
                    location.delete()
