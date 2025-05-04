from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from decimal import Decimal
from .models import Usuario, Producto, Venta, CategoriaCliente
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import Producto, CategoriaProducto
from django.template.loader import render_to_string
from xhtml2pdf import pisa # type: ignore
from io import BytesIO
from django.core.mail import EmailMessage
import random
import string
from django.db.models import Q
from django.core.paginator import Paginator



def generar_folio_alfanumerico(longitud=6):
    caracteres = string.ascii_uppercase + string.digits
    return ''.join(random.choices(caracteres, k=longitud))



# ======= AUTENTICACIÓN =======

def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {"form": AuthenticationForm})
    else:
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('catalogo')

        return render(request, 'signin.html', {"form": AuthenticationForm, "error": "Usuario o contraseña incorrectos."})

def signout(request):
    logout(request)
    messages.success(request, "Sesión cerrada correctamente.")
    return redirect('signin')

def home(request):
    return render(request, 'home.html')



# ======= CATÁLOGO Y CARRITO =======

from django.core.paginator import Paginator
...

@login_required
def catalogo(request):
    query = request.GET.get('q', '')
    categoria_id = request.GET.get('categoria', '')
    page = request.GET.get('page')

    # Filtrado base
    if request.user.categoria_cliente and request.user.categoria_cliente.nombre.lower() == "admin":
        productos_qs = Producto.objects.all()
    else:
        productos_qs = Producto.objects.filter(categoria_cliente=request.user.categoria_cliente)

    # Filtros aplicados
    if query:
        productos_qs = productos_qs.filter(nombre__icontains=query)

    if categoria_id:
        productos_qs = productos_qs.filter(categoria_producto_id=categoria_id)

    paginator = Paginator(productos_qs, 6)
    productos = paginator.get_page(page)

    categorias = CategoriaProducto.objects.all()

    return render(request, 'catalogo.html', {
        "productos": productos,
        "categorias": categorias,
        "query": query,
        "categoria_seleccionada": categoria_id
    })



@login_required
def carrito(request):
    cart = request.session.get('cart', {})
    productos = Producto.objects.filter(id__in=cart.keys())

    carrito_items = []
    total = Decimal("0.00")

    for producto in productos:
        cantidad = cart.get(str(producto.id), 0)
        subtotal = Decimal(producto.precio) * cantidad
        carrito_items.append({
            "producto": producto,
            "cantidad": cantidad,
            "subtotal": subtotal
        })
        total += subtotal

    return render(request, 'carrito.html', {
        "carrito_items": carrito_items,
        "total": total
    })

@login_required
def agregar_al_carrito(request, producto_id):
    cart = request.session.get('cart', {})
    cart[str(producto_id)] = cart.get(str(producto_id), 0) + 1
    request.session['cart'] = cart
    return JsonResponse({"message": "Producto agregado al carrito", "cart": cart})

@csrf_exempt
@login_required
def eliminar_del_carrito(request, producto_id):
    if request.method == "POST":
        cart = request.session.get('cart', {})
        if str(producto_id) in cart:
            del cart[str(producto_id)]
            request.session['cart'] = cart
            request.session.modified = True
        return JsonResponse({"message": "Producto eliminado del carrito", "cart": cart})
    return JsonResponse({"message": "Método no permitido"}, status=405)


@login_required
def obtener_conteo_carrito(request):
    cart = request.session.get('cart', {})
    total_items = sum(cart.values())
    return JsonResponse({"total_items": total_items})

@csrf_exempt
@login_required
def actualizar_cantidad_carrito(request, producto_id):
    if request.method == "POST":
        cart = request.session.get("cart", {})
        nueva_cantidad = int(request.POST.get("cantidad", 1))

        if nueva_cantidad <= 0:
            cart.pop(str(producto_id), None)
        else:
            cart[str(producto_id)] = nueva_cantidad

        request.session["cart"] = cart
        request.session.modified = True

        return JsonResponse({"message": "Carrito actualizado correctamente", "cart": cart})
    return JsonResponse({"message": "Método no permitido"}, status=405)

