from django.contrib import admin
from .models import *


admin.site.register(Producto)
admin.site.register(CategoriaProducto)
admin.site.register(Venta)
admin.site.register(CategoriaCliente)
admin.site.register(Usuario)