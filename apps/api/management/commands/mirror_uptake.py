from optparse import make_option

from django.core.management.base import NoArgsCommand
from texttable import Texttable

from api.views import XMLRenderer
from mirror.models import Location, OS, Product


class Command(NoArgsCommand):
    help = 'Display Mirror Uptake'
    __doc__ = help
    option_list = NoArgsCommand.option_list + (
        make_option('-p', '--product', action='store', dest='product',
                    default='', help='(Part of) the product name to display '\
                                     'the uptake for'),
        make_option('-o', '--os', action='store', dest='os',
                    default='', help='(Part of) the platform name to display '\
                                     'the uptake for'),
        make_option('-f', '--format', action='store', dest='format',
                    type='choice', choices=['text', 'xml'], default='text',
                    help='output format: text or xml'),
    )

    def handle_noargs(self, **options):
        if options['product']:
            products = Product.objects.filter(name__icontains=options['product'])
            pids = [ p.id for p in products ]
        else:
            pids = None

        if options['os']:
            oses = OS.objects.filter(name__icontains=options['os'])
            osids = [ o.id for o in oses ]
        else:
            osids = None
        uptake = Location.get_mirror_uptake(products=pids, oses=osids)

        render_options = {'text': self._display_text,
                          'xml': self._display_xml}
        render_options[options['format']](uptake)

    def _display_text(self, uptake):
        """display uptake as text"""
        table = Texttable()
        table.set_cols_align(['l', 'l', 'r', 'r'])
        table.add_row(['Product', 'OS', 'Available', 'Total'])
        for row in uptake:
            table.add_row([row['location__product__name'],
                           row['location__os__name'],
                           row['available'],
                           row['total']
                          ])
        print table.draw()

    def _display_xml(self, uptake):
        """display uptake as XML"""
        xml = XMLRenderer().render_uptake(uptake)
        print xml.toprettyxml(indent=' '*4, encoding='utf-8')

