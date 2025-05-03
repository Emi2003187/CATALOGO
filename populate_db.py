import os
import django
import random
from decimal import Decimal
from django.core.files import File

# Inicializar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FoodTrackOrder.settings')
django.setup()

from sushi.models import CategoriaProducto, CategoriaCliente, Producto, Usuario

# Categorías principales
categorias_productos = ["Hardware", "Software"]
for nombre in categorias_productos:
    CategoriaProducto.objects.get_or_create(nombre=nombre)

# Categorías de cliente (Admin solo para usuarios)
categorias_clientes = ["Ferretería", "Clínica", "Empresa", "Admin"]
for nombre in categorias_clientes:
    CategoriaCliente.objects.get_or_create(nombre=nombre)

# Productos de Hardware
productos_hardware = [
    {
        "nombre": "Intel Core i5-12400F",
        "descripcion": "Núcleos: 6, Hilos: 12, Socket: LGA1700",
        "precio_base": 3900.00
    },
    {
        "nombre": "Corsair Vengeance 16GB DDR4",
        "descripcion": "Velocidad: 3200MHz, Tipo: DDR4",
        "precio_base": 1200.00
    }
]

# Productos de Software
productos_software = [
    {
        "nombre": "Microsoft Office 365",
        "descripcion": "Word, Excel, PowerPoint y más. Suscripción anual.",
        "precio_base": 1800.00
    },
    {
        "nombre": "Adobe Photoshop CC",
        "descripcion": "Edición profesional de imágenes. Licencia mensual.",
        "precio_base": 1500.00
    },
    {
        "nombre": "AutoCAD 2024",
        "descripcion": "Diseño 2D/3D para ingeniería y arquitectura.",
        "precio_base": 6500.00
    },
    {
        "nombre": "Antivirus Kaspersky",
        "descripcion": "Protección básica y avanzada para tu equipo.",
        "precio_base": 850.00
    }
]

# Obtener instancias necesarias
categoria_hw = CategoriaProducto.objects.get(nombre="Hardware")
categoria_sw = CategoriaProducto.objects.get(nombre="Software")
categorias_cliente = CategoriaCliente.objects.exclude(nombre__iexact="Admin")

# Rutas de imagen
img_hw_path = os.path.join("img_populate", "case.jpg")
img_sw_path = os.path.join("img_populate", "sw demo.png")

def obtener_imagen(ruta):
    if os.path.exists(ruta):
        return File(open(ruta, 'rb'))
    return None

# Insertar productos de hardware
for prod in productos_hardware:
    for cliente in categorias_cliente:
        precio = Decimal(round(prod["precio_base"] * random.uniform(0.9, 1.2), 2))
        producto, creado = Producto.objects.get_or_create(
            nombre=prod["nombre"],
            descripcion=prod["descripcion"],
            precio=precio,
            categoria_producto=categoria_hw,
            categoria_cliente=cliente
        )
        if creado:
            imagen = obtener_imagen(img_hw_path)
            if imagen:
                producto.imagen.save("case.jpg", imagen, save=True)

# Insertar productos de software
for prod in productos_software:
    for cliente in categorias_cliente:
        precio = Decimal(round(prod["precio_base"] * random.uniform(0.9, 1.2), 2))
        producto, creado = Producto.objects.get_or_create(
            nombre=prod["nombre"],
            descripcion=prod["descripcion"],
            precio=precio,
            categoria_producto=categoria_sw,
            categoria_cliente=cliente
        )
        if created := obtener_imagen(img_sw_path):
            producto.imagen.save("sw demo.png", created, save=True)

# Crear usuario Emiliong
admin_categoria = CategoriaCliente.objects.get(nombre="Admin")
usuario_emiliong, creado = Usuario.objects.get_or_create(
    username="Emiliong",
    defaults={
        "email": "emiliong@example.com",
        "telefono": "6641234567",
        "categoria_cliente": admin_categoria,
        "is_staff": True,
        "is_superuser": True
    }
)

if creado:
    usuario_emiliong.set_password('123456')
    usuario_emiliong.save()

print("🎉 Base de datos poblada exitosamente con imágenes y productos.")
