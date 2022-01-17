from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from pdf2image import convert_from_path
from .models import Author, Book, BookRead, Category, ChangePassword, Follow, Library, Profile, Rating
import base64
from io import BytesIO
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as login_user, logout as logout_user
from django.core.mail import send_mail
from publiso.settings import EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
from django.views.decorators.csrf import csrf_exempt


def about(request):
    user = {'username':'unknown', 'first_name':'unknown', 'last_name':'person'}
    if request.user.is_authenticated:
        user = request.user
    return render(request, 'about.html', {'user':user})


def contact(request):
    user = {'username':'unknown', 'first_name':'unknown', 'last_name':'person'}
    if request.user.is_authenticated:
        user = request.user
    return render(request, 'contact.html', {'user':user})


def policy(request):
    user = {'username':'unknown', 'first_name':'unknown', 'last_name':'person'}
    if request.user.is_authenticated:
        user = request.user
    return render(request, 'policy.html', {'user':user})


def terms(request):
    user = {'username':'unknown', 'first_name':'unknown', 'last_name':'person'}
    if request.user.is_authenticated:
        user = request.user
    return render(request, 'terms.html', {'user':user})


def login(request):
    if request.user.is_authenticated:
        return redirect('home')
    success = request.GET.get('success', None) 
    error = request.GET.get('error', None) 
    next = request.GET.get('next', None) 
    if request.method == 'POST':
        password = request.POST.get('password') 
        username = request.POST.get('username')
        user = authenticate(username=username, password=password)
        if user is not None:
            login_user(request, user)
            if next is not None:
                return redirect(next)
            else:
                return redirect('home')
        else:
            return redirect('/login?error=1')
    return render(request, 'login.html', {'error':error, 'success':success})


@login_required(login_url='/login')
def profile_upload(request):
    if request.method == 'POST':
        profile = ''
        try:
            profile = Profile.objects.get(user=request.user)
            profile.image = request.FILES.get('file')
            profile.save()
        except:
            profile = Profile(image = request.FILES.get('file'), user=request.user)
            profile.save()
        data = {
            'url': profile.image.url,
        }
        return JsonResponse(data)
    return redirect('home')


def signup(request):
    if request.user.is_authenticated:
        return redirect('home')
    success = request.GET.get('success', None) 
    error = request.GET.get('error', None) 
    if request.method == 'POST':
        username = request.POST.get('username') 
        email = request.POST.get('email') 
        password = request.POST.get('password') 
        cpassword = request.POST.get('cpassword')
        if User.objects.filter(email=email).exists():
            return redirect('/signup?error=1')
        if User.objects.filter(username=username).exists():
            return redirect('/signup?error=2')
        if password == cpassword:
            user = User.objects.create_user(username, email, password)
            user.save()
            return redirect('/signup?success=1')
        else:
            return redirect('/signup?error=3')
    return render(request, 'signup.html', {'error':error, 'success':success})


def forgot_username(request):
    if request.user.is_authenticated:
        return redirect('home')
    success = request.GET.get('success', None) 
    error = request.GET.get('error', None)
    username = request.GET.get('username', None)
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            username = user.username
            return redirect(f'/forgot-username?success=1&username={username}')
        except:
            return redirect('/forgot-username?error=1')

    return render(request, 'forgot-username.html', {'error':error, 'success':success, 'username':username})


@login_required(login_url='/login')
def details(request):
    success = request.GET.get('success', None) 
    error = request.GET.get('error', None)
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        user = authenticate(username=request.user.username, password=password)
        if user is not None:

            if email is not None and not email.replace(" ", "") == '':
                if not User.objects.filter(email=email).exclude(id=request.user.id).exists():
                    user.email = email
                else:
                    return redirect('/details?error=2')

            if username is not None and not username.replace(" ", "") == '':
                if not User.objects.filter(username=username).exclude(id=request.user.id).exists():
                    user.username = username
                else:
                    return redirect('/details?error=3')

            if first_name is not None and not first_name.replace(" ", "") == '':
                user.first_name = first_name
            if last_name is not None and not last_name.replace(" ", "") == '':
                user.last_name = last_name

            user.save()
            return redirect('/details?success=1')
        else:
            return redirect('/details?error=1')
    return render(request, 'details.html', {'error':error, 'success':success, 'user':request.user})


