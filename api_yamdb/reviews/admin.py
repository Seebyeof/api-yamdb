from django.contrib import admin

from .models import (
    Category,
    Genre,
    Title,
    Comment,
    Review,
    User
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'year', 'category')
    list_filter = ('category', 'genre')
    search_fields = ('name',)
    filter_horizontal = ('genre',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'score', 'pub_date')
    list_filter = ('score', 'pub_date')
    search_fields = ('text', 'author__username', 'title__name')
    raw_id_fields = ('title', 'author')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'review', 'author', 'pub_date')
    list_filter = ('pub_date',)
    search_fields = ('text', 'author__username', 'review__title__name')
    raw_id_fields = ('review', 'author')
