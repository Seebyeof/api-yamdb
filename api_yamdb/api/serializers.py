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
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        exclude = ('id',)


class TitleCreateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
        write_only=True
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
        write_only=True
    )
    rating = serializers.FloatField(read_only=True, default=None)

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'description',
            'category',
            'genre',
            'rating'
        )

    def validate_year(self, value):
        current_year = timezone.now().year
        if value > current_year:
            raise serializers.ValidationError(
                f"Год выпуска не может быть больше {current_year}."
            )
        return value

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['category'] = CategorySerializer(instance.category).data
        representation['genre'] = GenreSerializer(instance.genre.all(), many=True).data
        return representation


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
