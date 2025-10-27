<template>
  <div class="modal-compartir" @click.self="$emit('cerrar')">
    <div class="modal-contenido" :class="{ 'theme-dark': isDark, 'theme-light': !isDark }">
      <div class="modal-header">
        <h2>Invitar Usuarios al Proyecto</h2>
        <button @click="$emit('cerrar')" class="btn-cerrar">&times;</button>
      </div>

      <div class="modal-body">
        <p class="project-id-label">Proyecto ID: {{ proyectoId }}</p>

        <div v-if="loading" class="alert-info">
          <i class="bi bi-arrow-clockwise fa-spin"></i> Generando link...
        </div>
        <div v-if="error" class="alert-error">{{ error }}</div>

        <div class="link-generation-section" v-if="!loading">
          <h3>Link de Invitación (Expira en 24 horas)</h3>
          
          <div class="link-box">
            <input type="text" :value="invitationLink" readonly ref="linkInput" class="form-control" />
            
            <button @click="copyLink" :disabled="!invitationLink" class="btn-copy" title="Copiar link">
              <i :class="copySuccess ? 'bi bi-check-lg' : 'bi bi-clipboard-fill'"></i>
            </button>
          </div>
          
          <p class="link-status" v-if="copySuccess">¡Copiado con éxito!</p>
          <p class="link-status" v-else-if="invitationLink">Comparte este link para dar acceso.</p>

          <div class="qr-management-box">
            <button @click="showQr = !showQr" class="btn-qr" :disabled="!invitationLink">
                <i class="bi bi-qr-code"></i> {{ showQr ? 'Ocultar QR' : 'Mostrar QR' }}
            </button>

            <div v-if="showQr && invitationLink" class="qr-code-box mt-3">
                <canvas id="qr-code-canvas"></canvas> 
            </div>
          </div>
        </div>
        
        <div class="user-management-section mt-4">
            <h4>Usuarios con Acceso ({{ members.length }} Total)</h4>
            <ul class="user-list">
                <li v-if="members.length === 0" class="user-item-placeholder">
                    Aún no hay otros miembros en este proyecto.
                </li>
                
                <li 
                    v-for="member in members" 
                    :key="member.usuario_id" 
                    class="user-item"
                    :class="{ 'owner': member.nombre_rol === 'Propietario' }"
                >
                    <i class="bi bi-person-fill"></i> 
                    
                    <span class="member-name">{{ member.nombre_usuario }}</span>
                    <span class="member-role">({{ member.nombre_rol }})</span>
                    
                    <button 
                        v-if="member.nombre_rol !== 'Propietario'"
                        @click="removeMember(member.usuario_id)" 
                        class="btn-remove" 
                        title="Remover Acceso"
                    >
                        <i class="bi bi-x-lg"></i>
                    </button>
                </li>
            </ul>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import QRCode from 'qrcode'; // 🚨 1. IMPORTAR LIBRERÍA QR
const API_BASE_URL = 'http://127.0.0.1:8001';


