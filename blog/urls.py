from django.urls import path
from . import views

urlpatterns = [
    # Publik
    path('', views.post_list, name='post-list'),
    path('post/<int:pk>/', views.post_detail, name='post-detail'),
    path('kategori/', views.category_list, name='category-list'),
    
    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard & CRUD (perlu login)
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('post/buat/', views.post_create, name='post-create'),
    path('post/<int:pk>/edit/', views.post_update, name='post-update'),
    path('post/<int:pk>/hapus/', views.post_delete, name='post-delete'),
]