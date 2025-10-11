from django.urls import path
from . import views

app_name = "projects"

urlpatterns = [
    path("", views.ProjectListView.as_view(), name="project_list"),
    path("featured/", views.FeaturedProjectListView.as_view(), name="featured_project_list"),
    path("<slug:slug>/", views.ProjectDetailView.as_view(), name="project_detail"),
    path("category/<slug:slug>/", views.CategoryDetailView.as_view(), name="category_detail"),
    path("technology/<slug:slug>/", views.TechnologyDetailView.as_view(), name="technology_detail"),
]