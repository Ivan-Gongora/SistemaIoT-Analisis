<template>
  <div class="modal-compartir" @click.self="$emit('cerrar')">
    <div class="modal-contenido" :class="{ 'theme-dark': isDark, 'theme-light': !isDark }">
      <div class="modal-header">
        <h2>Gestión de Acceso al Proyecto</h2>
        <button @click="$emit('cerrar')" class="btn-cerrar">&times;</button>
      </div>

      <div class="modal-body">
        
        <div class="section-invite">
            <h3>Invitar Nuevo Miembro</h3>
            <div class="invite-controls">
                <div class="role-select-group">
                    <label>Rol del Invitado:</label>
                    <select v-model="selectedRoleId" class="form-control role-select">
                        <option :value="3">Observador (Solo ver)</option>
                        <option :value="4">Colaborador (Ver y Editar)</option>
                    </select>
                </div>
                
                <button @click="generateLink" class="btn-generate" :disabled="loading">
                    <span v-if="loading"><i class="bi bi-arrow-clockwise fa-spin"></i></span>
                    <span v-else>Generar Link</span>
                </button>
            </div>

            <div class="link-result-box" v-if="invitationLink">
                <p class="link-instruction">Comparte este link (expira en 24h):</p>
                <div class="link-input-group">
                    <input type="text" :value="invitationLink" readonly ref="linkInput" class="form-control link-input" />
                    <button @click="copyLink" class="btn-copy" title="Copiar">
                        <i :class="copySuccess ? 'bi bi-check-lg' : 'bi bi-clipboard'"></i>
                    </button>
                </div>
                
                <button @click="showQr = !showQr" class="btn-qr-toggle">
                    <i class="bi bi-qr-code"></i> {{ showQr ? 'Ocultar QR' : 'Ver QR' }}
                </button>
                 <div v-if="showQr" class="qr-box">
                    <canvas id="qr-code-canvas"></canvas>
                </div>
            </div>
            
            <div v-if="error" class="alert-error mt-2">{{ error }}</div>
        </div>

        <hr class="divider">

        <div class="section-members">
            <h4>Miembros del Equipo ({{ members.length }})</h4>
            
            <div class="member-list-container">
                <ul class="user-list">
                    <li v-if="members.length === 0" class="empty-members">
                        Solo tú tienes acceso a este proyecto.
                    </li>
                    
                    <li v-for="member in members" :key="member.usuario_id" class="user-item" :class="{ 'is-owner': member.nombre_rol === 'Propietario' }">
                        <div class="user-info">
                            <div class="user-avatar">
                                <i class="bi bi-person-fill"></i>
                            </div>
                            <div class="user-text">
                                <span class="member-name">{{ member.nombre_usuario }}</span>
                                <span class="member-role-badge" :class="getRoleClass(member.nombre_rol)">
                                    {{ member.nombre_rol }}
                                </span>
                            </div>
                        </div>
                        
                        <button 
                            v-if="member.nombre_rol !== 'Propietario'"
                            @click="removeMember(member.usuario_id)" 
                            class="btn-remove-member" 
                            title="Revocar acceso"
                        >
                            <i class="bi bi-trash"></i>
                        </button>
                    </li>
                </ul>
            </div>
        </div>

      </div>
    </div>
  </div>
</template>


<script>
import QRCode from 'qrcode'; 



