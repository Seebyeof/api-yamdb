from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


MAX_LENGTH_NAME = 256
MAX_LENGTH_SLUG = 50
MIN_SCORE = 1
MAX_SCORE = 10


def current_year():
    return timezone.now().year


User = get_user_model()


class BaseNameSlugModel(models.Model):
    """Абстрактная модель с полями name и slug."""
    name = models.CharField(
        max_length=MAX_LENGTH_NAME,
        unique=True,
        verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=MAX_LENGTH_SLUG,
        unique=True,
        verbose_name='Слаг'
    )

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name


class Category(BaseNameSlugModel):
    class Meta(BaseNameSlugModel.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(BaseNameSlugModel):
    class Meta(BaseNameSlugModel.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.CharField(
        max_length=MAX_LENGTH_NAME,
        verbose_name='Название произведения'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='titles',
        verbose_name='Категория',
        blank=True,
        null=True
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='Жанры'
    )
    year = models.IntegerField(
        verbose_name='Год выпуска',
        validators=[MaxValueValidator(limit_value=current_year)],
        db_index=True
    )
    description = models.TextField(
        verbose_name='Описание',
        blank=True
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class BaseReviewComment(models.Model):
    """Абстрактная модель с общими полями для отзывов и комментариев."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)ss',
        verbose_name='Автор'
    )
    text = models.TextField(
        verbose_name='Текст'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.author} - {self.text[:20]}...'


class Review(BaseReviewComment):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    score = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(MIN_SCORE),
            MaxValueValidator(MAX_SCORE)
        ],
        verbose_name='Оценка'
    )

    class Meta:
        ordering = ('-pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author'),
                name='unique_review'
            )
        ]
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return f'{self.author} - {self.title}'


class Comment(BaseReviewComment):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )

    class Meta:
        ordering = ('pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'{self.author} - {self.review}'
