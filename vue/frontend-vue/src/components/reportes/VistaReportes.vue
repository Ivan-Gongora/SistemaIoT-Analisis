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
              <option :value="null" disabled>
                {{ loadingProyectos ? 'Cargando proyectos...' : 'Seleccione un proyecto' }}
              </option>
              <option v-for="p in proyectos" :key="p.id" :value="p.id">{{ p.nombre }}</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>2. Seleccione un Dispositivo:</label>
            <select v-model="dispositivoSeleccionadoId" @change="cargarCamposYFechas" class="form-control" :disabled="!proyectoSeleccionadoId || loadingDispositivos">
              <option :value="null" disabled>
                {{ loadingDispositivos ? 'Cargando...' : 'Seleccione un proyecto' }}
              </option>
              <option v-for="d in dispositivos" :key="d.id" :value="d.id">{{ d.nombre }}</option>
            </select>
          </div>

          <div class="form-group-combined">
            <div class="form-group">
                <label>3. Fecha de Inicio:</label>
                <input 
                    type="date" 
                    class="form-control" 
                    v-model="fechaInicioSeleccionada"
                    :min="fechaMinimaDisponible" 
                    :max="fechaMaximaDisponible"
                    :disabled="loadingCampos || !dispositivoSeleccionadoId"
                >
            </div>
            <div class="form-group-time">
                <label>Hora Inicio:</label>
                <input 
                    type="time" 
                    class="form-control" 
                    v-model="horaInicioSeleccionada"
                    :disabled="loadingCampos || !dispositivoSeleccionadoId"
                >
            </div>
          </div>

          <div class="form-group-combined">
            <div class="form-group">
                <label>4. Fecha de Fin:</label>
                <input 
                    type="date" 
                    class="form-control" 
                    v-model="fechaFinSeleccionada"
                    :min="fechaMinimaDisponible" 
                    :max="fechaMaximaDisponible"
                    :disabled="loadingCampos || !dispositivoSeleccionadoId"
                >
            </div>
            <div class="form-group-time">
                <label>Hora Fin:</label>
                <input 
                    type="time" 
                    class="form-control" 
                    v-model="horaFinSeleccionada"
                    :disabled="loadingCampos || !dispositivoSeleccionadoId"
                >
            </div>
          </div>
          
          <div class="form-group">
            <label>5. Modo de Vista:</label>
            <select v-model="modoVista" class="form-control" :disabled="!dispositivoSeleccionadoId">
              <option value="multiple">Múltiples Gráficos (Separados)</option>
              <option value="combinado">Gráfico Combinado (Comparar)</option>
            </select>
          </div>

        </div> 
        <div class="campo-selector-container" :class="{ 'theme-dark': isDark }" v-if="campos.length > 0">
            <h4 class="selector-titulo">6. Seleccione los campos a graficar (1 o más)</h4>
            <div v-if="loadingCampos" class="loading-message">Cargando campos...</div>
            <div class="checkbox-grid">
                <div v-for="c in campos" :key="c.id" class="checkbox-item">
                    <input type="checkbox" :id="'campo-' + c.id" :value="c.id" v-model="camposSeleccionadosIds">
                    
                    <label :for="'campo-' + c.id">
                        <i :class="getIcon(c.magnitud_tipo)"></i> {{ c.nombre }} ({{ c.simbolo_unidad || 'N/A' }}) </label>

                </div>
            </div>
        </div>
        
        <div v-if="errorCampos" class="alert-error">{{ errorCampos }}</div>
        
        <div class="charts-grid-multiple" v-if="camposFiltrados.length > 0 && modoVista === 'multiple' && dateRange.inicio">
          <GraficoHistorico
            v-for="campo in camposFiltrados"
            :key="'sep-'+campo.id"
            :campo-id="campo.id"
            :titulo="campo.nombre"
            :fecha-inicio="dateRange.inicio" 
            :fecha-fin="dateRange.fin"
            :is-dark="isDark"
          />
        </div>
        
        <div class="charts-grid-single" v-else-if="camposFiltrados.length > 0 && modoVista === 'combinado' && dateRange.inicio">
          <GraficoCombinado
            :key="'comb-'+dispositivoSeleccionadoId" :campos="camposFiltrados"
            :fecha-inicio="dateRange.inicio"
            :fecha-fin="dateRange.fin"
            :is-dark="isDark"
          />
        </div>
        
        <div v-if="!loadingCampos && dispositivoSeleccionadoId && campos.length === 0" class="alert-empty-data">
          Este dispositivo no tiene campos de medición registrados.
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
import GraficoCombinado from './GraficoCombinado.vue'; 