def forgot_password(request):
    success = request.GET.get('success', None) 
    error = request.GET.get('error', None)
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        email = request.POST.get('email')
        if User.objects.filter(email=email).exists():
            change_pass = ChangePassword(user=User.objects.get(email=email))
            change_pass.save()
            subject = 'Publiso Password Recovery'
            link = f'https://publiso.in/change-password/{change_pass.key}'
            message = f'Follow the link to recover your password : {link}'
            recepient = email
            send_mail(subject, 
                message, EMAIL_HOST_USER, [recepient], fail_silently = False)
            return redirect('/forgot-password?success=1')
        else:
            return redirect('/forgot-password?error=1')
    return render(request, 'forgot-password.html', {'error':error, 'success':success})


def change_password(request, key):
    success = request.GET.get('success', None) 
    error = request.GET.get('error', None)
    if not ChangePassword.objects.filter(key=key).exists():
        return redirect('login')
    if request.method == 'POST':
        password = request.POST.get('password')
        cpassword = request.POST.get('cpassword')
        if ChangePassword.objects.filter(key=key, changed=False).exists():
            if password == cpassword:
                change_pass = ChangePassword.objects.get(key=key)
                user = change_pass.user
                user.set_password(password)
                user.save()
                change_pass.changed = True
                change_pass.save()
                return redirect(f'/change-password/{key}?success=1')
            else:
                return redirect(f'/change-password/{key}?error=1')
        else:
            return redirect(f'/change-password/{key}?error=2')
    return render(request, 'change-password.html', {'error':error, 'success':success})


@login_required(login_url='/login')
def logout(request):
    logout_user(request)
    return redirect('login')


@login_required(login_url='/login')
def profile(request):
    follows = Follow.objects.filter(user=request.user).order_by('-date')[:6]
    reads = BookRead.objects.filter(user=request.user).order_by('-date')[:6]
    return render(request, 'profile.html', {'follows':follows, 'reads':reads, 'user':request.user})


# Create your views here.
def home(request):
    books = Book.objects.all()
    authors = Author.objects.all().order_by('-id')[:3]
    books_of_the_day = sorted(books, key=lambda t: (t.latest_reads_count, t.rating), reverse=True)[:3]
    popular_books = sorted(books, key=lambda t: t.rating, reverse=True)[:6]
    most_read_books = sorted(books, key=lambda t: t.reads_count, reverse=True)[:6]
    latest_books = books.order_by('-date')[:6]
    user = {'username':'unknown', 'first_name':'unknown', 'last_name':'person'}
    categories = Category.objects.all()
    if request.user.is_authenticated:
        user = request.user
    return render(request, 'home.html', {'user':user, 'categories':categories, 'authors':authors, 'books_of_the_day':books_of_the_day, 'latest_books':latest_books, 'popular_books':popular_books, 'most_read_books':most_read_books})


@login_required(login_url='/login')
def recommended(request):
    most = 0
    category = None
    categories = Category.objects.all()
    for c in categories:
        count = BookRead.objects.filter(user=request.user, book__category=c).count()
        if count > most:
            most = count
            category = c

    authors = Author.objects.all()
    author = None
    most = 0
    for a in authors:
        count = BookRead.objects.filter(user=request.user, book__author=a).count()
        if count > most:
            most = count
            author = a
    
    books = []
    if category is not None and author is not None:
        books = Book.objects.filter(Q(author=author) | Q(category=category))[:9]
    user = request.user
    return render(request, 'recommended.html', {'user':user, 'books':books})


def categories(request):
    categories = Category.objects.all()
    categories = sorted(categories, key=lambda t: t.books, reverse=True)
    user = {'username':'unknown', 'first_name':'unknown', 'last_name':'person'}
    if request.user.is_authenticated:
        user = request.user
    return render(request, 'categories.html', {'user':user, 'categories':categories})


