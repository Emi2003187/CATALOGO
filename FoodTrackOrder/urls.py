"""
URL configuration for FoodTrackOrder project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from sushi import views
from sushi.views import actualizar_cantidad_carrito, carrito, agregar_al_carrito, eliminar_del_carrito, obtener_conteo_carrito, catalogo

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('signin/', views.signin, name='signin'),
    path('logout/', views.signout, name='logout'),
    path('catalogo/', views.catalogo, name='catalogo'),

    path('carrito/', views.carrito, name='carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/eliminar/<int:producto_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('carrito/actualizar/<int:producto_id>/', views.actualizar_cantidad_carrito, name='actualizar_cantidad_carrito'),
    path('carrito/conteo/', views.obtener_conteo_carrito, name='obtener_conteo_carrito'),
    path('carrito/obtener_total/', views.obtener_total_carrito, name='obtener_total_carrito'),
    path('carrito/enviar_solicitud/', views.enviar_solicitud_compra, name='enviar_solicitud_compra'), 


    path('crud/usuarios/', views.crud_usuarios, name='crud_usuarios'),
    path('crud/usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('crud/usuarios/editar/<int:user_id>/', views.editar_usuario, name='editar_usuario'),
    path('crud/usuarios/eliminar/<int:user_id>/', views.eliminar_usuario, name='eliminar_usuario'),


    path('crud/productos/', views.crud_productos, name='crud_productos'),
    path('crud/productos/crear/', views.crear_producto, name='crear_producto'),
    path('crud/productos/editar/<int:producto_id>/', views.editar_producto, name='editar_producto'),
    path('crud/productos/eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),

    path('ventas/', views.ver_ventas, name='ver_ventas'),
    path('ventas/editar/<int:venta_id>/', views.editar_venta, name='editar_venta'),
    path('ventas/eliminar/<int:venta_id>/', views.eliminar_venta, name='eliminar_venta'),

    path('ventas/detalle/<int:venta_id>/', views.detalle_venta, name='detalle_venta'),


    path('usuarios/<int:user_id>/', views.detalle_usuario, name='detalle_usuario'),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