export default {
    name: 'ModalCompartir',
    props: {
        proyectoId: { type: Number, required: true }
    },
    data() {
        return {
            isDark: false,
            loading: false,
            error: null,
            invitationLink: '',
            copySuccess: false,
            members: [],
            showQr: false,
            selectedRoleId: 3,
        };
    },
    
    // 🚨 3. WATCHERS: Detecta el cambio en el link o en el botón de Mostrar QR
    watch: {
        showQr(newValue) {
            if (newValue && this.invitationLink) {
                this.$nextTick(() => { this.generateQrCode(this.invitationLink); });
            }
        },
        invitationLink(newLink) {
            if (this.showQr && newLink) {
                this.$nextTick(() => { this.generateQrCode(newLink); });
            }
        }
    },
    mounted() {
        this.detectarTemaSistema();
        this.loadMembers(); // Cargar la lista al abrir
    },
    methods: {
        // -----------------------------------------------------
        // LÓGICA DE FASTAPI: GENERAR LINK
        // -----------------------------------------------------
        async generateLink() {
            this.loading = true;
            this.error = null;
            this.invitationLink = ''; // Limpiar anterior
            this.showQr = false;
            
            const token = localStorage.getItem('accessToken');
            if (!token) return;

            try {
                // 🚨 ENVIAMOS EL ROL SELECCIONADO AL BACKEND
                // Nota: Necesitarás actualizar tu endpoint para aceptar ?rol_id=...
                const url = new URL(`${API_BASE_URL}/api/proyectos/${this.proyectoId}/invitar`);
                url.searchParams.append('rol_id', this.selectedRoleId);

                const response = await fetch(url.toString(), {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                const data = await response.json();
                if (!response.ok) throw new Error(data.detail || 'Fallo al generar link.');
                
                this.invitationLink = data.link;

            } catch (err) {
                this.error = err.message;
            } finally {
                this.loading = false;
            }
        },
        
        // 🚨 4. MÉTODO PARA DIBUJAR EL QR EN EL CANVAS
        async copyLink() {
        try {
            // 🚨 SOLUCIÓN: Usar navigator.clipboard.writeText
            // No necesitamos seleccionar el texto del input ($refs), 
            // podemos pasarle directamente la variable del texto.
            await navigator.clipboard.writeText(this.invitationLink);
            
            this.copySuccess = true;
            setTimeout(() => {
                this.copySuccess = false;
            }, 2000);
            
        } catch (err) {
            console.error('Error al copiar al portapapeles:', err);
            alert('No se pudo copiar el link automáticamente.');
        }
    },
        
        // // -----------------------------------------------------
        // // LÓGICA DE INTERFAZ: COPIAR
        // // -----------------------------------------------------
        // copyLink() {
        //     const input = this.$refs.linkInput;
        //     input.select();
        //     document.execCommand('copy'); 
            
        //     this.copySuccess = true;
        //     setTimeout(() => {
        //         this.copySuccess = false;
        //     }, 3000);
        // },
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
       //  FUNCIÓN PARA REMOVER MIEMBRO (Funcional)
async removeMember(userId) {
            if (!confirm('¿Revocar acceso a este usuario?')) return;
            
            const token = localStorage.getItem('accessToken');
            try {
                const response = await fetch(`${API_BASE_URL}/api/proyectos/${this.proyectoId}/miembros/${userId}`, {
                    method: 'DELETE',
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                if (!response.ok) {
                    const data = await response.json();
                    throw new Error(data.detail || 'Error al remover.');
                }
                
                // Actualizar lista localmente
                this.members = this.members.filter(m => m.usuario_id !== userId);

            } catch (err) {
                alert(err.message);
            }
        },

        async loadMembers() {
            const token = localStorage.getItem('accessToken');
            try {
                const response = await fetch(`${API_BASE_URL}/api/proyectos/${this.proyectoId}/miembros`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (response.ok) {
                    this.members = await response.json();
                }
            } catch (err) {
                console.error(err);
            }
        },
        getRoleClass(roleName) {
            if (roleName === 'Propietario') return 'badge-owner';
            if (roleName === 'Colaborador') return 'badge-collab';
            return 'badge-observer';
        }
    }
}
</script>
<style scoped lang="scss">
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
    h2 { font-size: 1.3rem; margin: 0; }
}

.btn-cerrar {
    background: none; border: none; font-size: 1.8rem; cursor: pointer;
    opacity: 0.7; transition: opacity 0.2s;
    &:hover { opacity: 1; }
}

// ----------------------------------------
// SECCIÓN 1: INVITAR (Generar Link)
// ----------------------------------------

.section-invite {
    h3 { font-size: 0.95rem; font-weight: 600; margin-bottom: 10px; color: $GRAY-COLD; text-transform: uppercase; letter-spacing: 0.5px; }
}

.invite-controls {
    display: flex;
    gap: 10px;
    align-items: flex-end; /* Alinea el botón con el input */
    margin-bottom: 15px;
    
    .role-select-group {
        flex-grow: 1;
        label { display: block; font-size: 0.85rem; margin-bottom: 5px; font-weight: 500; }
    }
    
    .form-control {
        width: 100%; padding: 10px; border-radius: 8px; border: 1px solid;
        font-size: 0.95rem;
        height: 42px; /* Altura fija para alinear con el botón */
        box-sizing: border-box;
    }
    
    .btn-generate {
        background-color: $PRIMARY-PURPLE; color: white; border: none;
        padding: 0 20px; border-radius: 8px; cursor: pointer;
        font-weight: 600; height: 42px; /* Misma altura que el input */
        transition: opacity 0.2s;
        white-space: nowrap;
        
        &:disabled { opacity: 0.7; cursor: not-allowed; }
        &:hover:not(:disabled) { opacity: 0.9; }
    }
}

// CAJA DE RESULTADO (Link + QR)
.link-result-box {
    background-color: rgba($PRIMARY-PURPLE, 0.05);
    padding: 15px; border-radius: 10px;
    border: 1px dashed rgba($PRIMARY-PURPLE, 0.3);
    margin-top: 15px;
    
    .link-instruction { font-size: 0.85rem; margin-bottom: 8px; color: $GRAY-COLD; margin-top: 0; }
    
    .link-input-group {
        display: flex; gap: 5px; align-items: center;
        background: rgba(255,255,255,0.5); /* Fondo sutil para el input */
        padding: 5px 10px; border-radius: 6px;

        .link-input { 
            flex-grow: 1; background: transparent; border: none; 
            font-family: monospace; color: $PRIMARY-PURPLE; font-weight: 600; font-size: 0.9rem;
            outline: none;
        }
        .btn-copy { 
            background: none; border: none; color: $PRIMARY-PURPLE; cursor: pointer; font-size: 1.1rem; padding: 5px;
            &:hover { transform: scale(1.1); }
        }
    }
    
    .btn-qr-toggle {
        margin-top: 10px; font-size: 0.8rem; background: none; border: none; 
        color: $GRAY-COLD; cursor: pointer; text-decoration: underline;
        display: block; width: 100%; text-align: center;
        &:hover { color: $PRIMARY-PURPLE; }
    }
    .qr-box { margin-top: 10px; text-align: center; }
}

.divider { border: 0; border-top: 1px solid rgba(150,150,150, 0.2); margin: 25px 0; }

// ----------------------------------------
// SECCIÓN 2: LISTA DE MIEMBROS
// ----------------------------------------
.section-members {
    h4 { font-size: 1rem; font-weight: 600; margin-bottom: 15px; }
}

.member-list-container {
    max-height: 250px; overflow-y: auto; // Scroll si hay muchos usuarios
    padding-right: 5px; // Espacio para el scrollbar
}

.user-list {
    list-style: none; padding: 0; margin: 0;
}

.empty-members {
    font-size: 0.9rem; color: $GRAY-COLD; font-style: italic; text-align: center; padding: 20px;
}

.user-item {
    display: flex; justify-content: space-between; align-items: center;
    padding: 10px 12px; border-radius: 8px; margin-bottom: 8px;
    transition: background 0.2s;
    border: 1px solid transparent;
    
    &:hover { background-color: rgba(0,0,0,0.03); }
    
    .user-info { display: flex; align-items: center; gap: 12px; }
    
    .user-avatar {
        width: 38px; height: 38px; background-color: rgba($PRIMARY-PURPLE, 0.1); color: $PRIMARY-PURPLE;
        border-radius: 50%; display: flex; justify-content: center; align-items: center;
        font-size: 1.1rem;
    }
    
    .user-text {
        display: flex; flex-direction: column;
        line-height: 1.3;
        .member-name { font-weight: 600; font-size: 0.95rem; }
    }
    
    // BADGES DE ROL (Usamos tus variables de color)
    .member-role-badge {
        font-size: 0.7rem; padding: 1px 6px; border-radius: 4px; font-weight: 600; text-transform: uppercase;
        display: inline-block; width: fit-content;
        
        &.badge-owner { color: $SUCCESS-COLOR; background-color: rgba($SUCCESS-COLOR, 0.1); border: 1px solid rgba($SUCCESS-COLOR, 0.2); }
        // Usamos una variante de azul para colaborador, si no tienes variable usa un hex directo o $INFO-COLOR si existe
        &.badge-collab { color: #3498DB; background-color: rgba(#3498DB, 0.1); border: 1px solid rgba(#3498DB, 0.2); }
        &.badge-observer { color: $GRAY-COLD; background-color: rgba($GRAY-COLD, 0.1); border: 1px solid rgba($GRAY-COLD, 0.2); }
    }
    
    .btn-remove-member {
        background: none; border: none; color: $DANGER-COLOR; opacity: 0.5; cursor: pointer; padding: 5px;
        font-size: 1rem; transition: all 0.2s;
        &:hover { opacity: 1; background-color: rgba($DANGER-COLOR, 0.1); border-radius: 50%; }
    }
    
    // Estilo especial para el item del propietario en la lista
    &.is-owner {
        border-color: rgba($SUCCESS-COLOR, 0.2);
        background-color: rgba($SUCCESS-COLOR, 0.02);
    }
}

// ----------------------------------------
// TEMAS (DARK/LIGHT)
// ----------------------------------------

// TEMA OSCURO
.theme-dark {
    .modal-contenido { background-color: $BG-CARD-DARK; color: $LIGHT-TEXT; }
    .btn-cerrar { color: $LIGHT-TEXT; }
    
    .form-control { 
        background-color: $DARK-INPUT-BG; border-color: rgba(255,255,255,0.1); color: white; 
        &:focus { border-color: $PRIMARY-PURPLE; }
    }
    
    .link-result-box .link-input-group { background-color: rgba(255,255,255,0.05); }
    
    .user-item:hover { background-color: rgba(255,255,255,0.05); }
    
    .alert-error { color: $DANGER-COLOR; }
}

// TEMA CLARO
.theme-light {
    .modal-contenido { background-color: $LIGHT-BG-CARD; color: $DARK-TEXT; }
    .btn-cerrar { color: $DARK-TEXT; }
    
    .form-control { 
        background-color: $LIGHT-INPUT-BG; border-color: $LIGHT-BORDER; color: $DARK-TEXT;
        &:focus { border-color: $PRIMARY-PURPLE; }
    }
    
    .link-result-box .link-input-group { background-color: white; border: 1px solid $LIGHT-BORDER; }
    
    .alert-error { color: $DANGER-COLOR; }
}
</style>
<!-- <style scoped lang="scss">
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
</style> -->