def category(request, id):
    category = Category.objects.get(pk=id)
    categories = Category.objects.all()
    books = Book.objects.filter(category=category)
    user = {'username':'unknown', 'first_name':'unknown', 'last_name':'person'}
    if request.user.is_authenticated:
        user = request.user
    return render(request, 'category.html', {'user':user, 'books':books, 'category':category, 'categories':categories})


def popular(request):
    books = Book.objects.all()
    books = sorted(books, key=lambda t: t.rating, reverse=True)
    user = {'username':'unknown', 'first_name':'unknown', 'last_name':'person'}
    if request.user.is_authenticated:
        user = request.user
    return render(request, 'popular.html', {'user':user, 'books':books})


def most_read(request):
    books = Book.objects.all()
    books = sorted(books, key=lambda t: t.reads_count, reverse=True)
    user = {'username':'unknown', 'first_name':'unknown', 'last_name':'person'}
    if request.user.is_authenticated:
        user = request.user
    return render(request, 'most-read.html', {'user':user, 'books':books})


def latest(request):
    books = Book.objects.all().order_by('-date')
    user = {'username':'unknown', 'first_name':'unknown', 'last_name':'person'}
    if request.user.is_authenticated:
        user = request.user
    return render(request, 'latest.html', {'user':user, 'books':books})


def book(request, id):
    if request.method == 'POST':
        if request.user.is_authenticated:
            book_id = request.POST.get('book_id')
            score = request.POST.get('score')
            book = Book.objects.get(pk=book_id)
            is_read = False
            try:
                book_read = BookRead.objects.get(user=request.user, book=book)
                is_read = book_read.completed
            except:
                pass
            if is_read:
                try:
                    rating = Rating.objects.get(user=request.user, book=book)
                except:
                    rating = Rating(user=request.user, book=book, score=float(score))
                    rating.save()
        return redirect(f'/book/{id}')
    book = Book.objects.get(pk=id)
    related_books = Book.objects.filter(category=book.category)[:6]
    is_read = False
    rating = None
    if request.user.is_authenticated:
        try:
            book_read = BookRead.objects.get(user=request.user, book=book)
            is_read = book_read.completed
            rating = Rating.objects.get(user=request.user, book=book)
        except:
            pass
    user = {'username':'unknown', 'first_name':'unknown', 'last_name':'person', 'unknown':True}
    if request.user.is_authenticated:
        user = request.user
    return render(request, 'book.html', {'user':user, 'book':book, 'related_books':related_books, 'is_read':is_read, 'rating':rating})


def author(request, id):
    author = Author.objects.get(pk=id)
    books = Book.objects.filter(author=author)[:6]
    return render(request, 'author.html', {'user':request.user, 'books':books, 'author':author})


def author_search(request):
    if request.method == 'GET':
        keyword = request.GET.get('keyword')
        sort = request.GET.get('sort')
        authors = Author.objects.filter(Q(name__icontains=keyword.lower()) | Q(full_name__icontains=keyword.lower()))
        
        if sort == 'rating':
            authors = sorted(authors, key=lambda t: t.rating, reverse=True)
        elif sort == 'reads':
            authors = sorted(authors, key=lambda t: t.reads_count, reverse=True)
        elif sort == 'books':
            authors = sorted(authors, key=lambda t: t.books, reverse=True)
        
        user = {'username':'unknown', 'first_name':'unknown', 'last_name':'person', 'unknown':True}
        if request.user.is_authenticated:
            user = request.user

        return render(request, 'search.html', {'user':user, 'authors':authors, 'keyword':keyword, 'sort':sort, 'target':'authors'})
    return redirect('home')


def category_search(request):
    if request.method == 'GET':
        keyword = request.GET.get('keyword')
        sort = request.GET.get('sort')
        category = Category.objects.get(pk=sort)
        books = Book.objects.filter(Q(name__icontains=keyword.lower()) | Q(description__icontains=keyword.lower()) | Q(author__name__icontains=keyword.lower())).filter(category=category)
        
        user = {'username':'unknown', 'first_name':'unknown', 'last_name':'person', 'unknown':True}
        if request.user.is_authenticated:
            user = request.user

        categories = Category.objects.all()

        return render(request, 'search.html', {'user':user, 'books':books, 'keyword':keyword, 'sort':sort, 'target':'categories', 'categories':categories})
    return redirect('home')


