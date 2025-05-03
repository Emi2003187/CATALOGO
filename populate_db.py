import os
import django
import random
from decimal import Decimal

# Inicializar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FoodTrackOrder.settings')
django.setup()

from sushi.models import CategoriaProducto, CategoriaCliente, Producto, Usuario

# 1. Crear Categorías de Productos
categorias_productos = [
    "Memorias RAM", "Tarjetas Madre", "Gabinetes", "Procesadores", "Discos Duros", "Fuentes de Poder"
]

for nombre in categorias_productos:
    CategoriaProducto.objects.get_or_create(nombre=nombre)

# 2. Crear Categorías de Clientes
categorias_clientes = [
    "Ferretería", "Clínica", "Empresa", "Admin"
]

for nombre in categorias_clientes:
    CategoriaCliente.objects.get_or_create(nombre=nombre)

# 3. Crear Productos repetidos por cliente
productos = [
    {
        "nombre": "Corsair Vengeance LPX 16GB DDR4",
        "descripcion": "Modelo: CMK16GX4M2B3200C16\nCapacidad: 16GB (2x8GB)\nVelocidad: 3200MHz\nTipo: DDR4\nColor: Negro",
        "precio_base": 1200.00,
        "categoria_producto": "Memorias RAM"
    },
    {
        "nombre": "ASUS ROG STRIX B550-F",
        "descripcion": "Modelo: B550-F\nSocket: AM4\nFormato: ATX\nCompatible: Ryzen 3000, 5000 series\nConectividad: PCIe 4.0, USB 3.2",
        "precio_base": 4200.00,
        "categoria_producto": "Tarjetas Madre"
    },
    {
        "nombre": "NZXT H510 Case",
        "descripcion": "Modelo: H510\nTipo: Mid Tower\nColor: Negro\nMaterial: Acero y Vidrio Templado\nCompatibilidad: ATX, Micro-ATX",
        "precio_base": 2000.00,
        "categoria_producto": "Gabinetes"
    },
    {
        "nombre": "Intel Core i5-12400F",
        "descripcion": "Modelo: BX8071512400F\nNúcleos: 6\nHilos: 12\nFrecuencia Base: 2.5GHz\nSocket: LGA1700",
        "precio_base": 3900.00,
        "categoria_producto": "Procesadores"
    },
    {
        "nombre": "Western Digital Blue 1TB HDD",
        "descripcion": "Modelo: WD10EZEX\nCapacidad: 1TB\nFormato: 3.5\"\nVelocidad: 7200 RPM\nInterfaz: SATA 6Gb/s",
        "precio_base": 750.00,
        "categoria_producto": "Discos Duros"
    },
    {
        "nombre": "Corsair CV550 550W 80+ Bronze",
        "descripcion": "Modelo: CP-9020210-NA\nPotencia: 550 Watts\nCertificación: 80 Plus Bronze\nFormato: ATX\nConectores: ATX, PCIe, SATA",
        "precio_base": 1050.00,
        "categoria_producto": "Fuentes de Poder"
    },
]

# Obtener todas las categorías de cliente y producto
clientes = CategoriaCliente.objects.all()
categorias_producto = {cp.nombre: cp for cp in CategoriaProducto.objects.all()}

# Crear productos para cada categoría de cliente con precio ajustado
for prod in productos:
    base_precio = prod["precio_base"]
    for cliente in clientes:
        precio_ajustado = base_precio * random.uniform(0.85, 1.25)
        Producto.objects.get_or_create(
            nombre=prod["nombre"],
            descripcion=prod["descripcion"],
            precio=Decimal(round(precio_ajustado, 2)),
            categoria_producto=categorias_producto[prod["categoria_producto"]],
            categoria_cliente=cliente
        )

# 4. Crear Usuario "Emiliong" si no existe
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

print("🎉 Base de datos poblada exitosamente con productos por categoría.")
