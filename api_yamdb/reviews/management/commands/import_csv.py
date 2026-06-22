import csv
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
from reviews.models import Category, Genre, Title, Review, Comment
from users.models import User


class Command(BaseCommand):
    help = 'Импорт данных из CSV-файлов в базу данных'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            help=(
                'Полный путь к папке с CSV-файлами'
                '(по умолчанию static/data/)'
            )
        )

    def handle(self, *args, **options):
        user_path = options.get('path')
        if user_path:
            base_path = Path(user_path)
        else:
            candidates = [
                settings.BASE_DIR / 'static' / 'data',
                settings.BASE_DIR / 'api_yamdb' / 'static' / 'data',
            ]
            base_path = None
            for p in candidates:
                if p.exists():
                    base_path = p
                    break
            if base_path is None:
                self.stderr.write(self.style.ERROR(
                    f'Папка с данными не найдена. Проверьте пути: {candidates}'
                ))
                return

        self.stdout.write(f'Импорт из папки: {base_path}')

        with transaction.atomic():
            try:
                self.import_users(base_path)
                self.import_categories(base_path)
                self.import_genres(base_path)
                self.import_titles(base_path)
                self.import_title_genre(base_path)
                self.import_reviews(base_path)
                self.import_comments(base_path)
                self.stdout.write(self.style.SUCCESS(
                    '✅ Все данные успешно импортированы'
                ))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'❌ Ошибка: {e}'))
                raise

    def _read_csv(self, filename, base_path):
        file_path = base_path / filename
        if not file_path.exists():
            self.stderr.write(self.style.WARNING(
                f'⚠️ Файл {file_path} не найден, пропускаем'
            ))
            return []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)

    def _get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            user = User.objects.create(
                id=user_id,
                username=f'user_{user_id}',
                email=f'user_{user_id}@example.com'
            )
            return user

    def _get_object_by_id_or_slug(self, model, value):
        if str(value).isdigit():
            try:
                return model.objects.get(id=int(value))
            except model.DoesNotExist:
                return None
        else:
            try:
                return model.objects.get(slug=value)
            except model.DoesNotExist:
                return None

    def _get_field_value(self, row, possible_names):
        for name in possible_names:
            if name in row:
                return row[name]
        return None

    def import_users(self, base_path):
        rows = self._read_csv('users.csv', base_path)
        for row in rows:
            user, created = User.objects.get_or_create(
                id=int(row['id']),
                defaults={
                    'username': row['username'],
                    'email': row['email'],
                    'role': row.get('role', 'user'),
                    'bio': row.get('bio', ''),
                    'first_name': row.get('first_name', ''),
                    'last_name': row.get('last_name', ''),
                    'confirmation_code': row.get('confirmation_code', ''),
                }
            )
            if created:
                self.stdout.write(f'Создан пользователь {user.username}')

    def import_categories(self, base_path):
        rows = self._read_csv('category.csv', base_path)
        for row in rows:
            category, created = Category.objects.get_or_create(
                slug=row['slug'],
                defaults={'name': row['name']}
            )
            if created:
                self.stdout.write(f'Создана категория {category.name}')

    def import_genres(self, base_path):
        rows = self._read_csv('genre.csv', base_path)
        for row in rows:
            genre, created = Genre.objects.get_or_create(
                slug=row['slug'],
                defaults={'name': row['name']}
            )
            if created:
                self.stdout.write(f'Создан жанр {genre.name}')

    def import_titles(self, base_path):
        rows = self._read_csv('titles.csv', base_path)
        for row in rows:
            category_value = row['category']
            category = self._get_object_by_id_or_slug(Category, category_value)
            if category is None:
                self.stderr.write(
                    f'Категория {category_value} не найдена, пропускаем'
                )
                continue

            title, created = Title.objects.get_or_create(
                id=int(row['id']),
                defaults={
                    'name': row['name'],
                    'year': int(row['year']),
                    'description': row.get('description', ''),
                    'category': category,
                }
            )
            if created:
                self.stdout.write(f'Создано произведение {title.name}')

    def import_title_genre(self, base_path):
        rows = self._read_csv('genre_title.csv', base_path)
        for row in rows:
            genre_value = self._get_field_value(
                row,
                ['genre_id', 'genre_slug', 'genre']
            )
            if not genre_value:
                self.stderr.write(
                    'Не найдено поле для жанра в genre_title.csv'
                )
                continue

            try:
                title = Title.objects.get(id=int(row['title_id']))
            except Title.DoesNotExist:
                self.stderr.write(
                    f'Произведение {row["title_id"]} не найдено, пропускаем'
                )
                continue

            genre = self._get_object_by_id_or_slug(Genre, genre_value)
            if genre is None:
                self.stderr.write(f'Жанр {genre_value} не найден, пропускаем')
                continue

            title.genre.add(genre)

    def import_reviews(self, base_path):
        rows = self._read_csv('review.csv', base_path)
        if rows:
            self.stdout.write(f"Колонки в review.csv: {list(rows[0].keys())}")
        for row in rows:
            title_id = row.get('title_id')
            author_id = row.get('author')
            if not title_id or not author_id:
                self.stderr.write(
                    f'Не найдены поля title_id или author в строке: {row}'
                )
                continue
            try:
                title = Title.objects.get(id=int(title_id))
                author = self._get_user(int(author_id))
            except Title.DoesNotExist:
                self.stderr.write(
                    f'Произведение {title_id} не найдено, пропускаем'
                )
                continue

            review, created = Review.objects.get_or_create(
                id=int(row['id']),
                defaults={
                    'title': title,
                    'author': author,
                    'text': row['text'],
                    'score': int(row['score']),
                    'pub_date': row.get('pub_date'),
                }
            )
            if created:
                self.stdout.write(f'Создан отзыв от {author.username}')

    def import_comments(self, base_path):
        rows = self._read_csv('comments.csv', base_path)
        if rows:
            self.stdout.write(
                f"Колонки в comments.csv: {list(rows[0].keys())}"
            )
        for row in rows:
            review_id = row.get('review_id')
            author_id = row.get('author')
            if not review_id or not author_id:
                self.stderr.write(
                    f'Не найдены поля review_id или author в строке: {row}'
                )
                continue
            try:
                review = Review.objects.get(id=int(review_id))
                author = self._get_user(int(author_id))
            except Review.DoesNotExist:
                self.stderr.write(f'Отзыв {review_id} не найден, пропускаем')
                continue

            comment, created = Comment.objects.get_or_create(
                id=int(row['id']),
                defaults={
                    'review': review,
                    'author': author,
                    'text': row['text'],
                    'pub_date': row.get('pub_date'),
                }
            )
            if created:
                self.stdout.write(f'Создан комментарий от {author.username}')
