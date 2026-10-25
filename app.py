import os
import re
from datetime import datetime
from zoneinfo import ZoneInfo

import cloudinary
import cloudinary.api
import cloudinary.uploader
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# ==========================================
# 1. CONFIGURACION
# ==========================================

ZONA_HORARIA = ZoneInfo("America/Mexico_City")

cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
    secure=True
)

DETECTOR_TOKEN = os.environ.get("DETECTOR_TOKEN", "")

# ==========================================
# 2. PAGINA WEB
# ==========================================

HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="60">
    <title>Proyecto Lirios Acuáticos</title>

    <style>
        :root {
            --verde: #176b45;
            --verde-oscuro: #104b32;
            --verde-claro: #eaf6ee;
            --azul: #eaf5fb;
            --texto: #24352b;
        }

        * {
            box-sizing: border-box;
            scroll-behavior: smooth;
        }

        body {
            margin: 0;
            font-family: Arial, Helvetica, sans-serif;
            color: var(--texto);
            background: #f7faf7;
            line-height: 1.6;
        }

        header {
            background: var(--verde-oscuro);
            color: white;
            padding: 16px 6%;
        }

        .marca {
            font-size: 1.2rem;
            font-weight: bold;
        }

        nav {
            background: var(--verde);
            padding: 12px 6%;
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            position: sticky;
            top: 0;
            z-index: 10;
        }

        nav a {
            color: white;
            text-decoration: none;
            font-weight: bold;
            font-size: 0.95rem;
        }

        nav a:hover {
            text-decoration: underline;
        }

        .hero {
            padding: 85px 7%;
            color: white;
            background: linear-gradient(
                120deg,
                rgba(10, 65, 43, .94),
                rgba(23, 107, 69, .79)
            );
            text-align: center;
        }

        .hero h1 {
            font-size: clamp(2rem, 5vw, 3.5rem);
            margin: 0 auto 20px;
            max-width: 900px;
            line-height: 1.15;
        }

        .hero p {
            max-width: 760px;
            margin: 0 auto 25px;
            font-size: 1.15rem;
        }

        .boton {
            display: inline-block;
            background: white;
            color: var(--verde-oscuro);
            padding: 12px 22px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: bold;
        }

        section {
            padding: 55px 7%;
            scroll-margin-top: 70px;
        }

        section h2 {
            color: var(--verde-oscuro);
            font-size: 2rem;
            margin-top: 0;
        }

        .introduccion {
            max-width: 900px;
            margin: auto;
            text-align: center;
        }

        .fondo-verde {
            background: var(--verde-claro);
        }

        .fondo-azul {
            background: var(--azul);
        }

        .tarjetas {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
            gap: 22px;
            margin-top: 25px;
        }

        .tarjeta {
            background: white;
            padding: 24px;
            border-radius: 14px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, .07);
        }

        .tarjeta h3 {
            color: var(--verde);
            margin-top: 0;
        }

        .icono {
            font-size: 2rem;
        }

        .galeria {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 22px;
            margin-top: 25px;
        }

        .foto {
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0, 0, 0, .08);
        }

        .foto img {
            width: 100%;
            height: 230px;
            object-fit: cover;
            display: block;
        }

        .foto-info {
            padding: 15px;
            overflow-wrap: anywhere;
        }

        .fecha {
            color: #5a6a60;
            font-size: .9rem;
        }

        .sin-fotos {
            background: white;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
        }

        .aviso {
            background: #fff8df;
            border-left: 5px solid #d8a528;
            padding: 18px;
            border-radius: 8px;
            margin-top: 20px;
        }

        footer {
            text-align: center;
            background: var(--verde-oscuro);
            color: white;
            padding: 28px 6%;
        }

        footer p {
            margin: 5px;
        }

        @media (max-width: 600px) {
            nav {
                gap: 12px;
            }

            nav a {
                font-size: .85rem;
            }

            section {
                padding: 40px 6%;
            }

            .hero {
                padding: 60px 6%;
            }
        }
    </style>
</head>

