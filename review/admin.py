from django.contrib import admin
from django.contrib.admin import DateFieldListFilter
from review.models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('get_film_name', 'name', 'email', 'date')
    search_fields = ('film__name', 'name', 'email',)
    list_filter = (
        ('date', DateFieldListFilter),
    )
