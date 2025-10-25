<template>
  <div class="modal-base" @click.self="$emit('close')">
    <div class="modal-contenido" :class="{ 'theme-dark': isDark, 'theme-light': !isDark }">
      
      <div class="modal-header">
        <h2>Agregar Nuevo Dispositivo al Proyecto {{ proyectoId }}</h2>
        <button @click="$emit('close')" class="btn-cerrar">&times;</button>
      </div>

      <div class="modal-scroll-body">
        <div class="modal-body">
          <div v-if="error" class="alert-error">{{ error }}</div>
          
          <form @submit.prevent="submitDispositivo">
            
            <div class="form-row">
              <div class="form-group">
                <label for="nombre">Nombre:</label>
                <input type="text" v-model="form.nombre" id="nombre" class="form-control" required>
              </div>
              <div class="form-group">
                <label for="tipo">Tipo de Dispositivo:</label>
                <select v-model="tipoSeleccionado" id="tipo" class="form-control" required>
                  <option v-for="t in tiposDispositivo" :key="t" :value="t">{{ t }}</option>
                  <option value="Otro">Otro (Especifique)</option>
                </select>
              </div>
            </div>
            
            <div v-if="tipoSeleccionado === 'Otro'" class="form-group mb-3 full-width">
              <label for="otro_tipo">Especifique el Tipo:</label>
              <input type="text" v-model="form.tipo" id="otro_tipo" class="form-control" required placeholder="Ej: Módulo de Relevo PLC">
            </div>
            
            <div class="form-group mb-3">
              <label for="descripcion">Descripción:</label>
              <textarea v-model="form.descripcion" id="descripcion" class="form-control" rows="2"></textarea>
            </div>
            
            <div class="location-group">
              <h4 class="location-heading">Ubicación (Pin Drop)</h4>
              <p class="location-note">Mueve el marcador o haz clic en el mapa para establecer la ubicación exacta.</p>
              
              <div id="leaflet-map-container" style="height: 300px; margin-bottom: 15px;"></div>
              
              <div class="form-row">
                <div class="form-group">
                  <label for="latitud">Latitud:</label>
                  <input type="text" v-model="form.latitud" id="latitud" class="form-control" readonly>
                </div>
                <div class="form-group">
                  <label for="longitud">Longitud:</label>
                  <input type="text" v-model="form.longitud" id="longitud" class="form-control" readonly>
                </div>
              </div>
            </div>
          </form>
        </div>
      </div> 
      <div class="modal-footer-actions">
        <button type="button" @click="$emit('close')" class="btn btn-secondary me-2">Cancelar</button>
        <button type="submit" @click="submitDispositivo" class="btn btn-primary" :disabled="loading">
          <i v-if="loading" class="bi bi-arrow-clockwise fa-spin"></i>
          {{ loading ? 'Guardando...' : 'Guardar Dispositivo' }}
        </button>
      </div>
      
    </div>
  </div>
</template>

<script>
import L from 'leaflet'; 
import 'leaflet-control-geocoder'; 
// No necesitamos importar leaflet.locatecontrol/dist/L.Control.Locate.min.js

// Importación de imágenes de marcador de Leaflet (para evitar que se rompan)
import marker2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

// CRÍTICO: Arreglar los íconos de marcador rotos de Leaflet
L.Icon.Default.mergeOptions({
    iconRetinaUrl: marker2x,
    iconUrl: markerIcon,
    shadowUrl: markerShadow,
});

const API_BASE_URL = 'http://127.0.0.1:8001';

// 🚨 Definición del control de ubicación personalizado (Método estable para el botón de geolocalización)
L.Control.CustomLocate = L.Control.extend({
    onAdd: function(map) {
        var container = L.DomUtil.create('div', 'leaflet-bar leaflet-control');
        container.style.backgroundColor = 'white';
        container.style.width = '30px';
        container.style.height = '30px';
        container.style.cursor = 'pointer';
        container.style.borderRadius = '4px';
        
        // Usamos el icono de Bootstrap Icons
        container.innerHTML = '<i class="bi bi-geo-alt-fill" style="font-size: 1.2rem; line-height: 30px; text-align: center; width: 100%; color: #007bff;"></i>';
        
        // 🚨 Acción: Al hacer clic, usa la función nativa de Leaflet para localizar
        container.onclick = function() {
            map.locate({ setView: true, maxZoom: 16, enableHighAccuracy: true });
        };

        return container;
    },
     onRemove: function() {} 
});

