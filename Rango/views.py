from Rango.forms import CategoryForm, PageForm, UserProfileForm
from django.shortcuts import render, redirect, get_object_or_404
from Rango.models import Category, Page, UserProfile
from django.contrib.auth.decorators import login_required
from datetime import datetime
from Rango.bing_search import run_query
from django.contrib.auth.models import User
from django.http import HttpResponse


def get_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


def get_category_list(max_results=0, starts_with=''):
    cat_list = []
    if starts_with:
        cat_list = Category.objects.filter(name__istartswith=starts_with)
    if max_results > 0:
        if len(cat_list) > max_results:
            cat_list = cat_list[:max_results]
    return cat_list


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
    return render(request, 'Rango/about.html', context)


def show_category(request, category_name_slug):
    context = {}
    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category).order_by('-views')
        context['category'] = category
        context['pages'] = pages
        context['query'] = category.name
    except Category.DoesNotExist:
        context['category'] = None
        context['pages'] = None
    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            result_list = run_query(query)
            context['query'] = query
            context['result_list'] = result_list
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


def track_url(request, page_id):
    page = get_object_or_404(Page, pk=page_id)
    page.views += 1
    page.save()
    return redirect(page.url)


@login_required
def register_profile(request):
    form = UserProfileForm()
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()
            return redirect('index')
        else:
            print(form.errors)
    return render(request, 'Rango/profile_registration.html', {'form': form})


@login_required
def profile(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return redirect('index')
    userprofile = UserProfile.objects.get_or_create(user=user)[0]
    form = UserProfileForm({'website': userprofile.website, 'picture': userprofile.picture})
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if form.is_valid():
            form.save(commit=True)
            return redirect('rango:profile', user.username)
        else:
            print(form.errors)
    return render(request, 'Rango/profile.html', {'userprofile': userprofile,
                                                  'selecteduser': user,
                                                  'form': form})


@login_required
def list_profiles(request):
    userprofile_list = UserProfile.objects.all()
    return render(request, 'Rango/list_profiles.html', {'userprofile_list': userprofile_list})


@login_required
def like_category(request):
    likes = None
    if request.method == "GET":
        cat_id = request.GET['category_id']
        likes = 0
        if cat_id:
            cat = Category.objects.get(pk=int(cat_id))
            if cat:
                likes = cat.likes + 1
                cat.likes = likes
                cat.save()
    return HttpResponse(likes)


def suggest_category(request):
    starts_with = ''
    if request.method == 'GET':
        starts_with = request.GET['suggestion']
    cat_list = get_category_list(8, starts_with)
    return render(request, 'Rango/cats.html', {'cats': cat_list})


@login_required
def auto_add_category(request):
    if request.method == 'GET':
        cat_id = request.GET['category_id']
        url = request.GET['url']
        title = request.GET['title']
        if cat_id:
            category = Category.objects.get(pk=int(cat_id))
            p = Page.objects.get_or_create(category=category, title=title, url=url)
            pages = Page.objects.filter(category=category).order_by('-views')
    return render(request, 'Rango/page_list.html', {'pages': pages})
