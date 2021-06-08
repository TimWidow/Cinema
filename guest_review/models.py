from django.db import models


class GuestReview(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField()
    text = models.TextField(max_length=20000)
    date = models.DateField()

    def __str__(self):
        return self.name


class AdminReview(models.Model):
    text = models.TextField(max_length=20000)
    guestReview = models.ForeignKey(GuestReview, on_delete=models.DO_NOTHING)
