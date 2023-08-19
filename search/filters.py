from rest_framework import filters


class CustomOrderingFilter(filters.OrderingFilter):
    ordering_description = 'view_count(조회수), published(날짜순)'