<body>
    <header>
        <div class="marca">🌿 Proyecto Lirios Acuáticos</div>
    </header>

    <nav>
        <a href="#inicio">Inicio</a>
        <a href="#conoce">Conoce el lirio</a>
        <a href="#impacto">Impacto ambiental</a>
        <a href="#proyecto">Nuestro proyecto</a>
        <a href="#galeria">Detecciones</a>
        <a href="#concientizacion">Concientización</a>
    </nav>

    <main>
        <section class="hero" id="inicio">
            <h1>Protejamos nuestros cuerpos de agua</h1>
            <p>
                Utilizamos tecnología de visión artificial para detectar
                lirios acuáticos y promover el cuidado de nuestros ecosistemas.
            </p>
            <a class="boton" href="#galeria">Ver fotografías detectadas</a>
        </section>

        <section id="conoce">
            <div class="introduccion">
                <h2>¿Qué es el lirio acuático?</h2>
                <p>
                    El lirio acuático (<em>Eichhornia crassipes</em>) es una
                    planta flotante que se reproduce rápidamente en ciertos
                    cuerpos de agua. Su proliferación excesiva puede generar
                    problemas ambientales.
                </p>
            </div>

            <div class="tarjetas">
                <article class="tarjeta">
                    <div class="icono">🌱</div>
                    <h3>Planta flotante</h3>
                    <p>
                        Crece sobre la superficie del agua y puede formar
                        grandes agrupaciones.
                    </p>
                </article>

                <article class="tarjeta">
                    <div class="icono">💧</div>
                    <h3>Reproducción rápida</h3>
                    <p>
                        Cuando las condiciones son favorables, puede expandirse
                        y cubrir amplias zonas.
                    </p>
                </article>

                <article class="tarjeta">
                    <div class="icono">🔎</div>
                    <h3>Monitoreo</h3>
                    <p>
                        Observar su presencia ayuda a identificar áreas que
                        requieren evaluación ambiental.
                    </p>
                </article>
            </div>
        </section>

        <section class="fondo-verde" id="impacto">
            <div class="introduccion">
                <h2>Impacto ambiental</h2>
                <p>
                    Cuando el lirio acuático cubre gran parte de un cuerpo de
                    agua, puede alterar las condiciones necesarias para la
                    vida acuática y dificultar algunos usos del recurso.
                </p>
            </div>

            <div class="tarjetas">
                <article class="tarjeta">
                    <h3>🐟 Vida acuática</h3>
                    <p>
                        Las coberturas densas pueden reducir la entrada de luz
                        y modificar el oxígeno disuelto, afectando a algunos
                        organismos.
                    </p>
                </article>

                <article class="tarjeta">
                    <h3>🚣 Uso del agua</h3>
                    <p>
                        La acumulación de plantas puede dificultar la navegación,
                        la pesca y algunas actividades comunitarias.
                    </p>
                </article>

                <article class="tarjeta">
                    <h3>🌎 Equilibrio ecológico</h3>
                    <p>
                        La expansión excesiva puede cambiar las condiciones
                        del hábitat y afectar el equilibrio del ecosistema.
                    </p>
                </article>
            </div>

            <div class="aviso">
                <strong>Importante:</strong> la presencia de lirio no significa
                por sí sola que el agua esté contaminada. Cada sitio requiere
                una evaluación de sus condiciones ambientales.
            </div>
        </section>

        <section id="proyecto">
            <div class="introduccion">
                <h2>Nuestro proyecto</h2>
                <p>
                    Este proyecto utiliza un modelo de inteligencia artificial
                    YOLO11 para apoyar la detección visual del lirio acuático.
                    Las fotografías se envían a una galería para facilitar su
                    consulta y seguimiento.
                </p>
            </div>

            <div class="tarjetas">
                <article class="tarjeta">
                    <h3>1. Captura de imágenes</h3>
                    <p>
                        Una cámara obtiene fotografías del entorno que se desea
                        monitorear.
                    </p>
                </article>

                <article class="tarjeta">
                    <h3>2. Detección con IA</h3>
                    <p>
                        El modelo analiza las imágenes para identificar lirios
                        según su entrenamiento.
                    </p>
                </article>

                <article class="tarjeta">
                    <h3>3. Registro y consulta</h3>
                    <p>
                        Las fotografías se almacenan en la nube y se muestran
                        en la galería pública.
                    </p>
                </article>
            </div>
        </section>

        <section class="fondo-azul" id="galeria">
            <div class="introduccion">
                <h2>Galería de detecciones</h2>
                <p>
                    Fotografías registradas por el sistema. La página se
                    actualiza automáticamente cada 60 segundos.
                    Las horas se muestran en horario de Chiapas.
                </p>
            </div>

            {% if fotos %}
                <div class="galeria">
                    {% for foto in fotos %}
                        <article class="foto">
                            <a href="{{ foto.url }}" target="_blank"
                               rel="noopener noreferrer">
                                <img src="{{ foto.url }}"
                                     alt="Fotografía de una detección de lirio acuático"
                                     loading="lazy">
                            </a>
                            <div class="foto-info">
                                <strong>Detección registrada</strong>
                                <div class="fecha">{{ foto.fecha }}</div>
                            </div>
                        </article>
                    {% endfor %}
                </div>
            {% else %}
                <div class="sin-fotos">
                    <h3>Aún no hay fotografías</h3>
                    <p>
                        Cuando el detector envíe nuevas imágenes, aparecerán
                        aquí automáticamente.
                    </p>
                </div>
            {% endif %}
        </section>

        <section id="concientizacion">
            <div class="introduccion">
                <h2>Concientización ambiental</h2>
                <p>
                    Cuidar los ecosistemas acuáticos es una responsabilidad
                    compartida. La información y la prevención ayudan a
                    proteger el agua y la biodiversidad.
                </p>
            </div>

            <div class="tarjetas">
                <article class="tarjeta">
                    <h3>💧 Cuida el agua</h3>
                    <p>
                        Evita arrojar basura, aceites o sustancias contaminantes
                        a ríos, lagos y otros cuerpos de agua.
                    </p>
                </article>

                <article class="tarjeta">
                    <h3>📢 Comparte información</h3>
                    <p>
                        Promueve la educación ambiental y comunica los problemas
                        observados a las autoridades correspondientes.
                    </p>
                </article>

                <article class="tarjeta">
                    <h3>🌿 Actúa responsablemente</h3>
                    <p>
                        No retires ni traslades plantas acuáticas por tu cuenta
                        sin conocer las recomendaciones locales.
                    </p>
                </article>
            </div>
        </section>
    </main>

    <footer>
        <p><strong>Proyecto de monitoreo de lirios acuáticos</strong></p>
        <p>Tecnología al servicio del cuidado ambiental.</p>
    </footer>
