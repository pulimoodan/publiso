from django import template
from webapp.models import Author, BookRead, Follow, Library, Book, Profile
from django.contrib.auth.models import User
from PyPDF2 import PdfFileReader

register = template.Library()

def is_added_to_library(value, arg):
    book = Book.objects.get(id=value)
    user = User.objects.get(id=arg)

    output = False

    try:
        Library.objects.get(user=user, book=book)
        output = True
    except:
        pass
    
    return output

def get_current_page(value, arg):
    book = Book.objects.get(id=value)
    user = User.objects.get(pk=arg)
    page_number = 0
    try:
        book_read = BookRead.objects.get(user=user, book=book)
        page_number = book_read.page
    except:
        pass
    
    return page_number

def is_following(value, arg):
    author = Author.objects.get(id=value)
    user = User.objects.get(pk=arg)
    following = False
    try:
        Follow.objects.get(user=user, author=author)
        following = True
    except:
        pass
    
    return following

def get_profile_picture(value):
    profile_picture = '/static/image/profile.jpg'
    try:
        user = User.objects.get(pk=value)
        profile = Profile.objects.get(user=user)
        profile_picture = profile.image.url
    except:
        pass
    
    return profile_picture

register.filter('get_current_page', get_current_page)
register.filter('get_profile_picture', get_profile_picture)
register.filter('is_following', is_following)
register.filter('is_added_to_library', is_added_to_library)