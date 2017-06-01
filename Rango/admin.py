from django.contrib import admin
from Rango.models import Category, Page, UserProfile


class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'url', 'views')


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug', 'views', 'likes')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(UserProfile)