# ======= PROCESAR SOLICITUD =======
@login_required
def enviar_solicitud_compra(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        if not cart:
            return JsonResponse({"error": "El carrito está vacío."}, status=400)

        productos = Producto.objects.filter(id__in=cart.keys())
        total = Decimal("0.00")
        productos_texto = ""
        carrito_pdf = []

        for producto in productos:
            cantidad = cart.get(str(producto.id), 0)
            subtotal = Decimal(producto.precio) * cantidad
            productos_texto += f"{cantidad}x {producto.nombre} - ${subtotal}\n"
            total += subtotal

            carrito_pdf.append({
                "nombre": producto.nombre,
                "cantidad": cantidad,
                "subtotal": subtotal
            })

        # Generar folio alfanumérico único
        def generar_folio_alfanumerico(longitud=6):
            caracteres = string.ascii_uppercase + string.digits
            return ''.join(random.choices(caracteres, k=longitud))

        while True:
            codigo = generar_folio_alfanumerico()
            folio_generado = codigo
            if not Venta.objects.filter(folio=folio_generado).exists():
                break

        # Guardar en base de datos
        venta = Venta.objects.create(
            usuario=request.user,
            nombre_cliente=request.user.username,
            email_cliente=request.user.email,
            telefono_cliente=request.user.telefono or "N/A",
            observaciones="Solicitud de compra enviada desde el sistema",
            productos=productos_texto,
            total=total,
            folio=folio_generado
        )

        # Generar PDF
        template_path = 'venta_pdf.html'
        context = {
            'folio': folio_generado,
            'nombre_cliente': request.user.username,
            'email_cliente': request.user.email,
            'telefono_cliente': request.user.telefono or "N/A",
            'carrito': carrito_pdf,
            'total': total
        }

        html = render_to_string(template_path, context)
        pdf_file = BytesIO()
        pisa_status = pisa.CreatePDF(html, dest=pdf_file)

        if pisa_status.err:
            return JsonResponse({"error": "Error al generar PDF."}, status=500)

        pdf_file.seek(0)

        destinatario = getattr(settings, 'EMAIL_SOLICITUD_DESTINO', settings.DEFAULT_FROM_EMAIL)

        email = EmailMessage(
            subject=f"Solicitud {folio_generado} de {request.user.username}",
            body=(
                f"Folio: {folio_generado}\n"
                f"Usuario: {request.user.username}\n"
                f"Correo: {request.user.email}\n"
                f"Teléfono: {request.user.telefono or 'N/A'}\n"
                f"Categoría: {request.user.categoria_cliente.nombre if request.user.categoria_cliente else 'No especificada'}\n\n"
                f"Productos solicitados:\n{productos_texto}\n"
                f"Total: ${total}\n"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[destinatario],
        )

        email.attach(f"{folio_generado}.pdf", pdf_file.read(), 'application/pdf')
        email.send()

        request.session['cart'] = {}
        request.session.modified = True

        return JsonResponse({"message": "Solicitud enviada correctamente.", "venta_id": venta.id})

    return JsonResponse({"message": "Método no permitido"}, status=405)


# ======= OBTENER TOTAL DEL CARRITO =======

@login_required
def obtener_total_carrito(request):
    cart = request.session.get("cart", {})
    productos = Producto.objects.filter(id__in=cart.keys())

    total = 0
    carrito_items = []

    for producto in productos:
        cantidad = cart.get(str(producto.id), 0)
        subtotal = float(producto.precio) * cantidad
        total += subtotal
        carrito_items.append({
            "producto_id": producto.id,
            "subtotal": subtotal
        })

    return JsonResponse({
        "total": total,
        "items": carrito_items
    })



# Requiere ser admin (por categoría_cliente)
def solo_admin(func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.categoria_cliente and request.user.categoria_cliente.nombre.lower() == "admin":
            return func(request, *args, **kwargs)
        messages.error(request, "Acceso no autorizado.")
        return redirect("catalogo")
    return login_required(_wrapped_view)

@solo_admin
def crud_usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'crud_usuarios.html', {'usuarios': usuarios})

@solo_admin
def crear_usuario(request):
    categorias = CategoriaCliente.objects.all()

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        telefono = request.POST.get('telefono', '')
        categoria_id = request.POST['categoria_cliente']

        if Usuario.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya existe.")
        else:
            categoria = get_object_or_404(CategoriaCliente, pk=categoria_id)
            nuevo_usuario = Usuario(
                username=username,
                email=email,
                telefono=telefono,
                categoria_cliente=categoria
            )
            nuevo_usuario.set_password(password)
            nuevo_usuario.save()
            messages.success(request, "Usuario creado correctamente.")
            return redirect('crud_usuarios')

    return render(request, 'crear_usuario.html', {'categorias': categorias})



@solo_admin
def editar_usuario(request, user_id):
    usuario = get_object_or_404(Usuario, id=user_id)
    categorias = CategoriaCliente.objects.all()

    if request.method == 'POST':
        usuario.username = request.POST['username']
        usuario.email = request.POST['email']
        usuario.telefono = request.POST.get('telefono', '')
        usuario.categoria_cliente = get_object_or_404(CategoriaCliente, pk=request.POST['categoria_cliente'])

        if request.POST['password']:
            usuario.set_password(request.POST['password'])

        usuario.save()
        messages.success(request, "Usuario actualizado correctamente.")
        return redirect('crud_usuarios')

    return render(request, 'editar_usuario.html', {
        'usuario': usuario,
        'categorias': categorias
    })

@solo_admin
def eliminar_usuario(request, user_id):
    usuario = get_object_or_404(Usuario, id=user_id)
    if usuario.username != request.user.username:
        usuario.delete()
        messages.success(request, "Usuario eliminado correctamente.")
    else:
        messages.error(request, "No puedes eliminar tu propio usuario.")
    return redirect('crud_usuarios')

@solo_admin
def crud_productos(request):
    productos = Producto.objects.all()
    return render(request, 'crud_productos.html', {'productos': productos})

@solo_admin
def crear_producto(request):
    categorias_producto = CategoriaProducto.objects.all()
    categorias_cliente = CategoriaCliente.objects.all()

    if request.method == 'POST':
        nombre = request.POST['nombre']
        descripcion = request.POST['descripcion']
        precio = request.POST['precio']
        categoria_producto = get_object_or_404(CategoriaProducto, pk=request.POST['categoria_producto'])
        categoria_cliente = get_object_or_404(CategoriaCliente, pk=request.POST['categoria_cliente'])
        imagen = request.FILES.get('imagen')

        Producto.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            categoria_producto=categoria_producto,
            categoria_cliente=categoria_cliente,
            imagen=imagen
        )
        messages.success(request, "Producto creado correctamente.")
        return redirect('catalogo')

    return render(request, 'crear_producto.html', {
        'categorias_producto': categorias_producto,
        'categorias_cliente': categorias_cliente
    })

@solo_admin
def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    categorias_producto = CategoriaProducto.objects.all()
    categorias_cliente = CategoriaCliente.objects.all()

    if request.method == 'POST':
        producto.nombre = request.POST['nombre']
        producto.descripcion = request.POST['descripcion']
        producto.precio = request.POST['precio']
        producto.categoria_producto = get_object_or_404(CategoriaProducto, pk=request.POST['categoria_producto'])
        producto.categoria_cliente = get_object_or_404(CategoriaCliente, pk=request.POST['categoria_cliente'])
        if request.FILES.get('imagen'):
            producto.imagen = request.FILES['imagen']
        producto.save()
        messages.success(request, "Producto actualizado correctamente.")
        return redirect('catalogo')

    return render(request, 'editar_producto.html', {
        'producto': producto,
        'categorias_producto': categorias_producto,
        'categorias_cliente': categorias_cliente
    })

@solo_admin
def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    producto.delete()
    messages.success(request, "Producto eliminado correctamente.")
    return redirect('catalogo')

@login_required
def ver_ventas(request):
    query = request.GET.get("q", "")
    ventas = Venta.objects.all()

    if request.user.categoria_cliente and request.user.categoria_cliente.nombre.lower() != "admin":
        ventas = ventas.filter(usuario=request.user)
    
    if query:
        ventas = ventas.filter(
            Q(nombre_cliente__icontains=query) |
            Q(telefono_cliente__icontains=query) |
            Q(folio__icontains=query.upper())

        )

    ventas = ventas.order_by('-fecha')
    return render(request, 'ventas.html', {"ventas": ventas, "query": query})

@login_required
def editar_venta(request, venta_id):
    if not request.user.categoria_cliente or request.user.categoria_cliente.nombre.lower() != "admin":
        return redirect('ver_ventas')

    venta = get_object_or_404(Venta, id=venta_id)

    if request.method == "POST":
        venta.nombre_cliente = request.POST.get("nombre_cliente")
        venta.telefono_cliente = request.POST.get("telefono_cliente")
        venta.email_cliente = request.POST.get("email_cliente")
        venta.observaciones = request.POST.get("observaciones")
        venta.save()
        messages.success(request, "Venta actualizada correctamente.")
        return redirect('ver_ventas')

    return render(request, 'editar_venta.html', {'venta': venta})

@login_required
def eliminar_venta(request, venta_id):
    if not request.user.categoria_cliente or request.user.categoria_cliente.nombre.lower() != "admin":
        return redirect('ver_ventas')

    venta = get_object_or_404(Venta, id=venta_id)
    venta.delete()
    messages.success(request, "Venta eliminada correctamente.")
    return redirect('ver_ventas')




@login_required
def detalle_venta(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)

    # Verificación: solo el dueño o un admin puede verla
    if request.user != venta.usuario and (not request.user.categoria_cliente or request.user.categoria_cliente.nombre.lower() != "admin"):
        return redirect('ver_ventas')

    # Parsear los productos desde el campo de texto
    productos = []
    for linea in venta.productos.strip().split("\n"):
        if "x" in linea and " - $" in linea:
            partes = linea.split("x")
            cantidad = partes[0].strip()
            nombre_y_precio = partes[1].split(" - $")
            nombre = nombre_y_precio[0].strip()
            subtotal = nombre_y_precio[1].strip()
            productos.append({
                "nombre": nombre,
                "cantidad": cantidad,
                "subtotal": subtotal
            })

    return render(request, 'detalle_venta.html', {
        "venta": venta,
        "productos": productos
    })


@solo_admin
def detalle_usuario(request, user_id):
    usuario = get_object_or_404(Usuario, id=user_id)
    return render(request, 'detalle_usuario.html', {'usuario': usuario})

@login_required
def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    return render(request, 'detalle_producto.html', {'producto': producto})


