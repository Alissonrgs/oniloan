# python
from collections import OrderedDict

# django
from django.conf import settings

# third party
from rest_framework.pagination import PageNumberPagination as BasePageNumberPagination
from rest_framework.settings import api_settings
from rest_framework.views import Response


class PageNumberPagination(BasePageNumberPagination):
    """
    Adds extra attributes to response, useful for building
    pagination widgets with range.
    """

    # The default page size.
    # Defaults to `None`, meaning pagination is disabled.
    page_size = api_settings.PAGE_SIZE or settings.DEFAULT_PAGE_SIZE

    # Client can control the page size using this query parameter.
    # Default is 'None'. Set to eg 'page_size' to enable usage.
    page_size_query_param = 'page_size'

    # Set to an integer to limit the maximum page size the client may request.
    # Only relevant if 'page_size_query_param' has also been set.
    max_page_size = getattr(api_settings, 'MAX_PAGE_SIZE', 100)

    def current_page(self):
        return self.request.query_params.get(self.page_query_param, 1)

    def next_page_number(self):
        return self.page.next_page_number() if self.page.has_next() else None

    def prev_page_number(self):
        return self.page.previous_page_number() if self.page.has_previous() else None

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('total', self.page.paginator.count),
            ('page_count', self.page.paginator.num_pages),
            ('page_size', self.page_size),
            ('current_page', self.current_page()),
            ('prev_page', self.prev_page_number()),
            ('next_page', self.next_page_number()),
            ('results', data)
        ]))
