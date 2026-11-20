from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),                 # signup/, profile/
    path("accounts/", include("django.contrib.auth.urls")),      # login/, logout/
    path("", include("dashboard.urls")),                         # dashboard
    path("", include("collection.urls")),                        # collection, search, want list
]
