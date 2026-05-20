from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('reservas/', views.ReservaListView.as_view(), name='lista_reservas'),
    path('reservas/nueva/', views.ReservaCreateView.as_view(), name='crear_reserva'),
    path('reservas/<int:pk>/editar/', views.ReservaUpdateView.as_view(), name='editar_reserva'),
    path('reservas/<int:pk>/eliminar/', views.ReservaDeleteView.as_view(), name='eliminar_reserva'),
    path('reservas/<int:pk>/estado/', views.cambiar_estado, name='cambiar_estado'),
]