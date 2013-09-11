ORDER_VAR = 'sort'
ORDER_TYPE_VAR = 'dir'


class SortHeaders:
    """
    Handles generation of an argument for the Django ORM's
    ``order_by`` method and generation of table headers which reflect
    the currently selected sort, based on defined table headers with
    matching sort criteria.

    Based in part on the Django Admin application's ``ChangeList``
    functionality.
    """
    def __init__(self, request, headers, default_order_field=None,
                 default_order_type='asc', additional_params=None):
        """
        request
            The request currently being processed - the current sort
            order field and type are determined based on GET
            parameters.

        headers
            A list of two-tuples of header text and matching ordering
            criteria for use with the Django ORM's ``order_by``
            method. A criterion of ``None`` indicates that a header
            is not sortable.

        default_order_field
            The index of the header definition to be used for default
            ordering and when an invalid or non-sortable header is
            specified in GET parameters. If not specified, the index
            of the first sortable header will be used.

        default_order_type
            The default type of ordering used - must be one of
            ``'asc`` or ``'desc'``.

        additional_params:
            Query parameters which should always appear in sort links,
            specified as a dictionary mapping parameter names to
            values. For example, this might contain the current page
            number if you're sorting a paginated list of items.
        """
        if default_order_field is None:
            for i, (header, query_lookup) in enumerate(headers):
                if query_lookup is not None:
                    default_order_field = i
                    break
        if default_order_field is None:
            raise AttributeError(
                'No default_order_field was specified and none of the header '
                'definitions given were sortable.')
        if default_order_type not in ('asc', 'desc'):
            raise AttributeError(
                'If given, default_order_type must be one of \'asc\' or '
                '\'desc\'.')
        if additional_params is None:
            additional_params = {}

        self.request = request
        self.header_defs = headers
        self.additional_params = additional_params
        self.order_field = default_order_field
        self.order_type = default_order_type

        # Determine order field and order type for the current request
        params = dict(request.GET.items())
        if ORDER_VAR in params:
            try:
                new_order_field = int(params[ORDER_VAR])
                if headers[new_order_field][1] is not None:
                    self.order_field = new_order_field
            except (IndexError, ValueError):
                pass  # Use the default
        if (ORDER_TYPE_VAR in params and
                params[ORDER_TYPE_VAR] in ('asc', 'desc')):
            self.order_type = params[ORDER_TYPE_VAR]

    def headers(self):
        """
        Generates dicts containing header and sort link details for
        all defined headers.
        """
        for i, (header, order_criterion) in enumerate(self.header_defs):
            th_classes = []
            new_order_type = 'asc'
            if i == self.order_field:
                th_classes.append('sorted %sending' % self.order_type)
                new_order_type = {'asc': 'desc',
                                  'desc': 'asc'}[self.order_type]
            is_sortable = order_criterion is not None
            if not is_sortable:
                th_classes.append('sorttable_nosort')
            yield {
                'text': header,
                'sortable': is_sortable,
                'url': self.get_query_string(
                    {ORDER_VAR: i, ORDER_TYPE_VAR: new_order_type}
                ),
                'class_attr': (th_classes and ' class="%s"'
                               % ' '.join(th_classes) or ''),
            }

    def get_query_string(self, params):
        """
        Creates a query string from the given pairwise list of
        parameters, including any additonal parameters which should
        always be present.
        """
        all_params = self.request.GET.copy()
        all_params.update(self.additional_params)  # does not overwrite
        for param, value in params.items():
            all_params[param] = value
        return '?%s' % all_params.urlencode()

    def get_order_by(self):
        """
        Creates an ordering criterion based on the current order
        field and order type, for use with the Django ORM's
        ``order_by`` method.
        """
        return '%s%s' % (
            self.order_type == 'desc' and '-' or '',
            self.header_defs[self.order_field][1],
        )
