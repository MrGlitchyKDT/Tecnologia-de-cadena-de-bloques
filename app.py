import hashlib
import json
import time
import threading
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Variable global para evitar múltiples procesos de minería
estado_mineria = {"minando": False}

# --- LÓGICA DE LA BLOCKCHAIN ---
class Blockchain:
    def __init__(self):
        self.chain = []
        self.transacciones_pendientes = []
        self.nodos = {}
        self.dificultad = 2
        
        # Bloque Génesis
        self.crear_bloque(nonce=100, hash_anterior="00000000000000000000000000000000")

    def crear_bloque(self, nonce, hash_anterior):
        bloque = {
            'indice': len(self.chain) + 1,
            'timestamp': time.time(),
            'transacciones': self.transacciones_pendientes,
            'nonce': nonce,
            'hash_anterior': hash_anterior
        }
        bloque['hash'] = self.generar_hash_datos(bloque)
        
        self.transacciones_pendientes = []
        self.chain.append(bloque)
        return bloque

    def obtener_ultimo_bloque(self):
        return self.chain[-1]

    @staticmethod
    def generar_hash_datos(bloque):
        # Hacemos una copia para calcular la huella pura de los datos
        bloque_copia = bloque.copy()
        # Excluimos la clave 'hash' para no crear un bucle infinito al calcular
        if 'hash' in bloque_copia:
            del bloque_copia['hash']
            
        bloque_string = json.dumps(bloque_copia, sort_keys=True).encode()
        return hashlib.sha256(bloque_string).hexdigest()

    def prueba_de_trabajo(self, hash_anterior):
        nonce = 0
        while self.validar_prueba(hash_anterior, nonce) is False:
            nonce += 1
        return nonce

    def validar_prueba(self, hash_anterior, nonce):
        intento = f'{hash_anterior}{nonce}'.encode()
        intento_hash = hashlib.sha256(intento).hexdigest()
        return intento_hash[:self.dificultad] == "0" * self.dificultad

    def validar_cadena(self, cadena):
        for i in range(1, len(cadena)):
            bloque_actual = cadena[i]
            bloque_anterior = cadena[i-1]

            if bloque_actual['hash'] != self.generar_hash_datos(bloque_actual):
                print(f"ERROR: integridad interna rota en el Bloque {bloque_actual['indice']}")
                return False

            if bloque_actual['hash_anterior'] != bloque_anterior['hash']:
                print(f"ERROR: enlace roto entre Bloque {bloque_anterior['indice']} y {bloque_actual['indice']}")
                return False
                
        return True

    def encontrar_bloque_invalido(self):
        for i in range(1, len(self.chain)):
            bloque_actual = self.chain[i]
            bloque_anterior = self.chain[i-1]

            if bloque_actual['hash'] != self.generar_hash_datos(bloque_actual):
                return i

            if bloque_actual['hash_anterior'] != bloque_anterior['hash']:
                return i - 1

        return None

    def reparar_cadena(self, desde_indice=1):
        for idx in range(desde_indice, len(self.chain)):
            bloque = self.chain[idx]
            bloque['indice'] = idx + 1
            bloque['hash_anterior'] = self.chain[idx - 1]['hash']
            bloque['hash'] = self.generar_hash_datos(bloque)

bc = Blockchain()

# --- FUNCIONES ASÍNCRONAS ---
def tarea_mineria_asincrona(ip_minero):
    estado_mineria["minando"] = True
    ultimo_bloque = bc.obtener_ultimo_bloque()
    
    # Tomamos directamente el hash que el bloque ya tiene guardado
    hash_anterior = ultimo_bloque['hash'] 
    
    # Resolviendo la prueba de trabajo (minando)
    nonce = bc.prueba_de_trabajo(hash_anterior)
    
    identificador = "Validador(Tú)" if ip_minero == "127.0.0.1" else f"Nodo_{ip_minero}"
    
    bc.transacciones_pendientes.append({
        "remitente": "0", 
        "destinatario": identificador,
        "cantidad": 1
    })
    
    bc.crear_bloque(nonce, hash_anterior)
    estado_mineria["minando"] = False