// 🚨 CONSTANTE DE API RESTAURADA
// const API_BASE_URL = 'http://127.0.0.1:8001';

export default {
    name: 'VistaReportes',
    components: {
        BarraLateralPlataforma,
        EncabezadoPlataforma,
        GraficoHistorico,
        GraficoCombinado
    },
    data() {
        return {
            isDark: false, 
            isSidebarOpen: true, 
            proyectos: [],
            dispositivos: [],
            campos: [], // Todos los campos disponibles
            
            proyectoSeleccionadoId: null,
            dispositivoSeleccionadoId: null,
            camposSeleccionadosIds: [], // Array de IDs seleccionados

            // Estados para los selectores de fecha y hora
            fechaMinimaDisponible: null,
            fechaMaximaDisponible: null,
            fechaInicioSeleccionada: null,
            fechaFinSeleccionada: null,
            horaInicioSeleccionada: '00:00',
            horaFinSeleccionada: '23:59',

            modoVista: 'multiple',
            
            // Estados de Carga
            loadingProyectos: true,
            loadingDispositivos: false,
            loadingCampos: false,
            errorCampos: null,
            error: null,
        };
    },
    
    computed: {
        // Combina fecha y hora para la API
        dateRange() {
            if (!this.fechaInicioSeleccionada || !this.fechaFinSeleccionada) {
                return { inicio: null, fin: null };
            }
            
            try {
                // 1. Combinar la fecha y la hora local
                const inicioLocal = `${this.fechaInicioSeleccionada}T${this.horaInicioSeleccionada}:00`;
                const finLocal = `${this.fechaFinSeleccionada}T${this.horaFinSeleccionada}:00`;
                
                return {
                    inicio: inicioLocal, // Envía el string local
                    fin: finLocal
                };
            } catch (e) {
                console.error("Error al construir el rango de fecha/hora:", e);
                return { inicio: null, fin: null };
            }
        },
        
        // Filtra los campos a graficar
        camposFiltrados() {
            return this.campos.filter(c => this.camposSeleccionadosIds.includes(c.id));
        }
    },
    
    mounted() {
        this.cargarProyectos();
        this.detectarTemaSistema();
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', this.handleThemeChange);
        }
    },
    beforeUnmount() { 
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').removeEventListener('change', this.handleThemeChange);
        }
    },
    methods: {
        // --- Carga de Dropdowns ---
        async cargarProyectos() {
            this.loadingProyectos = true;
            this.error = null;
            const token = localStorage.getItem('accessToken');

            let usuarioId = null;
            const resultadoString = localStorage.getItem('resultado');
            
            if (resultadoString) {
                const resultado = JSON.parse(resultadoString);
                if (resultado && resultado.usuario && resultado.usuario.id) {
                    usuarioId = resultado.usuario.id;
                }
            }

            if (!token || !usuarioId) { 
                this.error = "Error de autenticación. No se pudo encontrar el ID de usuario.";
                this.loadingProyectos = false;
                this.$router.push('/');
                return; 
            }

            try {
                const response = await fetch(`${API_BASE_URL}/api/proyectos/usuario/${usuarioId}`, { 
                    headers: { 'Authorization': `Bearer ${token}` } 
                });
                
                if (response.status === 404) {
                    this.proyectos = [];
                    throw new Error('No se encontraron proyectos para este usuario.');
                }
                if (!response.ok) { throw new Error('Fallo al cargar proyectos.'); }
                
                this.proyectos = await response.json();
                
                if (this.proyectos.length > 0) {
                    this.proyectoSeleccionadoId = this.proyectos[0].id;
                    await this.cargarDispositivos(); 
                }
                
            } catch (err) {
                console.error(err);
                this.error = err.message;
            } finally {
                this.loadingProyectos = false;
            }
        },

        async cargarDispositivos() {
            this.loadingDispositivos = true;
            this.dispositivos = []; 
            this.campos = [];
            // 🚨 NO REINICIAMOS EL ID DEL PROYECTO
            this.dispositivoSeleccionadoId = null;
            this.camposSeleccionadosIds = [];
            this.fechaMinimaDisponible = null;
            this.fechaMaximaDisponible = null;
            
            const token = localStorage.getItem('accessToken');
            if (!this.proyectoSeleccionadoId || !token) {
                this.loadingDispositivos = false;
                return;
            }
            
            try {
                const response = await fetch(`${API_BASE_URL}/api/dispositivos/proyecto/${this.proyectoSeleccionadoId}`, { 
                    headers: { 'Authorization': `Bearer ${token}` } 
                });
                if (response.status === 404) { this.dispositivos = []; } 
                else if (response.ok) { this.dispositivos = await response.json(); }
                
                if (this.dispositivos.length > 0) {
                    this.dispositivoSeleccionadoId = this.dispositivos[0].id;
                    await this.cargarCamposYFechas();
                }
            } catch (err) {
                console.error(err);
            } finally {
                this.loadingDispositivos = false;
            }
        },
    
        // Se llama al cambiar el Dispositivo
        async cargarCamposYFechas() {
            await this.cargarCampos();
            await this.cargarRangoDeFechas();
        },

        // Carga la lista de checkboxes
        async cargarCampos() {
            this.loadingCampos = true;
            this.errorCampos = null;
            this.campos = [];
            this.camposSeleccionadosIds = [];
            
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
                    
                    if (camposResponse.ok) {
                        const camposData = await camposResponse.json();
                        todosLosCampos.push(...camposData); 
                    }
                }
                this.campos = todosLosCampos; 
                
            } catch (err) {
                console.error("Error al cargar campos:", err);
                this.errorCampos = 'Error al cargar los campos del dispositivo.';
            } finally {
                this.loadingCampos = false;
            }
        },
        
        // Obtiene el MIN y MAX de fechas para los calendarios
        async cargarRangoDeFechas() {
            const token = localStorage.getItem('accessToken');
            if (!this.dispositivoSeleccionadoId || !token) return;

            try {
                const response = await fetch(`${API_BASE_URL}/api/valores/rango-fechas-dispositivo/${this.dispositivoSeleccionadoId}`, { 
                    headers: { 'Authorization': `Bearer ${token}` } 
                });
                
                if (!response.ok) {
                    throw new Error('No se pudo obtener el rango de fechas.');
                }
                
                const rango = await response.json(); 
                
                if (rango.fecha_minima) {
                    this.fechaMinimaDisponible = rango.fecha_minima.split('T')[0];
                    this.fechaInicioSeleccionada = this.fechaMinimaDisponible;
                    this.horaInicioSeleccionada = '00:00';
                }
                if (rango.fecha_maxima) {
                    this.fechaMaximaDisponible = rango.fecha_maxima.split('T')[0];
                    this.fechaFinSeleccionada = this.fechaMaximaDisponible;
                    this.horaFinSeleccionada = '23:59';
                }
                
            } catch (err) {
                console.error("Error al cargar rango de fechas:", err);
                const hoy = new Date().toISOString().split('T')[0];
                this.fechaInicioSeleccionada = hoy;
                this.fechaFinSeleccionada = hoy;
            }
        },
        
        // Mapeo de iconos
        getIcon(magnitudTipo) {
            if (!magnitudTipo) return 'bi bi-question-lg';
            const lowerMag = magnitudTipo.toLowerCase();
            
            if (lowerMag.includes('temperatura')) return 'bi bi-thermometer-half';
            if (lowerMag.includes('humedad')) return 'bi bi-droplet-half';
            if (lowerMag.includes('electricidad')) return 'bi bi-lightning-charge-fill';
            if (lowerMag.includes('potencia')) return 'bi bi-lightning';
            if (lowerMag.includes('energía')) return 'bi bi-battery-charging';
            if (lowerMag.includes('iluminación')) return 'bi bi-sun';
            if (lowerMag.includes('movimiento')) return 'bi bi-person-walking';
            
            return 'bi bi-speedometer2'; 
        },
            
        // --- Layout y Tema ---
        toggleSidebar() { this.isSidebarOpen = !this.isSidebarOpen; },
        handleThemeChange(event) { this.isDark = event.matches; },
        
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
// $PRIMARY-PURPLE: #8A2BE2;
// $SUCCESS-COLOR: #1ABC9C;
// $GRAY-COLD: #99A2AD;
// $LIGHT-TEXT: #E4E6EB;
// $DARK-TEXT: #333333;
// $SUBTLE-BG-DARK: #2B2B40; // Fondo de Tarjeta Oscura
// $BLUE-MIDNIGHT: #1A1A2E; // Fondo de Inputs Oscuros
// $SUBTLE-BG-LIGHT: #FFFFFF;
// $WHITE-SOFT: #F7F9FC; 
// $DANGER-COLOR: #e74c3c;
// $WIDTH-SIDEBAR: 280px; 
// $WIDTH-CLOSED: 80px;
// $DARK-BG-CONTRAST: #1E1E30; 


