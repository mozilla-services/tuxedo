from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from lib import docstring_trim
from lib.product_details import LocaleDetails
from mirror.models import Location, OS, Product


class Command(BaseCommand):
    help = docstring_trim("""
        Add a new location to the database.
        All arguments are mandatory. Add the --locale option to define a locale
        for this location.
        """)
    __doc__ = help
    args = '<product_name> <os_name> <location_path>'
    option_list = BaseCommand.option_list + (
        make_option('-l', '--locale', action='store', dest='locale',
            default=None, help='Locale code for this location. Default: none. '\
                               'Currently known locales: %s.' % \
                               ', '.join(LocaleDetails().get_locale_codes())
        ),
    )

    def handle(self, prod_name=None, os_name=None, loc_path=None, **options):
        pass
        if not (prod_name and os_name and loc_path):
            raise CommandError("Cannot all arguments are mandatory.")

        try:
            product = Product.objects.get(name=prod_name)
        except Product.DoesNotExist:
            raise CommandError("Unknown Product %s." % prod_name)
        try:
            os = OS.objects.get(name=os_name)
        except OS.DoesNotExist:
            oses = ", ".join([os.name for os in OS.objects.order_by('name')])
            raise CommandError("Unknown OS %s.\nKnown OSes: %s" % (os_name, oses))
        locale_codes = LocaleDetails().get_locale_codes()
        locale = options['locale']
        if not locale:
            locale=None
        elif locale and locale not in locale_codes:
            raise CommandError("Unknown locale code: %s.\nKnown locale "\
                               "codes: %s." % (locale, ", ".join(locale_codes)))

        new_location = Location(product=product, os=os, path=loc_path, lang=locale)
        try:
            new_location.save()
        except Exception, e:
            raise CommandError(e)

        return "Successfully added location %s for locale %s with id %d." % \
            ((prod_name, os_name, loc_path), locale, new_location.id)

