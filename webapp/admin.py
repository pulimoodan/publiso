from django.contrib import admin
from .models import Author, Book, Category
from .widgets import CustomDatePickerInput
from django import forms

class AuthorForm(forms.ModelForm):
    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js', # jquery
            'https://cdn.jsdelivr.net/npm/bootstrap@4.6.1/dist/js/bootstrap.bundle.min.js',
        )
        css = {
             'all': ('https://cdnjs.cloudflare.com/ajax/libs/bootstrap-datepicker/1.9.0/css/bootstrap-datepicker.min.css',)
        }
    class Meta:
        model = Author
        widgets = {
            'dod': CustomDatePickerInput,
            'dob': CustomDatePickerInput,
        }
        fields = '__all__' # required for Django 3.x

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__' # required for Django 3.x

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__' # required for Django 3.x

class AuthorAdmin(admin.ModelAdmin):
    form = AuthorForm
    search_fields = ['name',]
    
class CategoryAdmin(admin.ModelAdmin):
    form = CategoryForm
    exclude = ['date']
    search_fields = ['name',]
    
class BookAdmin(admin.ModelAdmin):
    form = BookForm
    exclude = ['date']
    autocomplete_fields = ['author', 'category',]


# Register your models here.
admin.site.register(Author, AuthorAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Book, BookAdmin)