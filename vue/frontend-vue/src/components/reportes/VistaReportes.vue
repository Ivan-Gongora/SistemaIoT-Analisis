<template>
  <div class="plataforma-layout" :class="{ 'theme-dark': isDark, 'theme-light': !isDark }">
    <BarraLateralPlataforma :is-open="isSidebarOpen" />
    <div class="plataforma-contenido" :class="{ 'shifted': isSidebarOpen }">
      <EncabezadoPlataforma 
        titulo="Reportes y Análisis"
        subtitulo="Visualización de datos históricos de los sensores"
        @toggle-sidebar="toggleSidebar" 
        :is-sidebar-open="isSidebarOpen"
      />

      <div class="reportes-contenido">
        
        <div class="selector-container" :class="{ 'theme-dark': isDark }">
            <div class="form-group">
                <label>1. Seleccione un Proyecto:</label>
                <select v-model="proyectoSeleccionadoId" @change="cargarDispositivos" class="form-control">
                    <option :value="null" disabled>Cargando proyectos...</option>
                    <option v-for="p in proyectos" :key="p.id" :value="p.id">{{ p.nombre }}</option>
                </select>
                <div v-if="loadingProyectos" class="loading-message">Cargando proyectos...</div>
            </div>
            
            <div class="form-group">
                <label>2. Seleccione un Dispositivo:</label>
                <select v-model="dispositivoSeleccionadoId" @change="cargarCampos" class="form-control" :disabled="!proyectoSeleccionadoId || loadingDispositivos">
                    <option :value="null" disabled>
                        {{ loadingDispositivos ? 'Cargando dispositivos...' : 'Seleccione un proyecto primero' }}
                    </option>
                    <option v-for="d in dispositivos" :key="d.id" :value="d.id">{{ d.nombre }}</option>
                </select>
                <div v-if="loadingDispositivos" class="loading-message">Cargando dispositivos...</div>
                <div v-if="!loadingDispositivos && proyectoSeleccionadoId && dispositivos.length === 0" class="no-data-message">
                    No hay dispositivos.
                </div>
            </div>

            <div class="form-group">
                <label>3. Seleccione un Campo:</label>
                <select v-model="campoSeleccionadoId" @change="seleccionarCampo" class="form-control" :disabled="!dispositivoSeleccionadoId || loadingCampos">
                    <option :value="null" disabled>
                        {{ loadingCampos ? 'Cargando campos...' : 'Seleccione un dispositivo primero' }}
                    </option>
                   <option v-for="c in campos" :key="c.id" :value="c.id">
    {{ c.nombre }} ({{ c.simbolo_unidad || 'N/A' }})
</option>
                </select>
                <div v-if="loadingCampos" class="loading-message">Cargando campos...</div>
                <div v-if="!loadingCampos && dispositivoSeleccionadoId && campos.length === 0" class="no-data-message">
                    No hay campos.
                </div>
            </div>
        </div>

        <div v-if="errorCampos" class="alert-error">{{ errorCampos }}</div>
        
        <div class="charts-grid" v-if="campoSeleccionadoId">
            <GraficoHistorico
                :key="campoSeleccionadoId" :campo-id="campoSeleccionadoId"
                :titulo="campoSeleccionadoNombre"
                :simbolo-unidad="campoSeleccionadoSimbolo"
                :is-dark="isDark"
            />
        </div>
        
        <div v-if="!loadingCampos && dispositivoSeleccionadoId && campos.length === 0 && !campoSeleccionadoId" class="alert-empty-data">
            Este dispositivo no tiene campos de medición registrados.
        </div>
        <div v-else-if="!campoSeleccionadoId && !loadingProyectos && !loadingDispositivos && proyectos.length > 0 && dispositivos.length > 0 && campos.length > 0" class="alert-info">
             Seleccione un campo para ver el gráfico.
        </div>

      </div>
    </div>
  </div>
</template>

<script>
// Componentes de Layout
import BarraLateralPlataforma from '../plataforma/BarraLateralPlataforma.vue';
import EncabezadoPlataforma from '../plataforma/EncabezadoPlataforma.vue';
// Componente hijo
import GraficoHistorico from './GraficoHistorico.vue';

const API_BASE_URL = 'http://127.0.0.1:8001';

