from django.db import models
from django.core.exceptions import ValidationError

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')

    def __str__(self):
        return self.name

class Article(models.Model):
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')
    image = models.ImageField(upload_to='articles/', blank=True, null=True, verbose_name='Изображение')
    # другие поля статьи...

    tags = models.ManyToManyField(Tag, through='ArticleScope', related_name='articles', verbose_name='Тематики')

    def clean(self):
        super().clean()
        # Проверка, что ровно один основной раздел
        main_scopes = self.scopes.filter(is_main=True)
        if main_scopes.count() != 1:
            raise ValidationError('Должен быть ровно один основной раздел.')

    def __str__(self):
        return self.title

class ArticleScope(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='scopes')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='scopes')
    is_main = models.BooleanField(default=False, verbose_name='Основной')

    class Meta:
        unique_together = ('article', 'tag')
        verbose_name = 'Тематика статьи'
        verbose_name_plural = 'Тематики статьи'

    def clean(self):
        # Проверка, что если is_main=True, то у статьи нет другого основного раздела
        if self.is_main:
            qs = ArticleScope.objects.filter(article=self.article, is_main=True)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError('У статьи уже есть основной раздел.')

    def __str__(self):
        return f'{self.tag} для {self.article} {"(основной)" if self.is_main else ""}'
