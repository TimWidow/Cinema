from django.contrib import admin
from django.contrib.admin import DateFieldListFilter
from films.models import *


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'session_id', 'session_date_get', 'session_time_get', 'row', 'seat', 'price',)
    search_fields = ('session_id__film__name',)
    list_filter = (
        ('session_id__date', DateFieldListFilter),
    )


@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    list_display = ('name', 'production', 'year', 'director', 'genre_get',)
    search_fields = ('name', 'production', 'year', 'director', 'genre__name')


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'film', 'date', 'time', 'price',)
    search_fields = ('film__name',)
    list_filter = (
        ('date', DateFieldListFilter),
    )
    fieldsets = ((
                     None, {
                         'fields': ('date', 'time', 'film', 'price')
                     }),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "film":
            kwargs["queryset"] = Film.objects.filter(in_theatre__lte=datetime.datetime.today().date())
        return super(SessionAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('for_name', 'session_get', 'session_date_get', 'session_time_get', 'row', 'seat', 'price')
    search_fields = ('session_id__film__name', 'for_name',)
    list_filter = (
        ('session_id__date', DateFieldListFilter),
    )


@admin.register(Sell)
class SellAdmin(admin.ModelAdmin):
    list_display = ('get_film_name', 'get_session_date', 'get_session_time', 'kol_bil', 'summa',)
    search_fields = ('session_id__film__name', 'session_id__date',)
    list_filter = (
        ('session_id__date', DateFieldListFilter),
    )