def search(request):
    if request.method == 'GET':
        keyword = request.GET.get('keyword')
        sort = request.GET.get('sort')
        books = []
        if sort == 'date':
            books = Book.objects.filter(Q(name__icontains=keyword.lower()) | Q(description__icontains=keyword.lower()) | Q(category__name__icontains=keyword.lower()) | Q(author__name__icontains=keyword.lower())).order_by('-date')
        else:
            books = Book.objects.filter(Q(name__icontains=keyword.lower()) | Q(description__icontains=keyword.lower()) | Q(category__name__icontains=keyword.lower()) | Q(author__name__icontains=keyword.lower()))
        
        if sort == 'rating':
            books = sorted(books, key=lambda t: t.rating, reverse=True)
        elif sort == 'reads':
            books = sorted(books, key=lambda t: t.reads_count, reverse=True)
        user = {'username':'unknown', 'first_name':'unknown', 'last_name':'person', 'unknown':True}
        if request.user.is_authenticated:
            user = request.user
        return render(request, 'search.html', {'user':user, 'books':books, 'keyword':keyword, 'sort':sort, 'target':'all'})
    return redirect('home')


@login_required(login_url='/login')
def library_search(request):
    if request.method == 'GET':
        keyword = request.GET.get('keyword')
        sort = request.GET.get('sort')
        books = []
        if sort == 'date':
            books = Library.objects.filter(Q(book__name__icontains=keyword.lower()) | Q(book__description__icontains=keyword.lower()) | Q(book__category__name__icontains=keyword.lower()) | Q(book__author__name__icontains=keyword.lower())).order_by('-date')
        else:
            books = Library.objects.filter(Q(book__name__icontains=keyword.lower()) | Q(book__description__icontains=keyword.lower()) | Q(book__category__name__icontains=keyword.lower()) | Q(book__author__name__icontains=keyword.lower()))
        
        if sort == 'rating':
            books = sorted(books, key=lambda t: t.book.rating, reverse=True)
        elif sort == 'reads':
            books = sorted(books, key=lambda t: t.book.reads_count, reverse=True)
        return render(request, 'search.html', {'user':request.user, 'library_books':books, 'keyword':keyword, 'sort':sort, 'target':'library'})
    return redirect('home')


@login_required(login_url='/login')
def library(request):
    library_books = Library.objects.filter(user=request.user).order_by('-date', '-id')
    return render(request, 'library.html', {'user':request.user, 'library_books':library_books})


@login_required(login_url='/login')
def read(request, id):
    page_number = 1
    book = Book.objects.get(pk=id)
    try:
        book_read = BookRead.objects.get(user=request.user, book=book)
        page_number = book_read.page
    except:
        book_read = BookRead(user=request.user, book=book, page=page_number)
        book_read.save()
    page = get_page(book, page_number)
    return render(request, 'read.html', {'image':page.decode('utf-8'), 'book_name':book.name, 'book_author':book.author, 'page_number':page_number, 'book_id':book.pk, 'total_page':book.pages})


def authors(request):
    authors = Author.objects.all().order_by('-id')
    user = {'username':'unknown', 'first_name':'unknown', 'last_name':'person', 'unknown':True}
    if request.user.is_authenticated:
        user = request.user
    return render(request, 'authors.html', {'authors':authors, 'user':user})


@login_required(login_url='/login')
def add_to_library(request):
    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        added = False
        book = Book.objects.get(pk=book_id)
        try:
            library = Library.objects.get(book=book, user=request.user)
            library.delete()
        except:
            library = Library(book=book, user=request.user)
            library.save()
            added = True
        
        data = {
            'added': added,
        }
        return JsonResponse(data)
    return redirect('home')


