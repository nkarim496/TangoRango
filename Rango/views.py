from django.http import HttpResponse
from django.shortcuts import render
from Rango.models import Category, Page

def index(request):
    categories_list = Category.objects.order_by('-likes')[:5]
    context = {'categories': categories_list}

    # top five most viewed pages
    top_five_pages = Page.objects.order_by('-views')[:5]
    context["top_five_pages"] = top_five_pages
    return render(request, 'rango/index.html', context=context)

def about(request):
    return render(request, 'rango/about.html')

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
