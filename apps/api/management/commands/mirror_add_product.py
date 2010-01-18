from django.core.management.base import LabelCommand, CommandError

from mirror.models import Product


class Command(LabelCommand):
    help = 'Add one or more products to the database.'
    __doc__ = help
    args = '<productname productname ...>'
    label = 'product name (e.g., "Firefox-3.0.5")'

    def handle_label(self, prodname, **options):
        if not prodname:
            return "Cannot add an empty product name."
        prod = Product(name=prodname)
        try:
            prod.save()
        except Exception, e:
            raise CommandError(e)
        return "Successfully added product %s with id %d." % (prodname, prod.id)

