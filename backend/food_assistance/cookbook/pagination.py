from rest_framework.pagination import PageNumberPagination


class SbscrptPagination(PageNumberPagination):
    page_size_query_param = 'limit'
