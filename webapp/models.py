from django.db import models
from django.dispatch import receiver
import os
from django_countries.fields import CountryField
import uuid
from django.contrib.auth.models import User
from django.db.models import Q
from datetime import date, timedelta
from django.db.models import Sum
from languages.fields import LanguageField
from PyPDF2 import PdfFileReader
from colorfield.fields import ColorField
from datetime import datetime, timedelta

class ChangePassword(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    changed = models.BooleanField(default=False)
    key = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return f'{self.user.username} Password recovery'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profiles')

    def __str__(self):
        return f'{self.user.username} Profile'

@receiver(models.signals.post_delete, sender=Profile)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)

@receiver(models.signals.pre_save, sender=Profile)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = Profile.objects.get(pk=instance.pk).image
    except Profile.DoesNotExist:
        return False

    new_file = instance.image
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


class Author(models.Model):
    name = models.CharField(max_length=60)
    full_name = models.CharField(max_length=100)
    dob = models.DateField()
    dod = models.DateField(null=True, blank=True)
    country = CountryField()
    profile_picture = models.ImageField(upload_to ='authors')
    def __str__(self):
        return self.name
    @property
    def books(self):
        return Book.objects.filter(author=self).count()
    @property
    def reads_count(self):
        books = Book.objects.filter(author=self)
        reads = 0
        for book in books:
            reads += BookRead.objects.filter(book=book, completed=True).count()
        return reads
    @property
    def rating(self):
        books = Book.objects.filter(author=self)
        value = 0
        num = 0
        for book in books:
            num += Rating.objects.filter(book=book).count()
            sum = Rating.objects.filter(book=book).aggregate(Sum('score'))
            if sum['score__sum'] is not None:
                value += sum['score__sum']
        if value == 0:
            value = 5
        else:
            value = value / num
        return value


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)


class Category(models.Model):
    name = models.CharField(max_length=60)
    date = models.DateField(auto_now_add=True)
    color = ColorField(default='#5CD17B')
    def __str__(self):
        return self.name
    @property
    def books(self):
        return Book.objects.filter(category=self).count()

def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('books', filename)

class Book(models.Model):
    name = models.CharField(max_length=60)
    description = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    language = LanguageField()
    date = models.DateField(auto_now_add=True)
    cover_picture = models.ImageField(upload_to ='covers')
    book = models.FileField(upload_to =get_file_path)
    pages = models.IntegerField(default=1)
    def get_absolute_url(self):
        return "/book/%i/" % self.id
    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        pdf = PdfFileReader(self.book)
        self.pages = pdf.getNumPages()
        super().save(*args, **kwargs)
    @property
    def reads_count(self):
        return BookRead.objects.filter(book=self, completed=True).count()
    @property
    def latest_reads_count(self):
        yesterday = date.today() - timedelta(days = 1)
        return BookRead.objects.filter(book=self, completed=True).filter(Q(date__gte=yesterday)|Q(date=yesterday)).count()
    @property
    def rating(self):
        num = Rating.objects.filter(book=self).count()
        sum = Rating.objects.filter(book=self).aggregate(Sum('score'))
        value = 5
        if sum['score__sum'] is not None:
            value = sum['score__sum'] / num
        return value


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    score = models.DecimalField(max_digits=2, decimal_places=1) 


class Library(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)


class BookRead(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    page = models.IntegerField()
    completed = models.BooleanField(default=False)

    def __str__(self):
        return '{0} in {1} book'.format(self.user, self.book.name)

@receiver(models.signals.post_delete, sender=Book)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.book:
        if os.path.isfile(instance.book.path):
            os.remove(instance.book.path)
    if instance.cover_picture:
        if os.path.isfile(instance.cover_picture.path):
            os.remove(instance.cover_picture.path)

@receiver(models.signals.pre_save, sender=Book)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = Book.objects.get(pk=instance.pk).book
    except Book.DoesNotExist:
        return False

    new_file = instance.book
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)

    try:
        old_file = Book.objects.get(pk=instance.pk).cover_picture
    except Book.DoesNotExist:
        return False

    new_file = instance.cover_picture
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)

@receiver(models.signals.post_delete, sender=Author)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.profile_picture:
        if os.path.isfile(instance.profile_picture.path):
            os.remove(instance.profile_picture.path)

@receiver(models.signals.pre_save, sender=Author)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = Author.objects.get(pk=instance.pk).profile_picture
    except Author.DoesNotExist:
        return False

    new_file = instance.profile_picture
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)