from django.conf import settings
from django.core.paginator import (
    EmptyPage,
    Paginator,
    PageNotAnInteger,
)


def wrap_with_paginator(objects_list, page: int, per_page: int):
    paginator = Paginator(objects_list, per_page)
    try:
        objects = paginator.page(page)
    except PageNotAnInteger:
        objects = paginator.page(1)
    except EmptyPage:
        objects = paginator.page(paginator.num_pages)
    return objects