export default {
    name: 'ModalCompartir',
    props: {
        proyectoId: {
            type: Number,
            required: true
        }
    },
    data() {
        return {
            isDark: false,
            loading: false,
            error: null,
            invitationLink: '',
            copySuccess: false,
            members: [], 
            showQr: false, // 🚨 2. AÑADIDO: Estado para mostrar/ocultar el QR
        };
    },
    
    // 🚨 3. WATCHERS: Detecta el cambio en el link o en el botón de Mostrar QR
    watch: {
        // Observa el estado showQr (cuando el usuario presiona el botón)
        showQr(newValue) {
            if (newValue && this.invitationLink) {
                // $nextTick espera a que Vue haya renderizado el <canvas> en el DOM.
                this.$nextTick(() => { 
                    this.generateQrCode(this.invitationLink);
                });
            }
        },
        // Observa si el link se genera de la API mientras el QR está visible
        invitationLink(newLink) {
            if (this.showQr && newLink) {
                this.$nextTick(() => { 
                    this.generateQrCode(newLink);
                });
            }
        }
    },
    
    mounted() {
        this.detectarTemaSistema();
        this.generateLink();
        this.loadMembers(); 
    },
    methods: {
        // -----------------------------------------------------
        // LÓGICA DE FASTAPI: GENERAR LINK
        // -----------------------------------------------------
        async generateLink() {
            // ... (Lógica de generateLink, sin cambios) ...
            this.loading = true;
            this.error = null;
            const token = localStorage.getItem('accessToken');

            if (!token) {
                this.error = 'No autenticado. Por favor, inicie sesión.';
                this.loading = false;
                return;
            }

            try {
                const response = await fetch(`${API_BASE_URL}/api/proyectos/${this.proyectoId}/invitar`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.detail || 'Fallo al generar el link.');
                }
                
                this.invitationLink = data.link;

            } catch (err) {
                this.error = err.message || 'Error de conexión.';
            } finally {
                this.loading = false;
            }
        },
        
        // 🚨 4. MÉTODO PARA DIBUJAR EL QR EN EL CANVAS
        generateQrCode(url) {
            const canvas = document.getElementById('qr-code-canvas');
            if (canvas) {
                // Usamos la librería QRCode.js para dibujar en el elemento <canvas>
                QRCode.toCanvas(canvas, url, { errorCorrectionLevel: 'H', width: 200 }, function (error) {
                    if (error) console.error('Error generando QR:', error);
                });
            }
        },
        
        // -----------------------------------------------------
        // LÓGICA DE INTERFAZ: COPIAR
        // -----------------------------------------------------
        copyLink() {
            const input = this.$refs.linkInput;
            input.select();
            document.execCommand('copy'); 
            
            this.copySuccess = true;
            setTimeout(() => {
                this.copySuccess = false;
            }, 3000);
        },
        // -----------------------------------------------------
        // LÓGICA DE TEMA Y MIEMBROS
        // -----------------------------------------------------
        detectarTemaSistema() {
            if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
                this.isDark = true;
            } else {
                this.isDark = false;
            }
        },
       // 🚨 FUNCIÓN PARA REMOVER MIEMBRO (Funcional)
