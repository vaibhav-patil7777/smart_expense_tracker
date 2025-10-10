from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import toggle_block_user, view_all_users, user_dashboard
from expenseapp import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth
    path('login/', views.login_view, name='login'),  # ✅ Fixed
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('user-dashboard/<int:user_id>/', views.user_dashboard, name='user_dashboard'),

    # Expense Management
    path('edit/<int:expense_id>/', views.edit_expense, name='edit_expense'),
    path('delete/<int:expense_id>/', views.delete_expense, name='delete_expense'),
    path('set-budget/', views.set_budget, name='set_budget'),

    # Upload/Add Expense
    path('add/manual/', views.manual_expense_add, name='manual_expense_add'),
    path('add/file/', views.upload_expense_file, name='upload_expense_file'),
    path('add/voice/', views.save_voice_expense, name='save_voice_expense'),

    # Voice Page
    path('voice-expense/', views.voice_expense_page, name='voice_expense_page'),

    # Export
    path('download-csv/', views.download_csv, name='download_csv'),
    path('download-pdf/', views.download_pdf, name='download_pdf'),

    # Admin actions
    path('admin-approve/<int:user_id>/', views.approve_user, name='approve_user'),
    path('admin-login/<str:username>/<str:secret>/', views.admin_user_access, name='admin_user_access'),
    path('admin-users/', view_all_users, name='view_all_users'),

    # User actions
    path('toggle-user/<int:user_id>/', toggle_block_user, name='toggle_block_user'),
    path('users/', views.view_all_users, name='view_all_users'),
    path('user/<int:user_id>/dashboard/', views.view_user_dashboard, name='view_user_dashboard'),
    path('user/<int:user_id>/block/', views.block_user, name='block_user'),
    path('user/<int:user_id>/unblock/', views.unblock_user, name='unblock_user'),
]

# Media file serving
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
