"""Pagination classes for the REST API."""

from rest_framework.pagination import PageNumberPagination


class LimitPagination(PageNumberPagination):
    """Page number pagination with page size set by the ``limit`` param."""

    page_size_query_param = 'limit'
