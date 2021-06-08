from django.db import models
from films.models import Film


class Review(models.Model):
    name = models.CharField(max_length=30)
    text = models.TextField(max_length=20000)
    email = models.EmailField()
    date = models.DateField()
    film = models.ForeignKey(Film, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.film.name

    def get_film_name(self):
        return self.film.name