L.control.customLocate = function(opts) {
    return new L.Control.CustomLocate(opts);
}


export default {
    name: 'ModalCrearDispositivo',
    props: {
        proyectoId: {
            type: [Number, String],
            required: true
        }
    },
    data() {
        return {
            isDark: false,
            loading: false,
            error: null,
            tiposDispositivo: ['Microcontrolador', 'Raspberry Pi', 'Sensor Gateway', 'Controlador'],
            
            map: null,
            marker: null,
            
            tipoSeleccionado: 'Microcontrolador', 
            
            form: {
                nombre: '',
                descripcion: '',
                tipo: 'Microcontrolador', 
                latitud: null,
                longitud: null,
                habilitado: true, 
                proyecto_id: this.proyectoId 
            }
        };
    },
    watch: {
        tipoSeleccionado(newValue) {
            this.form.tipo = (newValue !== 'Otro') ? newValue : ''; 
        },
    },
    mounted() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            this.isDark = true;
        }
        
        const resultado = JSON.parse(localStorage.getItem('resultado'));
        if (!resultado || !resultado.usuario) {
            this.$router.push('/'); 
        }

        this.$nextTick(this.initMap); 
    },
    methods: {
        // -----------------------------------------------------
        // LÓGICA DEL MAPA
        // -----------------------------------------------------
        initMap() {
            const defaultLat = 20.501;
            const defaultLng = -87.001; 
            const defaultZoom = 13;

            this.map = L.map('leaflet-map-container').setView([defaultLat, defaultLng], defaultZoom);

            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
            }).addTo(this.map);

            this.marker = L.marker([defaultLat, defaultLng], {
                draggable: true 
            }).addTo(this.map);

            this.updateCoordinates(defaultLat, defaultLng);

            // 🚨 1. INTEGRACIÓN DE LA BARRA DE BÚSQUEDA (GEOCODER)
            L.Control.geocoder({
                defaultMarkGeocode: false, 
                placeholder: 'Buscar dirección o lugar...',
            })
            .on('markgeocode', (event) => {
                const latlng = event.geocode.center;
                
                if (this.marker) {
                    this.marker.setLatLng(latlng);
                }
                
                this.map.fitBounds(event.geocode.bbox, { padding: [100, 100] });
                this.updateCoordinates(latlng.lat, latlng.lng);
            })
            .addTo(this.map);
            
            // 🚨 2. INTEGRACIÓN DEL BOTÓN DE GEOLOCALIZACIÓN ESTABLE (CustomLocate)
            L.control.customLocate({position: 'topleft'}).addTo(this.map);
            
            // 3. EVENTOS: Manejar la actualización de coordenadas al encontrar la ubicación
            this.map.on('locationfound', (e) => {
                this.updateCoordinates(e.latlng.lat, e.latlng.lng);
                if (this.marker) {
                    this.marker.setLatLng(e.latlng);
                }
            });


            // 4. EVENTO: Actualizar coordenadas al mover el marcador
            this.marker.on('dragend', (event) => {
                const latlng = event.target.getLatLng();
                this.updateCoordinates(latlng.lat, latlng.lng);
            });

            // 5. EVENTO: Actualizar coordenadas al hacer clic en el mapa (Mueve el pin)
            this.map.on('click', (event) => {
                if (this.marker) {
                    this.marker.setLatLng(event.latlng);
                }
                this.updateCoordinates(event.latlng.lat, event.latlng.lng);
            });

            // CRÍTICO: El mapa necesita ser invalidado
            setTimeout(() => { this.map.invalidateSize(); }, 10);
        },
        updateCoordinates(lat, lng) {
            this.form.latitud = parseFloat(lat).toFixed(6);
            this.form.longitud = parseFloat(lng).toFixed(6);
        },
        // -----------------------------------------------------
        // LÓGICA DE ENVÍO
        // -----------------------------------------------------
        async submitDispositivo() {
            if (this.tipoSeleccionado === 'Otro' && !this.form.tipo) {
                this.error = "Por favor, especifique el tipo de dispositivo.";
                return;
            }
            if (!this.form.nombre || !this.form.descripcion || !this.form.tipo) {
                this.error = "Faltan campos obligatorios.";
                return;
            }
            
            this.loading = true;
            this.error = null;
            const token = localStorage.getItem('accessToken');
            
            try {
                const response = await fetch(`${API_BASE_URL}/api/dispositivos/`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(this.form)
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.message || data.detail || 'Fallo al crear el dispositivo.');
                }
                
                this.$emit('dispositivo-creado', data.resultados[0]);
                this.$emit('close');

            } catch (err) {
                this.error = err.message || 'Error de conexión.';
            } finally {
                this.loading = false;
            }
        },
    }
};
</script>