export default {
    name: 'VistaReportes',
    components: {
        BarraLateralPlataforma,
        EncabezadoPlataforma,
        GraficoHistorico
    },
    data() {
        return {
            isDark: false, 
            isSidebarOpen: true, 
            
            // Listas para los dropdowns
            proyectos: [],
            dispositivos: [],
            campos: [],
            
            // Estados de selección
            proyectoSeleccionadoId: null,
            dispositivoSeleccionadoId: null,
            campoSeleccionadoId: null,       // 🚨 NUEVO: ID del campo seleccionado para el gráfico
            campoSeleccionadoNombre: '',     // 🚨 NUEVO: Nombre del campo seleccionado
            campoSeleccionadoSimbolo: '',    // 🚨 NUEVO: Símbolo del campo seleccionado
            // Estados de Carga
            loadingProyectos: true,
            loadingDispositivos: false,
            loadingCampos: false,
            errorCampos: null,
            error: null, // 🚨 Añadir estado de error general
        };
    },
    mounted() {
        this.cargarProyectos();
        this.detectarTemaSistema();
        if (window.matchMedia) {
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', this.handleThemeChange);
    }
    },beforeUnmount() { 
    if (window.matchMedia) {
      window.matchMedia('(prefers-color-scheme: dark)').removeEventListener('change', this.handleThemeChange);
    }
  },
    methods: {
        // --- Carga de Dropdowns ---
       // 🚨 MÉTODO CORREGIDO
        async cargarProyectos() {
            this.loadingProyectos = true;
            this.error = null; // Limpiar errores previos
            const token = localStorage.getItem('accessToken');

            // 🚨 SOLUCIÓN: Obtener el ID del usuario desde el objeto 'resultado' guardado
            let usuarioId = null;
            const resultadoString = localStorage.getItem('resultado');
            
            if (resultadoString) {
                const resultado = JSON.parse(resultadoString);
                if (resultado && resultado.usuario && resultado.usuario.id) {
                    usuarioId = resultado.usuario.id;
                }
            }

            // 🚨 Validar que el ID exista ANTES de hacer el fetch
            if (!token || !usuarioId) { 
                this.error = "Error de autenticación. No se pudo encontrar el ID de usuario.";
                this.loadingProyectos = false;
                this.$router.push('/'); // Redirigir si no hay sesión
                return; 
            }

            try {
                // La URL ahora tendrá un ID numérico (ej: /api/proyectos/usuario/1)
                const response = await fetch(`${API_BASE_URL}/api/proyectos/usuario/${usuarioId}`, { 
                    headers: { 'Authorization': `Bearer ${token}` } 
                });
                
                if (response.status === 404) {
                    this.proyectos = [];
                    throw new Error('No se encontraron proyectos para este usuario.');
                }
                if (!response.ok) { throw new Error('Fallo al cargar proyectos.'); }
                
                this.proyectos = await response.json();
                
                // Mejora de UX: Seleccionar el primer proyecto automáticamente
                if (this.proyectos.length > 0) {
                this.proyectoSeleccionadoId = this.proyectos[0].id;
                await this.cargarDispositivos(); // Usar await para esperar la carga
                }
                
            } catch (err) {
                console.error(err);
                this.error = err.message; // Mostrar error en la UI
            } finally {
                this.loadingProyectos = false;
            }
        },

        async cargarDispositivos() {
            this.loadingDispositivos = true;
            this.dispositivos = []; 
            this.campos = []; // Limpiar campos también
            this.dispositivoSeleccionadoId = null; // Reiniciar
            this.campoSeleccionadoId = null; // 🚨 Reiniciar también el campo seleccionado
            this.campoSeleccionadoNombre = '';
            this.campoSeleccionadoSimbolo = '';
            
            const token = localStorage.getItem('accessToken');
            if (!this.proyectoSeleccionadoId || !token) {
                this.loadingDispositivos = false;
                return;
            }
            
            try {
                const response = await fetch(`${API_BASE_URL}/api/dispositivos/proyecto/${this.proyectoSeleccionadoId}`, { 
                    headers: { 'Authorization': `Bearer ${token}` } 
                });
                if (response.status === 404) { 
                    this.dispositivos = []; 
                } else if (response.ok) { 
                    this.dispositivos = await response.json(); 
                }
                
                // UX: Seleccionar el primer dispositivo automáticamente
                if (this.dispositivos.length > 0) {
                    this.dispositivoSeleccionadoId = this.dispositivos[0].id;
                    await this.cargarCampos(); // Usar await para esperar la carga
                }

            } catch (err) {
                console.error(err);
            } finally {
                this.loadingDispositivos = false;
            }
        },
  
     async cargarCampos() {
            this.loadingCampos = true;
            this.errorCampos = null;
            this.campos = [];
            this.campoSeleccionadoId = null; // 🚨 Reiniciar campo seleccionado
            this.campoSeleccionadoNombre = '';
            this.campoSeleccionadoSimbolo = '';
            
            const token = localStorage.getItem('accessToken');
            if (!this.dispositivoSeleccionadoId || !token) {
                this.loadingCampos = false;
                return;
            }

            try {
                const sensoresResponse = await fetch(`${API_BASE_URL}/api/sensores/dispositivo/${this.dispositivoSeleccionadoId}`, { 
                    headers: { 'Authorization': `Bearer ${token}` } 
                });
                if (sensoresResponse.status === 404) { this.campos = []; this.loadingCampos = false; return; }
                
                const sensores = await sensoresResponse.json();
                let todosLosCampos = [];

                for (const sensor of sensores) {
                    const camposResponse = await fetch(`${API_BASE_URL}/api/sensores/${sensor.id}/campos`, { 
                        headers: { 'Authorization': `Bearer ${token}` } 
                    });
                    console.log(camposResponse)
                    if (camposResponse.ok) {
                        const camposData = await camposResponse.json();
                         console.log(camposData)
                        const camposMapeados = camposData.map(campo => ({
                            id: campo.id,
                            nombre: campo.nombre,
                            tipo_valor: campo.tipo_valor,
                            simbolo_unidad: campo.simbolo_unidad ? campo.simbolo_unidad : '', // 👈 Esto debe existir si usas la versión aplanada 
                            magnitud_tipo: campo.unidad ? campo.unidad.magnitud_tipo : 'Valor sin Unidad',
                        }));
                        todosLosCampos.push(...camposMapeados);
                    }
                }
                this.campos = todosLosCampos;

                // UX: Seleccionar el primer campo automáticamente para mostrar el gráfico
                if (this.campos.length > 0) {
                    this.campoSeleccionadoId = this.campos[0].id;
                    this.campoSeleccionadoNombre = this.campos[0].nombre;
                    // 🚨 Asegurar la inicialización correcta:
                    this.campoSeleccionadoSimbolo = this.campos[0].simbolo_unidad || ''; 
                }

            } catch (err) {
                console.error("Error al cargar campos:", err);
                this.errorCampos = 'Error al cargar los campos del dispositivo.';
            } finally {
                this.loadingCampos = false;
            }
        },
      seleccionarCampo() {
    const campo = this.campos.find(c => c.id === this.campoSeleccionadoId);
    if (campo) {
        this.campoSeleccionadoNombre = campo.nombre;
        // 🚨 Usamos la propiedad aplanada (simbolo_unidad)
        this.campoSeleccionadoSimbolo = campo.simbolo_unidad || ''; 
    } else {
        this.campoSeleccionadoNombre = '';
        this.campoSeleccionadoSimbolo = '';
    }
},
        // 🚨 NUEVO MÉTODO: Para cuando se selecciona un campo manualmente
        // VistaReportes.vue <script>



        // --- Layout y Tema ---
        toggleSidebar() { this.isSidebarOpen = !this.isSidebarOpen; },
    handleThemeChange(event) { this.isDark = event.matches; },
    
    // 🚨 FUNCIÓN FALTANTE
    detectarTemaSistema() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            this.isDark = true;
        } else {
            this.isDark = false;
        }
    }
    }
};
</script>
<style scoped lang="scss">
// ----------------------------------------
// VARIABLES DE PALETA (Copiadas de tu Tarjeta)
// ----------------------------------------
$PRIMARY-PURPLE: #8A2BE2;
$SUCCESS-COLOR: #1ABC9C;
$GRAY-COLD: #99A2AD;
$LIGHT-TEXT: #E4E6EB;
$DARK-TEXT: #333333;
$SUBTLE-BG-DARK: #2B2B40; // Fondo de Tarjeta Oscura
$BLUE-MIDNIGHT: #1A1A2E; // Fondo de Inputs Oscuros
$SUBTLE-BG-LIGHT: #FFFFFF;
$WHITE-SOFT: #F7F9FC; 
$DANGER-COLOR: #e74c3c;
$WIDTH-SIDEBAR: 280px; 
$WIDTH-CLOSED: 80px;
$DARK-BG-CONTRAST: #1E1E30; 


