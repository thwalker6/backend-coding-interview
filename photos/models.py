from django.db import models


class Photographer(models.Model):
    photographer_id = models.IntegerField(db_index=True)
    name = models.CharField(db_index=True, max_length=200)
    url = models.URLField(max_length=500)

    class Meta:
        ordering = ["name"]
        verbose_name = "Photographer"
        verbose_name_plural = "Photographers"
        indexes = [
            models.Index(fields=["photographer_id"]),
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return f"{self.name} (ID: {self.photographer_id})"

    @property
    def photo_count(self):
        return self.photos.count()


class Photo(models.Model):
    photo_id = models.IntegerField(unique=True, db_index=True)
    width = models.IntegerField()
    height = models.IntegerField()
    url = models.URLField(max_length=500)
    src_url = models.URLField(max_length=500)

    photographer = models.ForeignKey(
        Photographer, on_delete=models.CASCADE, related_name="photos"
    )

    avg_color = models.CharField(max_length=7)
    alt = models.TextField(blank=False, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]
        verbose_name = "Photo"
        verbose_name_plural = "Photos"
        indexes = [
            models.Index(fields=["id"]),
            models.Index(fields=["photographer"]),
        ]

    def __str__(self):
        return f"Photo {self.alt} by {self.photographer.name}"

    # Making it a calculated field for the portrait and landscape URL so that our API has control over the size and dimensions.
    # Could even make it change the values from the property here instead
    @property
    def portrait_url(self):
        return self.src_url + "?auto=compress&cs=tinysrgb&fit=crop&h=1200&w=800"

    @property
    def landscape_url(self):
        return self.src_url + "?auto=compress&cs=tinysrgb&fit=crop&h=627&w=1200"

    @property
    def tiny_pic_url(self):
        return self.src_url + "?auto=compress&cs=tinysrgb&dpr=1&fit=crop&h=200&w=280"

    @property
    def extra_large_pic_url(self):
        return self.src_url + "?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"

    @property
    def large_pic_url(self):
        return self.src_url + "?auto=compress&cs=tinysrgb&h=650&w=940"

    @property
    def small_pic_url(self):
        return self.src_url + "?auto=compress&cs=tinysrgb&h=130"

    @property
    def medium_pic_url(self):
        return self.src_url + "?auto=compress&cs=tinysrgb&h=350"
