# Semana 12 · Servicios web con Django y React

Se reutilizan la API de cuestionarios de la Semana 8 y la cartelera de la Semana 11. La pestaña **Exámenes** usa Axios para consultar, crear y eliminar registros. Django conserva la autenticación por token y el control de roles de la Semana 8.

## Servidor Django

Desde `Semana 12`, en PowerShell:

```powershell
cd servidor
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_quiz
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Ejecuta `seed_quiz` sobre una base de laboratorio: al repetirlo, reemplaza los exámenes por los datos de demostración. Guarda el token local del usuario `profe` para ingresarlo en el cliente. El token del agente no permite eliminar. La raíz HTTP de la API es `http://127.0.0.1:8000/api/` y la documentación navegable está en `http://127.0.0.1:8000/api/docs/`. La raíz de DRF exige autenticación.

## Cliente React

Abre otra consola desde `Semana 12`:

```powershell
cd cliente
npm ci
npm run dev -- --host localhost --port 5173 --strictPort
```

Abre `http://localhost:5173/#/examenes`. En **Configurar acceso a Django**, pega el token local de **profe** y guarda el acceso. El token dura lo que dure la sesión de la pestaña o hasta pulsar **Cerrar acceso**. Usa Python 3.12 o superior y Node 20.19+, 22.12+ o una versión posterior compatible con Vite.

La API permite exclusivamente el origen `http://localhost:5173` por defecto. Si se cambia el origen del cliente, define `DJANGO_CORS_ORIGINS` con el origen exacto antes de iniciar Django. Si se cambia la dirección del servidor, define `VITE_API_URL` con la URL base, incluida la ruta `/api/`, antes de iniciar Vite.

| Acción | Petición | Resultado |
| --- | --- | --- |
| Abrir listado o reintentar | `GET /api/exams/?page=1` | Carga, tabla paginada o error con reintento |
| Guardar título válido | `POST /api/exams/` | HTTP 201 y regreso al listado |
| Guardar título vacío | `POST /api/exams/` | HTTP 400 y mensaje del campo `title` |
| Eliminar | `DELETE /api/exams/<id>/` | HTTP 204 y nueva consulta del listado |

Para reproducir el bloqueo CORS, inicia Django temporalmente con `$env:DJANGO_CORS_ORIGINS = ''` y abre el listado en una pestaña nueva. Restaura la configuración con `Remove-Item Env:DJANGO_CORS_ORIGINS` y reinicia Django. Para verificar la caída, detén Django con React abierto y vuelve a entrar a Exámenes. La recuperación se comprueba reiniciando Django y pulsando **Reintentar**.

Pruebas del servidor: `manage.py test` con el Python del entorno virtual. Compilación del cliente: `npm run build`.


## Entregable y evidencias

- [Guía de laboratorio resuelta](GLAB-S12-MMONTGOMERY-2026-02-resuelto.docx)
- [Capturas originales y resultados de pruebas](evidencias/)
