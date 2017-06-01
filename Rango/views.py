from Rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.shortcuts import render
from Rango.models import Category, Page
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from datetime import datetime


def get_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


def visitor_cookie_handler(request):
    visits = int(get_cookie(request, 'visits', '1'))
    last_visit_cookie = get_cookie(request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], "%Y-%m-%d %H:%M:%S")
    if (datetime.now() - last_visit_time).seconds > 0:
        visits += 1
        request.session['last_visit'] = str(datetime.now())
    else:
        visits = 1
        request.session['last_visit'] = last_visit_cookie
    request.session['visits'] = visits


def index(request):
    categories_list = Category.objects.order_by('-likes')[:5]
    context = {'categories': categories_list}

    # top five most viewed pages
    top_five_pages = Page.objects.order_by('-views')[:5]
    context["top_five_pages"] = top_five_pages

    visitor_cookie_handler(request)
    context['last_visit'] = request.session['last_visit']
    response = render(request, 'Rango/index.html', context=context)
    return response


def about(request):
    last_visit = request.session['last_visit'][:-7]
    context = {'last_visit': last_visit}
    return render(request, 'rango/about.html', context)


def show_category(request, category_name_slug):
    context = {}
    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category)
        context['category'] = category
        context['pages'] = pages
    except Category.DoesNotExist:
        context['category'] = None
        context['pages'] = None
    return render(request, 'rango/category.html', context)


def add_category(request):
    form = CategoryForm()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return index(request)
    else:
        print(form.errors)
    return render(request, "Rango/add_category.html", {'form': form})


@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    form = PageForm()
    if request.method == "POST":
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return show_category(request, category_name_slug)
        else:
            print(form.errors)
    context = {'category': category, 'form': form}
    return render(request, 'Rango/add_page.html', context)


def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            profile.save()
            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    return render(request, 'Rango/register.html', {'user_form': user_form,
                                                   'profile_form': profile_form,
                                                   'registered': registered})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse("Your account is not active")
        else:
            print("Invalid login details {} and {}".format(username, password))
            return HttpResponse("Invalid login details supplied")
    else:
        return render(request, 'Rango/login.html', {})


@login_required
def restricted(request):
    return HttpResponse("%s, welcome to Darkside" % request.user)


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))