async removeMember(userId) {
    if (!confirm(`¿Estás seguro de que quieres remover el acceso al usuario ID ${userId}?`)) {
        return;
    }

    const token = localStorage.getItem('accessToken');
    if (!token) return; // No debería pasar si el modal está abierto

    try {
        const response = await fetch(`${API_BASE_URL}/api/proyectos/${this.proyectoId}/miembros/${userId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) {
            const errorData = await response.json();
            alert(`Error: ${errorData.detail || 'Fallo al remover miembro.'}`);
            return;
        }

        // Si es exitoso, actualiza la lista localmente
        this.members = this.members.filter(m => m.usuario_id !== userId);
        alert(`Usuario removido exitosamente.`);

    } catch (err) {
        console.error("Error al eliminar miembro:", err);
        alert('Error de conexión al intentar remover el miembro.');
    }
},
        async loadMembers() {
            const token = localStorage.getItem('accessToken');
            if (!token || !this.proyectoId) return;

            try {
                const response = await fetch(`${API_BASE_URL}/api/proyectos/${this.proyectoId}/miembros`, {
                    method: 'GET',
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                
                if (!response.ok) { throw new Error('No se pudo cargar la lista de miembros.'); }
                
                const data = await response.json();
                this.members = data; 
                
            } catch (err) {
                console.error("Error al cargar miembros:", err);
            }
        },
    }
}
</script>

<style scoped lang="scss">
// ----------------------------------------
// VARIABLES DE LA PALETA
// ----------------------------------------
// $PRIMARY-PURPLE: #8A2BE2;
// $SUCCESS-COLOR: #1ABC9C;
// $BLUE-MIDNIGHT: #1A1A2E;
// $LIGHT-TEXT: #E4E6EB;
// $DARK-TEXT: #333333;
// $SUBTLE-BG-DARK: #2B2B40; 
// $SUBTLE-BG-LIGHT: #FFFFFF;
// $LIGHT-TEXT: #E4E6EB;     // También es necesaria
// $WHITE-SOFT: #F7F9FC;     // 🚨 Esta es la variable que faltaba

// ----------------------------------------
// BASE DEL MODAL
// ----------------------------------------
.modal-compartir {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background-color: rgba(0, 0, 0, 0.6);
    display: flex; justify-content: center; align-items: center;
    z-index: 9999;
}

.modal-contenido {
    width: 90%; max-width: 550px;
    border-radius: 15px; padding: 25px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
    transition: background-color 0.3s;
}

.modal-header {
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 20px;
    h2 { font-size: 1.5rem; }
}

.btn-cerrar {
    background: none; border: none; font-size: 1.8rem; cursor: pointer;
    opacity: 0.7; transition: opacity 0.2s;
    &:hover { opacity: 1; }
}

// ----------------------------------------
// ESTILOS DE CONTENIDO
// ----------------------------------------

.link-generation-section {
    margin-bottom: 30px;
    h3 { font-size: 1.1rem; margin-bottom: 10px; font-weight: 600; }
}

.link-box {
    display: flex; gap: 10px;
    .form-control {
        flex-grow: 1; padding: 10px; border-radius: 8px; border: 1px solid;
        font-size: 0.9rem; background-color: rgba($PRIMARY-PURPLE, 0.05);
        cursor: text;
    }
    .btn-copy {
        background-color: $PRIMARY-PURPLE; color: white; border: none;
        padding: 10px 15px; border-radius: 8px; cursor: pointer;
        transition: background-color 0.2s;
        &:disabled { opacity: 0.5; cursor: not-allowed; }
        i { font-size: 1.1rem; }
    }
}

.link-status {
    font-size: 0.85rem; margin-top: 10px; color: $SUCCESS-COLOR;
}

.user-management-section {
    h4 { font-size: 1.1rem; margin-bottom: 15px; border-bottom: 1px solid; padding-bottom: 5px; }
}
.user-list {
    list-style: none; 
    padding: 0;
    
    .user-item {
        display: flex; 
        align-items: center;
        padding: 10px 15px; 
        margin-bottom: 5px;
        border-radius: 8px;
        transition: background-color 0.2s;
        
        // 🚨 ÍCONOS Y TEXTO
        i { margin-right: 10px; color: $PRIMARY-PURPLE; font-size: 1.1rem; }
        .member-name { font-weight: 600; margin-right: 5px; }
        .member-role { font-size: 0.9rem; opacity: 0.7; }

        // 🚨 PROPIETARIO (Estilo de distinción)
        &.owner { 
            background-color: rgba($SUCCESS-COLOR, 0.1); 
            border-left: 3px solid $SUCCESS-COLOR;
            padding-left: 12px;
        }
    }
    
    // 🚨 Botón de Remover (La X)
    .btn-remove {
        margin-left: auto; /* Mueve el botón al extremo derecho */
        background: none; 
        border: none; 
        color: #ff6347; /* Color de peligro */
        cursor: pointer; 
        opacity: 0.7;
        padding: 5px;

        &:hover { 
            opacity: 1; 
            color: #ff0000;
        }
    }
}

// ----------------------------------------
// TEMAS (DARK/LIGHT)
// ----------------------------------------
// TEMAS (Asegurar el contraste del botón de remover en modo oscuro)
.theme-dark {
    // ...
    .user-item {
        color: $LIGHT-TEXT;
        &:hover {
            background-color: rgba($LIGHT-TEXT, 0.05);
        }
    }
    .user-list .btn-remove {
        color: #ff6347;
    }
}
// MODO OSCURO
.theme-dark {
    background-color: $SUBTLE-BG-DARK;
    color: $LIGHT-TEXT;
    
    .btn-cerrar { color: $LIGHT-TEXT; }
    .form-control {
        background-color: $BLUE-MIDNIGHT;
        color: $LIGHT-TEXT;
        border-color: rgba($LIGHT-TEXT, 0.2);
    }
    .user-management-section h4 { border-bottom-color: rgba($LIGHT-TEXT, 0.3); }
}

// MODO CLARO
.theme-light {
    background-color: $SUBTLE-BG-LIGHT;
    color: $DARK-TEXT;
    
    .btn-cerrar { color: $DARK-TEXT; }
    .form-control {
        background-color: $WHITE-SOFT;
        color: $DARK-TEXT;
        border-color: #ddd;
    }
    .user-management-section h4 { border-bottom-color: #ddd; }
}
</style>