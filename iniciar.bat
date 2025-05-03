@echo off
setlocal

:: Establecer la codificación a UTF-8
chcp 65001 >nul

:: Definir las rutas de los proyectos
set DJANGO_PROJECT_1="C:\IT\DjangoSushi-main"
@echo off
setlocal

:: Establecer la codificación a UTF-8
chcp 65001 >nul
set PYTHONIOENCODING=utf-8

:: Definir las rutas de los proyectos
set DJANGO_PROJECT_1="C:\IT\DjangoSushi-main"
set DJANGO_PROJECT_2="C:\IT\administrar_usuarios\restaurante_sushi"

:: Ejecutar el primer servidor en primer plano en una nueva ventana de CMD
cd /d %DJANGO_PROJECT_1%
start cmd /k "set PYTHONIOENCODING=utf-8 && python manage.py runserver"

:: Esperar 3 segundos antes de iniciar el segundo servidor
timeout /t 3 /nobreak >nul

:: Ejecutar el segundo servidor en primer plano en una nueva ventana de CMD
cd /d %DJANGO_PROJECT_2%
start cmd /k "set PYTHONIOENCODING=utf-8 && python manage.py runserver 8001"

:: Mensaje de confirmación
echo Los servidores se han iniciado en nuevas ventanas de CMD.
exit