<style scoped lang="scss">
// ----------------------------------------
// VARIABLES DE LA PALETA
// ----------------------------------------
$PRIMARY-PURPLE: #8A2BE2;
$SUCCESS-COLOR: #1ABC9C;
$BLUE-MIDNIGHT: #1A1A2E;
$DARK-TEXT: #333333;
$LIGHT-TEXT: #E4E6EB;
$SUBTLE-BG-DARK: #2B2B40; 
$SUBTLE-BG-LIGHT: #FFFFFF;
$WHITE-SOFT: #F7F9FC;
$GRAY-COLD: #99A2AD;


// ----------------------------------------
// BASE DEL MODAL (POSICIONAMIENTO)
// ----------------------------------------
.modal-base {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background-color: rgba(0, 0, 0, 0.6);
    display: flex; justify-content: center; align-items: center;
    z-index: 9999;
}

.modal-contenido {
    width: 90%; 
    max-width: 650px; /* Ancho cómodo para el mapa */
    border-radius: 15px; 
    padding: 0; /* 🚨 CRÍTICO: El padding se mueve a header/footer/scroll-body */
    max-height: 90vh; /* 🚨 CRÍTICO: Altura máxima de la ventana */
    display: flex;
    flex-direction: column;
    overflow: hidden; /* Evita que el scroll afecte al contenedor principal */
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
    transition: background-color 0.3s;
}

// ----------------------------------------
// CABECERA Y CUERPO SCROLLABLE
// ----------------------------------------

.modal-header {
    display: flex; justify-content: space-between; align-items: center;
    padding: 20px 25px; /* Padding Fijo */
    flex-shrink: 0; /* Evita que el header se encoja */
    border-bottom: 1px solid rgba($GRAY-COLD, 0.1);
    h2 { font-size: 1.4rem; font-weight: 600; }
}

.modal-scroll-body {
    // 🚨 HABILITA LA BARRA DE DESPLAZAMIENTO
    flex-grow: 1; 
    overflow-y: auto; 
    padding: 0 25px; /* Mantiene el padding lateral */
}

.modal-body {
    padding-top: 20px; /* Añadir espacio arriba del formulario */
    padding-bottom: 20px;
}

.form-row { display: flex; gap: 20px; }
.form-group { flex: 1; margin-bottom: 15px; }

// ----------------------------------------
// FOOTER FIJO (Botones)
// ----------------------------------------
.modal-footer-actions {
    // 🚨 MANTIENE LOS BOTONES VISIBLES
    flex-shrink: 0; 
    padding: 15px 25px; 
    border-top: 1px solid rgba(0, 0, 0, 0.1);
    background-color: inherit; 
    display: flex;
    justify-content: flex-end;
    gap: 10px;
}

// ----------------------------------------
// ESTILOS DE MAPA Y FORMULARIO
// ----------------------------------------
.location-group { margin-top: 20px; }
.location-heading { font-size: 1.2rem; margin-bottom: 5px; }
.location-note { font-size: 0.85rem; opacity: 0.7; margin-bottom: 10px; }


// ----------------------------------------
// TEMAS (DARK/LIGHT)
// ----------------------------------------
.theme-light { 
    background-color: $SUBTLE-BG-LIGHT; color: $DARK-TEXT; 
    .form-control { border: 1px solid #ddd; }
    .modal-header, .modal-footer-actions { border-color: #ddd; }
}
.theme-dark { 
    background-color: $SUBTLE-BG-DARK; 
    color: $LIGHT-TEXT; 
    .modal-header, .modal-footer-actions { border-color: rgba($LIGHT-TEXT, 0.2); }
    .form-control { 
        background-color: $BLUE-MIDNIGHT; 
        border: 1px solid rgba($LIGHT-TEXT, 0.2); 
        color: $LIGHT-TEXT; 
    }
    .btn-secondary { background-color: #444; color: $LIGHT-TEXT; }
}
</style>