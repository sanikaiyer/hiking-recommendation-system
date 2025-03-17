from django.urls import path
from . import views

urlpatterns = [
    path('', views.trail_list, name='trail_list'),  # To list all trails
    path('<int:trail_id>/', views.trail_detail, name='trail_detail'),  # For trail details
    path('recommendation/', views.recommendation_view, name='recommendation'),
    
]