</body>
</html>
"""


# ==========================================
# 3. OBTENER FOTOGRAFIAS DE CLOUDINARY
# ==========================================

def obtener_fotos():
    try:
        respuesta = cloudinary.api.resources(
            resource_type="image",
            type="upload",
            prefix="lirios/",
            max_results=100
        )

        fotos = []

        for recurso in respuesta.get("resources", []):
            nombre = recurso.get("filename", "")
            fecha = None

            coincidencia = re.search(
                r"Lirio_(\d{8})_(\d{6})_(\d{6})",
                nombre
            )

            if coincidencia:
                try:
                    fecha = datetime.strptime(
                        "_".join(coincidencia.groups()),
                        "%Y%m%d_%H%M%S_%f"
                    ).replace(tzinfo=ZONA_HORARIA)
                except ValueError:
                    fecha = None

            if fecha is None:
                creada = recurso.get("created_at", "")

                try:
                    fecha = datetime.fromisoformat(
                        creada.replace("Z", "+00:00")
                    )

                    if fecha.tzinfo is None:
                        fecha = fecha.replace(
                            tzinfo=ZoneInfo("UTC")
                        )

                    fecha = fecha.astimezone(ZONA_HORARIA)

                except (ValueError, TypeError, AttributeError):
                    fecha = None

            if fecha is not None:
                fecha_texto = fecha.strftime(
                    "%d/%m/%Y %I:%M:%S %p"
                )
                orden = fecha.timestamp()
            else:
                fecha_texto = "Fecha no disponible"
                orden = 0

            fotos.append({
                "url": recurso.get("secure_url", ""),
                "fecha": fecha_texto,
                "creada": orden
            })

        fotos.sort(
            key=lambda foto: foto["creada"],
            reverse=True
        )

        return fotos

    except Exception:
        app.logger.exception(
            "Error al obtener fotografías de Cloudinary"
        )
        return []


# ==========================================
# 4. PAGINA PRINCIPAL
# ==========================================

@app.route("/")
def inicio():
    fotos = obtener_fotos()
    return render_template_string(HTML, fotos=fotos)


# ==========================================
# 5. RECIBIR FOTOGRAFIAS DEL DETECTOR
# ==========================================

@app.route("/api/detections", methods=["POST"])
def recibir_deteccion():
    if not DETECTOR_TOKEN:
        return jsonify({
            "error": "El servidor no tiene configurado DETECTOR_TOKEN"
        }), 500

    token = request.headers.get("X-Detector-Token", "")

    if token != DETECTOR_TOKEN:
        return jsonify({"error": "No autorizado"}), 401

    nombre = request.form.get("filename", "").strip()

    if not re.fullmatch(
        r"Lirio_\d{8}_\d{6}_\d{6}\.jpg",
        nombre
    ):
        return jsonify({
            "error": "Nombre de archivo inválido o ausente"
        }), 400

    # CORRECCION: aceptar "image", que es el campo
    # que utiliza el detector actual.
    archivo = (
        request.files.get("image")
        or request.files.get("file")
        or request.files.get("imagen")
        or request.files.get("foto")
        or request.files.get("archivo")
    )

    if archivo is None or not archivo.filename:
        return jsonify({
            "error": "No se recibió ninguna fotografía"
        }), 400

    try:
        resultado = cloudinary.uploader.upload(
            archivo,
            public_id=f"lirios/{nombre.rsplit('.', 1)[0]}",
            resource_type="image",
            overwrite=False
        )

        return jsonify({
            "mensaje": "Fotografía recibida correctamente",
            "url": resultado.get("secure_url")
        }), 201

    except Exception:
        app.logger.exception(
            "Error al guardar la fotografía en Cloudinary"
        )
        return jsonify({
            "error": "No se pudo guardar la fotografía"
        }), 500


# ==========================================
# 6. CONSULTAR DETECCIONES
# ==========================================

@app.route("/api/detections", methods=["GET"])
def listar_detecciones():
    fotos = obtener_fotos()

    return jsonify([
        {
            "url": foto["url"],
            "fecha": foto["fecha"]
        }
        for foto in fotos
    ])


# ==========================================
# 7. INICIAR SERVIDOR
# ==========================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
