from rest_framework import serializers
from django.utils import timezone

from reviews.models import Title, Category, Genre


class TitleReadSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug', read_only=True
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug', many=True, read_only=True
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'category', 'genre')


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
