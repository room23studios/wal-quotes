from django.contrib import admin
from .models import Quote, Daily


def accept(modeladmin, request, queryset):
    queryset.update(accepted=True)
accept.short_description = "Accepts selected quotes"

@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    actions_on_top = True
    list_display = ('text', 'date', 'annotation', 'accepted')
    list_filter = ('accepted',)
    actions = [accept]


admin.site.register(Daily)