import os
import re
from datetime import datetime
from zoneinfo import ZoneInfo

import cloudinary
import cloudinary.uploader
import cloudinary.api

from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Credenciales: se configuran como variables de entorno
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
    secure=True
)

DETECTOR_TOKEN = os.environ.get("DETECTOR_TOKEN", "")

HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="60">
<title>Monitor de lirios acuáticos</title>
<style>
body {
  margin: 0;
  font-family: Arial, sans-serif;
  background: #f1f7f2;
  color: #183c2c;
}
header {
  background: #176b48;
  color: white;
  padding: 28px 16px;
  text-align: center;
}
main { max-width: 1100px; margin: auto; padding: 20px; }
.galeria {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 18px;
}
.tarjeta {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 3px 12px #0001;
}
.tarjeta img {
  width: 100%;
  height: 230px;
  object-fit: cover;
}
.info { padding: 14px; }
.fecha { color: #426b57; font-size: 14px; }
a { color: #176b48; }
footer { text-align: center; padding: 24px; }
</style>
</head>
<body>
<header>
  <h1>Detección de lirios acuáticos</h1>
  <p>Galería pública de fotografías detectadas mediante YOLO11</p>
</header>
<main>
  <h2>Últimas detecciones</h2>
  <p>Las fotografías se actualizan automáticamente cada minuto.</p>
  {% if fotos %}
  <section class="galeria">
    {% for foto in fotos %}
    <article class="tarjeta">
      <a href="{{ foto.url }}" target="_blank" rel="noopener">
        <img src="{{ foto.url }}" alt="Fotografía de detección de lirio acuático"
             loading="lazy">
      </a>
      <div class="info">
        <strong>Lirio acuático</strong>
        <p class="fecha">Fecha y hora: {{ foto.fecha }}</p>
      </div>
    </article>
    {% endfor %}
  </section>
  {% else %}
  <p>Aún no hay fotografías disponibles.</p>
  {% endif %}
</main>
<footer>Proyecto de monitoreo de lirios acuáticos</footer>
</body>
</html>
"""


def obtener_fotos():
    """Consulta en Cloudinary las fotografías guardadas por el detector."""
    resultado = cloudinary.api.resources(
        resource_type="image",
        type="upload",
        prefix="lirios/",
        max_results=100
    )

    fotos = []

    for recurso in resultado.get("resources", []):
        public_id = recurso.get("public_id", "")
        nombre = public_id.rsplit("/", 1)[-1]

        # Nombre esperado:
        # Lirio_20261024_154500_123456
        coincidencia = re.fullmatch(
            r"Lirio_(\d{8})_(\d{6})_(\d{6})",
            nombre
        )

        if coincidencia:
            fecha_dt = datetime.strptime(
                nombre, "Lirio_%Y%m%d_%H%M%S_%f"
            )
            fecha = fecha_dt.strftime("%d/%m/%Y %H:%M:%S")
        else:
            fecha = recurso.get("created_at", "Fecha no disponible")

        fotos.append({
            "url": recurso["secure_url"],
            "fecha": fecha,
            "creada": recurso.get("created_at", "")
        })

    fotos.sort(key=lambda f: f["creada"], reverse=True)
    return fotos


@app.route("/")
def inicio():
    try:
        fotos = obtener_fotos()
    except Exception:
        app.logger.exception("No se pudieron consultar las imágenes")
        fotos = []

    return render_template_string(HTML, fotos=fotos)


@app.route("/api/detections", methods=["POST"])
def recibir_deteccion():
    # Solo el programa detector puede subir nuevas fotografías.
    # Las visitas a la galería siguen siendo públicas.
    if not DETECTOR_TOKEN:
        return jsonify({"error": "Falta configurar DETECTOR_TOKEN"}), 500

    token = request.headers.get("X-Detector-Token", "")
    if token != DETECTOR_TOKEN:
        return jsonify({"error": "No autorizado"}), 401

    imagen = request.files.get("image")
    nombre = request.form.get("filename", "")

    if not imagen or not nombre:
        return jsonify({
            "error": "Falta la imagen o el nombre del archivo"
        }), 400

    # Solo aceptar nombres generados por el detector.
    if not re.fullmatch(
        r"Lirio_\d{8}_\d{6}_\d{6}\.jpg", nombre
    ):
        return jsonify({"error": "Nombre de archivo no válido"}), 400

    try:
        public_id = "lirios/" + nombre[:-4]

        resultado = cloudinary.uploader.upload(
            imagen,
            resource_type="image",
            public_id=public_id,
            overwrite=False
        )

        return jsonify({
            "mensaje": "Fotografía publicada",
            "url": resultado["secure_url"],
            "public_id": resultado["public_id"]
        }), 201

    except Exception:
        app.logger.exception("Error al subir la fotografía")
        return jsonify({"error": "No se pudo subir la imagen"}), 500


@app.route("/api/detections", methods=["GET"])
def listar_detecciones():
    # Este endpoint es público y no requiere token.
    try:
        return jsonify(obtener_fotos())
    except Exception:
        app.logger.exception("Error al consultar las detecciones")
        return jsonify({"error": "No se pudieron consultar las imágenes"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
