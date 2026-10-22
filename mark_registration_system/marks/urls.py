from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('input_marks/', views.input_marks, name='input_marks'),
    path('update_marks/', views.update_marks, name='update_marks'),
    path('view_marks/', views.view_marks, name='view_marks'),
    path('visualization/', views.visualization, name='visualization'),
]

# Serve media files in development (not for production use)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)