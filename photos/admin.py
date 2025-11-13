from django.contrib import admin
from .models import Photo, Photographer


@admin.register(Photographer)
class PhotographerAdmin(admin.ModelAdmin):
    list_display = ["id", "photographer_id", "name", "photo_count"]
    search_fields = ["name", "photographer_id"]
    readonly_fields = ["photographer_id", "photo_count"]

    fieldsets = (
        (
            "Photographer Information",
            {"fields": ("photographer_id", "name", "url", "photo_count")},
        ),
    )

    def photo_count(self, obj):
        return obj.photo_count

    photo_count.short_description = "Number of Photos"


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "photo_id",
        "photographer",
        "width",
        "height",
        "avg_color",
    ]
    list_filter = ["photographer", "created_at"]
    search_fields = ["id", "photo_id", "photographer__name", "alt"]
    readonly_fields = ["id", "photo_id", "created_at", "updated_at"]
    autocomplete_fields = ["photographer"]

    fieldsets = (
        ("IDs", {"fields": ("id", "photo_id")}),
        (
            "Photo Information",
            {"fields": ("width", "height", "url", "avg_color", "alt", "photographer")},
        ),
        (
            "Metadata",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
