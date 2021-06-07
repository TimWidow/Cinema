from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django.forms import ValidationError
import datetime


class Genre(models.Model):
    name = models.CharField(max_length=15)

    def __str__(self):
        return self.name


class Film(models.Model):
    name = models.CharField(max_length=50)
    second_name = models.CharField(max_length=50)
    url_name = models.CharField(max_length=50)
    description = models.TextField()
    duration = models.FloatField()
    format = models.CharField(max_length=3)
    production = models.CharField(max_length=20)
    director = models.CharField(max_length=50)
    actors = models.TextField()
    year = models.IntegerField()
    image = models.ImageField(
        upload_to="media/films",
        height_field="image_height",
        width_field="image_width"
    )
    image_height = models.PositiveIntegerField(
        null=True,
        blank=True,
        editable=False,
        default="525"
    )
    image_width = models.PositiveIntegerField(
        null=True,
        blank=True,
        editable=False,
        default="260"
    )
    trailer = models.URLField()
    in_theatre = models.DateField(blank=True)
    genre = models.ManyToManyField(Genre)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    def genre_get(self):
        a = ''
        for i in self.genre.all():
            a += i.name + ','

        return a[:-1]


class Session(models.Model):
    date = models.DateField()
    time = models.CharField(max_length=30)
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    price = models.CharField(validators=[validate_comma_separated_integer_list], max_length=30)

    def __unicode__(self):
        name = str(self.film) + "," + str(self.date) + " " + str(self.time)
        return name

    def __str__(self):
        name = self.film.name + ", " + str(self.date) + " " + str(self.time)[:5]
        return name

    def film_name_get(self):
        return self.film.name

    def save(self, *args, **kwargs):
        for session in Session.objects.filter(date=getattr(self, 'date')):

            time1 = datetime.datetime.combine(
                getattr(self, 'date'),
                datetime.datetime.strptime(
                    getattr(self, 'time'),
                    '%Y-%m-%d').time()
            )
            time2 = datetime.datetime.now()

            if getattr(self, 'time') == session.time or time1 < time2:
                raise ValidationError('Выбрано неподходящее время для сеанса.')

        super(Session, self).save(*args, **kwargs)


class Booking(models.Model):
    session_id = models.ForeignKey(Session, on_delete=models.CASCADE)
    for_name = models.CharField(max_length=20)
    row = models.IntegerField(default=0)
    seat = models.IntegerField(default=0)
    price = models.IntegerField(default=0)

    def __unicode__(self):
        return self.for_name

    def __str__(self):
        return self.for_name

    def session_get(self):
        return self.session_id.film.name

    def session_date_get(self):
        return self.session_id.date

    def session_time_get(self):
        return self.session_id.time


class Ticket(models.Model):
    session_id = models.ForeignKey(Session, on_delete=models.CASCADE)
    row = models.IntegerField(default=0)
    seat = models.IntegerField(default=0)
    price = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        sell, created = Sell.objects.get_or_create(seans_id=getattr(self, 'session_id'))
        sell.kol_bil += 1
        sell.summa += int(getattr(self, 'price'))
        sell.save()

        super(Ticket, self).save(*args, **kwargs)

    def __unicode__(self):
        return str(self.id)

    def __str__(self):
        return str(self.id)

    def session_get(self):
        return self.session_id.film.name

    def session_date_get(self):
        return self.session_id.date

    def session_time_get(self):
        return self.session_id.time


class Sell(models.Model):
    session_id = models.ForeignKey(Session, on_delete=models.CASCADE)
    kol_bil = models.IntegerField(default=0)
    summa = models.IntegerField(default=0)

    def __unicode__(self):
        return str(self.session_id)

    def __str__(self):
        return str(self.session_id)

    def get_film_name(self):
        return self.session_id.film.name

    def get_session_date(self):
        return self.session_id.date

    def get_session_time(self):
        return self.session_id.time