# --- INTERFAZ VISUAL ---
HTML_UI = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blockchain Interactiva</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    
    <style>
        body { background-color: #f4f7f6; overflow-x: hidden; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .wrapper { display: flex; height: 100vh; }
        
        /* BARRA LATERAL (NODOS) */
        .sidebar { width: 300px; background-color: #1a252f; color: white; padding: 20px; box-shadow: 3px 0 15px rgba(0,0,0,0.3); z-index: 10; display: flex; flex-direction: column; }
        .sidebar h3 { font-weight: bold; border-bottom: 2px solid #34495e; padding-bottom: 15px; margin-bottom: 20px; text-align: center; }
        .node-item { background: #2c3e50; padding: 15px; border-radius: 10px; margin-bottom: 15px; display: flex; align-items: center; box-shadow: 0 4px 8px rgba(0,0,0,0.2); transition: transform 0.3s; }
        .node-item:hover { transform: scale(1.05); cursor: pointer; }
        
        .pulse { width: 16px; height: 16px; background-color: #2ecc71; border-radius: 50%; margin-right: 15px; box-shadow: 0 0 0 rgba(46, 204, 113, 0.4); animation: pulse-animation 1.5s infinite; flex-shrink: 0;}
        @keyframes pulse-animation { 0% { box-shadow: 0 0 0 0 rgba(46, 204, 113, 0.7); } 70% { box-shadow: 0 0 0 12px rgba(46, 204, 113, 0); } 100% { box-shadow: 0 0 0 0 rgba(46, 204, 113, 0); } }

        /* ÁREA PRINCIPAL */
        .main-content { flex-grow: 1; padding: 40px; display: flex; flex-direction: column; overflow-y: auto; }
        
        .button-panel { display: flex; gap: 20px; margin-bottom: 40px; flex-wrap: wrap; }
        .btn-action { flex: 1; min-width: 200px; padding: 20px; font-size: 1.2rem; font-weight: bold; border-radius: 15px; border: none; color: white; box-shadow: 0 8px 15px rgba(0,0,0,0.2); transition: all 0.2s ease-in-out; text-transform: uppercase;}
        .btn-action:hover { transform: translateY(-5px); box-shadow: 0 12px 20px rgba(0,0,0,0.3); }
        .btn-action:active { transform: translateY(2px); box-shadow: 0 4px 10px rgba(0,0,0,0.2); }
        .btn-mine { background: linear-gradient(135deg, #f39c12, #d35400); }
        .btn-tx { background: linear-gradient(135deg, #3498db, #2980b9); }
        .btn-val { background: linear-gradient(135deg, #2ecc71, #27ae60); }
        
        /* BLOQUES */
        .blockchain-container { display: flex; overflow-x: auto; padding: 20px 10px; gap: 20px; align-items: center; min-height: 350px;}
        .block-card { min-width: 320px; background: white; border-radius: 12px; border-top: 6px solid #34495e; box-shadow: 0 0 15px rgba(0,0,0,0.1); padding: 20px; transition: all 0.3s; position: relative;}
        .block-card:hover { border-top-color: #3498db; box-shadow: 0 0 20px rgba(52, 152, 219, 0.4); transform: scale(1.02);}
        
        .hash-text { display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: #e74c3c; font-family: monospace; font-size: 0.95rem; background: #f8f9fa; padding: 5px; border-radius: 4px;}
        .chain-link { font-size: 2.5rem; color: #bdc3c7; }
        
        #notification-area { position: fixed; bottom: 20px; right: 20px; z-index: 1000; }
        .toast-msg { background: #34495e; color: white; padding: 15px 25px; border-radius: 8px; margin-top: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); opacity: 0; transition: opacity 0.3s; }
    </style>
</head>
<body>

<div class="wrapper">
    <!-- PANEL IZQUIERDO -->
    <div class="sidebar">
        <h3>Red P2P Activa</h3>
        <p class="text-muted text-center" style="font-size: 0.9rem;">Dispositivos sincronizando en la red</p>
        <div id="nodes-container"></div>
    </div>

    <!-- PANEL PRINCIPAL -->
    <div class="main-content">
        <h1 class="mb-2">BLOCKCHAIN - CAPICOIN</h1>
        <p class="text-muted mb-4">Interactúa con la cadena. Conexion mediante WIFI.</p>
        
        <div class="button-panel">
            <button class="btn-action btn-tx" onclick="agregarTransaccionAleatoria()">Transacción Aleatoria</button>
            <button class="btn-action btn-mine" onclick="minarBloque()">Minar Bloque</button>
            <button class="btn-action btn-val" onclick="validarCadena()">Validar Cadena</button>
            <button class="btn-action text-white" style="background: #c0392b;" onclick="eliminarBloque()">Borrar Bloque</button>
            <button class="btn-action text-white" style="background: #2c3e50;" onclick="hackearCadena()">Simular Hackeo</button>
        </div>

        <h4 class="text-secondary mt-2">CADENA DE BLOQUES (Ledger)</h4>
        <div class="blockchain-container" id="blockchain-container"></div>
    </div>
</div>

<div id="notification-area"></div>

<script>
    function mostrarNotificacion(mensaje, color="#34495e") {
        const panel = document.getElementById("notification-area");
        const msg = document.createElement("div");
        msg.className = "toast-msg";
        msg.style.backgroundColor = color;
        msg.innerText = mensaje;
        panel.appendChild(msg);
        setTimeout(() => msg.style.opacity = "1", 10);
        setTimeout(() => { msg.style.opacity = "0"; setTimeout(() => msg.remove(), 300); }, 3000);
    }

    function eliminarBloque() {
        mostrarNotificacion("Intentando borrar bloque...", "#c0392b");
        fetch('/api/delete_block')
        .then(response => response.json())
        .then(data => {
            if(data.status.includes("Mina")) {
                mostrarNotificacion(data.status, "#e67e22");
            } else {
                mostrarNotificacion(data.status, "#c0392b");
            }
        });
    }
    
    function agregarTransaccionAleatoria() {
        const remitentes = ["Alice", "Bob", "Charlie", "Diana"];
        const destinatarios = ["Eva", "Frank", "Grace", "Hank"];
        const tx = {
            remitente: remitentes[Math.floor(Math.random() * remitentes.length)],
            destinatario: destinatarios[Math.floor(Math.random() * destinatarios.length)],
            cantidad: Math.floor(Math.random() * 100) + 1
        };

        fetch('/api/transactions/new', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(tx)
        })
        .then(response => response.json())
        .then(data => mostrarNotificacion("✅ " + data.mensaje, "#2980b9"))
        .catch(error => mostrarNotificacion("❌ Error al añadir", "#e74c3c"));
    }

    function minarBloque() {
        mostrarNotificacion("Minando... Resolviendo Proof of Work...", "#f39c12");
        fetch('/api/mine')
        .then(response => response.json())
        .then(data => {
            if(data.status.includes("iniciada")) {
                mostrarNotificacion("✅ " + data.status, "#27ae60");
            } else {
                mostrarNotificacion("⚠️ " + data.status, "#e67e22");
            }
        });
    }

    function validarCadena() {
        fetch('/api/validate')
        .then(response => response.json())
        .then(data => {
            if(data.status.includes("✅")) {
                mostrarNotificacion(data.status, "#27ae60");
            } else {
                mostrarNotificacion(data.status, "#e74c3c");
            }
        });
    }

    function hackearCadena() {
        mostrarNotificacion("Inyectando código malicioso...", "#8e44ad");
        fetch('/api/hack')
        .then(response => response.json())
        .then(data => {
            if(data.status.includes("Mina")) {
                mostrarNotificacion(data.status, "#e67e22");
            } else {
                mostrarNotificacion(data.status, "#c0392b"); // Rojo de alerta
            }
        });
    }

    function actualizarNodos() {
        fetch('/api/status')
        .then(res => res.json())
        .then(nodos => {
            const container = document.getElementById('nodes-container');
            container.innerHTML = ''; 
            for (const [ip, info] of Object.entries(nodos)) {
                container.innerHTML += `
                    <div class="node-item">
                        <div class="pulse"></div>
                        <div>
                            <strong style="display:block; font-size:1.1rem;">IP: ${ip}</strong>
                            <span class="text-info">${info.rol}</span>
                        </div>
                    </div>
                `;
            }
        });
    }

    function actualizarBlockchain() {
        fetch('/api/chain')
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById('blockchain-container');
            container.innerHTML = ''; 
            data.cadena.forEach((bloque, index) => {
                let txHtml = bloque.transacciones.length === 0 
                    ? '<span class="text-muted">Sin transacciones</span>' 
                    : bloque.transacciones.map(t => `💸 ${t.remitente} -> ${t.destinatario}: <b>${t.cantidad}</b>`).join('<br>');

                const card = `
                    <div class="block-card">
                        <h5 class="text-center font-weight-bold">Bloque #${bloque.indice}</h5>
                        <hr>
                        <p class="mb-1"><strong>Nonce:</strong> ${bloque.nonce}</p>
                        <p class="mb-1"><strong>Transacciones:</strong><br>${txHtml}</p>
                        <hr>
                        <p class="mb-1"><strong>Prev Hash:</strong><br><span class="hash-text text-muted">${bloque.hash_anterior}</span></p>
                    </div>
                `;
                container.innerHTML += card;
                if(index < data.cadena.length - 1) {
                    container.innerHTML += `<div class="chain-link">🔗</div>`;
                }
            });
            container.scrollLeft = container.scrollWidth;
        });
    }

    setInterval(() => {
        actualizarNodos();
        actualizarBlockchain();
    }, 2000);
    actualizarNodos();
    actualizarBlockchain();
</script>
</body>
</html>
'''

# --- RUTAS DE FLASK ---
@app.route('/')
def index():
    return render_template_string(HTML_UI)

@app.route('/api/hack', methods=['GET'])
def hackear():
    # Nos aseguramos de que haya al menos 2 bloques (Génesis + 1 bloque minado)
    if len(bc.chain) < 2:
        return jsonify({"status": "⚠️ Mina al menos un bloque primero para poder hackearlo"}), 400
    
    # Seleccionamos el bloque 2 (índice 1) y reescribimos sus datos a la fuerza
    bloque_objetivo = bc.chain[1]
    bloque_objetivo['transacciones'] = [{"remitente": "Banco", "destinatario": "Hacker_Anonimo", "cantidad": 999999}]
    bloque_objetivo['hash'] = bc.generar_hash_datos(bloque_objetivo)
    
    return jsonify({"status": "🦹‍♂️ ¡Hackeo exitoso! Bloque 2 alterado en secreto"}), 200

@app.route('/api/delete_block', methods=['GET'])
def eliminar_bloque():
    if len(bc.chain) < 3:
        return jsonify({"status": "⚠️ Mina al menos 2 bloques nuevos para demostrar la eliminación"}), 400

    invalido = bc.encontrar_bloque_invalido()
    if invalido is None:
        return jsonify({"status": "✅ No hay bloques alterados. Nada que borrar."}), 200

    bloque_eliminado = bc.chain.pop(invalido)
    bc.reparar_cadena(desde_indice=invalido)

    return jsonify({"status": f"🗑️ ¡Bloque {bloque_eliminado['indice']} eliminado y la cadena reparada!"}), 200

@app.route('/api/status')
def status():
    ip = request.remote_addr
    if ip not in bc.nodos:
        rol = "Validador (Tú)" if ip == "127.0.0.1" else "Cliente/Nodo"
        bc.nodos[ip] = {"rol": rol, "last_seen": time.time()}
    return jsonify(bc.nodos)

@app.route('/api/transactions/new', methods=['POST'])
def nueva_transaccion():
    valores = request.get_json()
    requeridos = ['remitente', 'destinatario', 'cantidad']
    if not valores or not all(k in valores for k in requeridos):
        return 'Faltan valores', 400

    bc.transacciones_pendientes.append(valores)
    respuesta = {'mensaje': f'La transacción irá al bloque {bc.obtener_ultimo_bloque()["indice"] + 1}'}
    return jsonify(respuesta), 201

@app.route('/api/mine', methods=['GET'])
def mine():
    if estado_mineria["minando"]:
        return jsonify({"status": "Ya hay un proceso de minería en curso"}), 429

    ip_solicitante = request.remote_addr
    hilo = threading.Thread(target=tarea_mineria_asincrona, args=(ip_solicitante,))
    hilo.start()

    return jsonify({"status": f"Minería iniciada por {ip_solicitante}..."}), 200

@app.route('/api/chain', methods=['GET'])
def full_chain():
    return jsonify({'cadena': bc.chain, 'longitud': len(bc.chain)}), 200

@app.route('/api/validate', methods=['GET'])
def validate():
    if bc.validar_cadena(bc.chain):
        return jsonify({"status": "✅ Cadena válida e íntegra"}), 200
    else:
        return jsonify({"status": "❌ ERROR: La cadena ha sido alterada"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
