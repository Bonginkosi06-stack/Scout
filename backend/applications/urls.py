from django.urls import path

from .views import review_application


urlpatterns = [
    path("review/", review_application, name="review-application"),
]