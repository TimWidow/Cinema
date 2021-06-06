from django.contrib import admin
from django.contrib.admin import DateFieldListFilter
from guest_review.models import GuestReview, AdminReview


@admin.register(GuestReview)
class GuestReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'date')
    search_fields = ('name',)
    list_filter = (
        ('date', DateFieldListFilter),
    )


@admin.register(AdminReview)
class AdminReviewAdmin(admin.ModelAdmin):
    list_display = ('guestReview', 'text',)
    search_fields = ('guestReview__name',)
    list_filter = (
        ('guestReview__date', DateFieldListFilter),
    )
