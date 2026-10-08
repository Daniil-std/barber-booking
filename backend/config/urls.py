from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "FORM — Studio administration"
admin.site.site_title = "FORM Admin"
admin.site.index_title = "Studio management"

urlpatterns = [path("admin/", admin.site.urls), path("api/", include("studio.urls"))]
