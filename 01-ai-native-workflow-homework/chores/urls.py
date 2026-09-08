from django.urls import path
from . import views

app_name = 'chores'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('chores/', views.ChoreListView.as_view(), name='chore_list'),
    path('chores/new/', views.ChoreCreateView.as_view(), name='chore_create'),
    path('chores/<int:pk>/edit/', views.ChoreUpdateView.as_view(), name='chore_edit'),
    path('chores/<int:pk>/delete/', views.ChoreDeleteView.as_view(), name='chore_delete'),
    path('occurrences/<int:pk>/complete/', views.mark_completed, name='mark_completed'),
    path('occurrences/<int:pk>/validate/', views.validate_chore, name='validate_chore'),
]
