from flask import Flask, render_template, request, jsonify
import anthropic
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

def cargar_glosario():
    with open("glosario.json", "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_glosario(data):
    data["terminos"].sort(key=lambda t: t["termino"].lower())
    with open("glosario.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

DESCRIPCIONES_CATEGORIA = {
    "Base de datos": "Sistemas para almacenar, organizar y consultar información de forma estructurada.",
    "General": "Conceptos fundamentales de programación que aplican a cualquier tecnología o lenguaje.",
    "Git": "Herramientas para controlar versiones de código, colaborar en equipo y gestionar el historial de cambios.",
    "Python": "Conceptos del lenguaje Python y su ecosistema de librerías y herramientas.",
    "Web": "Tecnologías y conceptos para construir y publicar aplicaciones en internet.",
}

@app.route("/")
def index():
    glosario = cargar_glosario()
    return render_template("index.html", terminos=glosario["terminos"], descripciones=DESCRIPCIONES_CATEGORIA)

@app.route("/agregar", methods=["POST"])
def agregar():
    termino = request.json.get("termino")
    cliente = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    mensaje = cliente.messages.create(
        model="claude-opus-4-7",
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": f"Evalúa si '{termino}' es un término de desarrollo de software. Si NO lo es, responde exactamente: {{\"valido\": false}}. Si SÍ lo es, defínelo en máximo 2 oraciones simples en español e indica su categoría eligiendo una de: Git, Python, Web, Base de datos, General. Responde: {{\"valido\": true, \"definicion\": \"...\", \"categoria\": \"...\"}}"
        }]
    )
    respuesta = json.loads(mensaje.content[0].text)
    if not respuesta.get("valido"):
        return jsonify({"ok": False, "invalido": True})
    glosario = cargar_glosario()
    glosario["terminos"].append({
        "termino": termino,
        "definicion": respuesta["definicion"],
        "categoria": respuesta["categoria"]
    })
    guardar_glosario(glosario)
    return jsonify({"ok": True})

@app.route("/eliminar", methods=["POST"])
def eliminar():
    indice = request.json.get("indice")
    glosario = cargar_glosario()
    glosario["terminos"].pop(indice)
    guardar_glosario(glosario)
    return jsonify({"ok": True})

@app.route("/editar", methods=["POST"])
def editar():
    indice = request.json.get("indice")
    definicion = request.json.get("definicion")
    glosario = cargar_glosario()
    glosario["terminos"][indice]["definicion"] = definicion
    guardar_glosario(glosario)
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(debug=True)