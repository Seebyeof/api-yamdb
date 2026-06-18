from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MaxValueValidator
from django.utils import timezone


User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=256, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=256, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name="Название"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='titles',
        verbose_name="Категория"
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name="Жанры"
    )
    year = models.PositiveIntegerField(
        verbose_name="Год выпуска",
        validators=[MaxValueValidator(limit_value=timezone.now().year)]
    )

    def __str__(self):
        return self.text