// // ----------------------------------------
// // LAYOUT PRINCIPAL (CORRECCIÓN CRÍTICA DE FONDO)
// // ----------------------------------------
// .plataforma-layout {
//     display: flex;
//     min-height: 100vh;
//     transition: background-color 0.3s;
// }

// .plataforma-contenido {
//     margin-left: $WIDTH-CLOSED;
//     flex-grow: 1;
//     padding: 0;
//     transition: margin-left 0.3s ease-in-out;
    
//     &.shifted {
//         margin-left: $WIDTH-SIDEBAR;
//     }
// }

.reportes-contenido {
    /* Mantiene el espaciado lateral de 40px */
    padding: 0 40px 40px 40px;
}
/* ----------------------------------------
   NUEVOS ESTILOS: Selector de Campos (Checkboxes)
   ---------------------------------------- */
.campo-selector-container {
    background-color: #FFFFFF; /* Fondo claro por defecto */
    padding: 20px 25px;
    border-radius: 12px;
    margin-bottom: 30px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    
    .selector-titulo {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 15px;
        border-bottom: 1px solid #eee;
        padding-bottom: 10px;
    }
}
.checkbox-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 10px 15px;
}
.checkbox-item {
    display: flex;
    align-items: center;
    
    input[type="checkbox"] {
        width: 18px;
        height: 18px;
        border: 2px solid #99A2AD;
        border-radius: 4px;
        margin-right: 10px;
        cursor: pointer;
        transition: all 0.2s;
        
        &:checked {
            background-color: #8A2BE2;
            border-color: #8A2BE2;
        }
    }
    
    label {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.95rem;
        cursor: pointer;
        i {
            color: #8A2BE2;
            font-size: 1rem;
        }
    }
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
.charts-grid-multiple {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 20px;
}

/* El grid para el gráfico único (ocupa todo el ancho) */
.charts-grid-single {
    display: grid;
    grid-template-columns: 1fr;
    gap: 20px;
}

/* ----------------------------------------
   NUEVOS ESTILOS: Selector de Campos (Checkboxes)
   ---------------------------------------- */
.campo-selector-container {
    background-color: #FFFFFF; /* Fondo claro por defecto */
    padding: 20px 25px;
    border-radius: 12px;
    margin-bottom: 30px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    
    .selector-titulo {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 15px;
        border-bottom: 1px solid #eee;
        padding-bottom: 10px;
    }
}
.checkbox-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 10px 15px;
}
.checkbox-item {
    display: flex;
    align-items: center;
    
    input[type="checkbox"] {
        width: 18px;
        height: 18px;
        border: 2px solid #99A2AD;
        border-radius: 4px;
        margin-right: 10px;
        cursor: pointer;
        transition: all 0.2s;
        
        &:checked {
            background-color: #8A2BE2;
            border-color: #8A2BE2;
        }
    }
    
    label {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.95rem;
        cursor: pointer;
        i {
            color: #8A2BE2;
            font-size: 1rem;
        }
    }
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