// ----------------------------------------
// LAYOUT PRINCIPAL (CORRECCIÓN CRÍTICA DE FONDO)
// ----------------------------------------
.plataforma-layout {
    display: flex;
    min-height: 100vh;
    transition: background-color 0.3s;
}

.plataforma-contenido {
    margin-left: $WIDTH-CLOSED;
    flex-grow: 1;
    padding: 0;
    transition: margin-left 0.3s ease-in-out;
    
    &.shifted {
        margin-left: $WIDTH-SIDEBAR;
    }
}

.reportes-contenido {
    /* Mantiene el espaciado lateral de 40px */
    padding: 0 40px 40px 40px;
}

// ----------------------------------------
// CONTROLES Y GRÁFICOS
// ----------------------------------------

.selector-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 20px;
    padding: 25px; 
    border-radius: 12px;
    margin-bottom: 30px;
    transition: background-color 0.3s;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}
.form-group {
    label { 
        font-weight: 600; 
        margin-bottom: 8px; 
        display: block; 
        white-space: nowrap;
    }
    .form-control {
        width: 100%;
        padding: 10px 15px;
        border-radius: 8px;
        font-size: 1rem;
        appearance: none; 
        background-repeat: no-repeat;
        background-position: right 15px center;
        background-size: 10px;
    }
    .loading-message, .no-data-message {
        font-size: 0.85rem;
        color: $GRAY-COLD;
        margin-top: 5px;
        font-style: italic;
    }
}

