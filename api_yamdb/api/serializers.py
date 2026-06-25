from rest_framework import serializers
from django.utils import timezone

from reviews.models import (
    Title,
    Category,
    Genre,
    Review,
    Comment
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')

    def validate_slug(self, value):
        if Category.objects.filter(slug=value).exists():
            raise serializers.ValidationError(
                "Категория с таким slug уже существует."
            )
        return value


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')

    def validate_slug(self, value):
        if Genre.objects.filter(slug=value).exists():
            raise serializers.ValidationError(
                "Жанр с таким slug уже существует."
            )
        return value


class TitleReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.FloatField(read_only=True, default=None)

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category'
        )


class TitleCreateSerializer(serializers.ModelSerializer):
    category = serializers.SlugField(write_only=True)
    genre = serializers.ListField(
        child=serializers.SlugField(),
        write_only=True
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'category', 'genre')
        read_only_fields = ('id',)

    def validate_year(self, value):
        current_year = timezone.now().year
        if value > current_year:
            raise serializers.ValidationError(
                f"Год выпуска не может быть больше {current_year}."
            )
        return value

    def validate_category(self, value):
        try:
            return Category.objects.get(slug=value)
        except Category.DoesNotExist:
            raise serializers.ValidationError(
                f"Категория со слагом '{value}' не найдена."
            )

    def validate_genre(self, value):
        genres = []
        for slug in value:
            try:
                genres.append(Genre.objects.get(slug=slug))
            except Genre.DoesNotExist:
                raise serializers.ValidationError(
                    f"Жанр со слагом '{slug}' не найден."
                )
        return genres

    def create(self, validated_data):
        category = validated_data.pop('category')
        genres = validated_data.pop('genre')
        title = Title.objects.create(category=category, **validated_data)
        title.genre.set(genres)
        return title


class ReviewCreateSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    score = serializers.IntegerField(min_value=1, max_value=10)

    class Meta:
        model = Review
        fields = ('id', 'text', 'score', 'author', 'pub_date',)
        read_only_fields = ('author', 'pub_date',)

    def validate(self, data):
        request = self.context['request']

        if request.method != 'POST':
            return data

        title_id = self.context['view'].kwargs.get('title_pk')

        if Review.objects.filter(
            title_id=title_id,
            author=request.user
        ).exists():
            raise serializers.ValidationError(
                'Вы уже оставили отзыв на это произведение.'
            )

        return data


class CommentCreateSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date',)
        read_only_fields = ('author', 'pub_date',)
