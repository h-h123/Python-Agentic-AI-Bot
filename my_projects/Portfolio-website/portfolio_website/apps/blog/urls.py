from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    path("", views.PostListView.as_view(), name="post_list"),
    path("<int:year>/<int:month>/<int:day>/<slug:slug>/",
         views.PostDetailView.as_view(), name="post_detail"),
    path("category/<slug:slug>/", views.CategoryDetailView.as_view(), name="category_detail"),
    path("tag/<slug:slug>/", views.TagDetailView.as_view(), name="tag_detail"),
    path("search/", views.PostSearchView.as_view(), name="post_search"),
]