.charts-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 20px;
}
.alert-empty-data, .alert-info, .alert-error {
    text-align: center;
    padding: 20px;
    border-radius: 8px;
    margin-top: 20px;
    font-size: 1.1rem;
    font-weight: 500;
}
.alert-empty-data {
    background-color: #ffe0b2;
    color: #e65100;
}
.alert-info {
    background-color: #bbdefb;
    color: #0d47a1;
}
.alert-error {
    background-color: #ffcdd2;
    color: $DANGER-COLOR;
}

/* ----------------------------------------
   TEMAS
   ---------------------------------------- */

/* TEMA CLARO */
.theme-light {
    background-color: $WHITE-SOFT; /* Fondo de la página */
    .selector-container {
        background-color: $SUBTLE-BG-LIGHT;
        color: $DARK-TEXT;
    }
    .form-control {
        background-color: $SUBTLE-BG-LIGHT;
        color: $DARK-TEXT;
        border: 1px solid #ccc;
    }
}

/* TEMA OSCURO */
.theme-dark {
    /* 🚨 CRÍTICO: Aplicar el fondo principal a toda el área de contenido */
    background-color: $DARK-BG-CONTRAST; 
    color: $LIGHT-TEXT;

    .plataforma-contenido {
        /* Asegura que el contenido también use el fondo principal */
        background-color: $DARK-BG-CONTRAST;
    }
    :global(.user-profile-card) { 
        background-color: $SUBTLE-BG-DARK !important;
        color: $LIGHT-TEXT !important;
        box-shadow: none;
    }
    .selector-container {
        background-color: $SUBTLE-BG-DARK; 
        color: $LIGHT-TEXT;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);

        .form-group label {
            color: $LIGHT-TEXT; 
        }
        
        .form-control {
            background-color: $BLUE-MIDNIGHT; 
            color: $LIGHT-TEXT;
            border: 1px solid rgba($LIGHT-TEXT, 0.2); 
            /* Reajustar la flecha para el modo oscuro */
            background-image: url('data:image/svg+xml;charset=UTF-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2212%22%20height%3D%2212%22%20viewBox%3D%220%200%2012%2012%22%3E%3Cpath%20fill%3D%22%23{$LIGHT-TEXT}%22%20d%3D%22M6%209L0%203h12z%22%2F%3E%3C%2Fsvg%3E');
        }
        .loading-message, .no-data-message {
            color: $GRAY-COLD;
        }
    }
}
</style>