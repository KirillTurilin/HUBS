from django.urls import path
from . import views

app_name = 'friends'

urlpatterns = [
    path('', views.search_view, name='search'),
    path('request/send/<int:user_id>/', views.send_friend_request, name='send_request'),
    path('request/respond/<int:request_id>/', views.respond_to_friend_request, name='respond_request'),
    path('remove/<int:user_id>/', views.remove_friend, name='remove_friend'),
] 