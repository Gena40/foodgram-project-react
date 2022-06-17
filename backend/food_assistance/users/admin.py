from django.contrib import admin
from users.models import Follow, User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email'
    )
    filter_horizontal = ('favorite_recipes',)
    list_filter = ('email', 'username')
    empty_value_display = '-пусто-'


class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author'
    )
    search_fields = ('user', 'author')
    list_filter = ('author',)


admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
