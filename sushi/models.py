from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

# Categoría de Cliente
class CategoriaCliente(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

# Usuario personalizado con teléfono
class Usuario(AbstractUser):
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)  # ✅ nuevo campo
    categoria_cliente = models.ForeignKey(CategoriaCliente, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.username

# Producto de catálogo
class CategoriaProducto(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='imagenes/productos/', blank=True, null=True)
    categoria_producto = models.ForeignKey(CategoriaProducto, on_delete=models.CASCADE)
    categoria_cliente = models.ForeignKey(CategoriaCliente, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

# Solicitud de compra
class Venta(models.Model):
    folio = models.CharField(max_length=20, unique=True, blank=True, null=True)
    fecha = models.DateTimeField(default=timezone.localtime)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    productos = models.TextField()
    nombre_cliente = models.CharField(max_length=100)
    email_cliente = models.EmailField()
    telefono_cliente = models.CharField(max_length=20, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    def __str__(self):
        return f"Pedido #{self.id} de {self.nombre_cliente} ({self.fecha.strftime('%Y-%m-%d')})"
