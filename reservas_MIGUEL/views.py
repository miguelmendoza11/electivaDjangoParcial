from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Reserva

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    return render(request, 'registration/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    es_admin = request.user.is_staff
    return render(request, 'reservas/dashboard.html', {'es_admin': es_admin})

# LISTAR reservas
class ReservaListView(LoginRequiredMixin, ListView):
    model = Reserva
    template_name = 'reservas/lista_reservas.html'
    context_object_name = 'reservas'

    def get_queryset(self):
        if self.request.user.is_staff:
            return Reserva.objects.all()
        return Reserva.objects.filter(usuario=self.request.user)

# CREAR reserva
class ReservaCreateView(LoginRequiredMixin, CreateView):
    model = Reserva
    template_name = 'reservas/form_reserva.html'
    fields = ['laboratorio', 'fecha', 'hora_inicio', 'hora_fin', 'motivo']
    success_url = reverse_lazy('lista_reservas')

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        # Validar conflicto de horarios
        nueva = form.instance
        conflicto = Reserva.objects.filter(
            laboratorio=nueva.laboratorio,
            fecha=nueva.fecha,
            estado='aprobada'
        ).filter(
            hora_inicio__lt=nueva.hora_fin,
            hora_fin__gt=nueva.hora_inicio
        ).exists()
        if conflicto:
            form.add_error(None, 'Ya existe una reserva aprobada en ese horario para ese laboratorio.')
            return self.form_invalid(form)
        return super().form_valid(form)

# EDITAR reserva
class ReservaUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Reserva
    template_name = 'reservas/form_reserva.html'
    fields = ['laboratorio', 'fecha', 'hora_inicio', 'hora_fin', 'motivo']
    success_url = reverse_lazy('lista_reservas')

    def test_func(self):
        reserva = self.get_object()
        return reserva.usuario == self.request.user and reserva.estado == 'pendiente'

# ELIMINAR reserva
class ReservaDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Reserva
    template_name = 'reservas/confirmar_eliminar.html'
    success_url = reverse_lazy('lista_reservas')

    def test_func(self):
        reserva = self.get_object()
        return reserva.usuario == self.request.user and reserva.estado == 'pendiente'

# CAMBIAR ESTADO (solo admin)
@login_required
def cambiar_estado(request, pk):
    if not request.user.is_staff:
        return redirect('lista_reservas')
    reserva = get_object_or_404(Reserva, pk=pk)
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in ['aprobada', 'rechazada']:
            reserva.estado = nuevo_estado
            reserva.save()
    return redirect('lista_reservas')