@login_required(login_url='/login')
def follow_author(request):
    if request.method == 'POST':
        author_id = request.POST.get('author_id')
        author = Author.objects.get(pk=author_id)
        added = False
        try:
            follow = Follow.objects.get(author=author, user=request.user)
            follow.delete()
        except:
            follow = Follow(author=author, user=request.user)
            follow.save()
            added = True
        
        data = {
            'added': added,
        }
        return JsonResponse(data)
    return redirect('home')

@login_required(login_url='/login')
def remove_from_library(request):
    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        removed = False
        book = Book.objects.get(pk=book_id)
        try:
            library = Library.objects.get(book=book, user=request.user)
            library.delete()
            removed = True
        except:
            pass
        
        data = {
            'removed': removed,
        }
        return JsonResponse(data)
    return redirect('home')

@login_required(login_url='/login')
def get_next_page(request):
    if request.method == 'GET':
        book_id = request.GET.get('book_id')
        page_number = int(request.GET.get('page_num'))
        total_page = int(request.GET.get('total_page'))
        book = Book.objects.get(pk=book_id)
        if not page_number == total_page:
            page_number = page_number + 1
        page = get_page(book, page_number)
        book_read = BookRead.objects.get(user=request.user, book=book)
        book_read.page = page_number
        if page_number == total_page:
            book_read.completed = True
        book_read.save()
        data = {
            'page': page.decode('utf-8'),
            'page_number': page_number,
        }
        return JsonResponse(data)
    return redirect('home')

@login_required(login_url='/login')
def get_prev_page(request):
    if request.method == 'GET':
        book_id = request.GET.get('book_id')
        page_number = int(request.GET.get('page_num'))
        if not page_number  == 1:
            page_number = page_number - 1
        book = Book.objects.get(pk=book_id)
        page = get_page(book, page_number)
        book_read = BookRead.objects.get(user=request.user, book=book)
        book_read.page = page_number
        book_read.save()
        data = {
            'page': page.decode('utf-8'),
            'page_number': page_number,
        }
        return JsonResponse(data)
    return redirect('home')

@login_required(login_url='/login')
def get_first_page(request):
    if request.method == 'GET':
        book_id = request.GET.get('book_id')
        page_number = 1
        book = Book.objects.get(pk=book_id)
        page = get_page(book, page_number)
        book_read = BookRead.objects.get(user=request.user, book=book)
        book_read.page = page_number
        book_read.save()
        data = {
            'page': page.decode('utf-8'),
            'page_number': page_number,
        }
        return JsonResponse(data)
    return redirect('home')

@login_required(login_url='/login')
def go_to_page(request):
    if request.method == 'GET':
        book_id = request.GET.get('book_id')
        page_number = int(request.GET.get('go_to'))
        total_page = int(request.GET.get('total_page'))
        if total_page < page_number:
            data = {
                'success': False,
            }
            return JsonResponse(data)
        book = Book.objects.get(pk=book_id)
        page = get_page(book, page_number)
        book_read = BookRead.objects.get(user=request.user, book=book)
        book_read.page = page_number
        if page_number == total_page:
            book_read.completed = True
        book_read.save()
        data = {
            'success': True,
            'page': page.decode('utf-8'),
            'page_number': page_number,
        }
        return JsonResponse(data)
    return redirect('home')

@login_required(login_url='/login')
def get_last_page(request):
    if request.method == 'GET':
        book_id = request.GET.get('book_id')
        total_page = int(request.GET.get('total_page'))
        book = Book.objects.get(pk=book_id)
        page = get_page(book, total_page)
        book_read = BookRead.objects.get(user=request.user, book=book)
        book_read.completed = True
        book_read.page = total_page
        book_read.save()
        data = {
            'page': page.decode('utf-8'),
            'page_number': total_page,
        }
        return JsonResponse(data)
    return redirect('home')


def get_page(book, page_num):
    images = convert_from_path(book.book.path, 100, first_page=page_num, last_page=page_num)
    page = ''
    for image in images:
        buffer = BytesIO()
        image.save(buffer, "PNG")
        page = base64.b64encode(buffer.getvalue())
    return page