<template>
  <div class="resumen-card" :class="{ 'theme-dark': isDark, 'theme-light': !isDark }">
    <div class="card-icon">
      <i :class="['bi', icono]"></i>
    </div>
    <div class="card-content">
      <h6 class="card-title">{{ titulo }}</h6>
      <p class="card-value">{{ valor }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ResumenCard',
  props: {
    titulo: String,
    valor: [String, Number],
    icono: String, // Clase de icono de Bootstrap, ej: "bi-lightning"
    isDark: {
      type: Boolean,
      default: false,
    },
  },
};
</script>

<style scoped lang="scss">
@use "sass:color";
// NOTA: Asumimos que $spacer, $primary-color, $LIGHT_TEXT, $SUBTLE_BG_DARK, etc.
// están definidos en tu archivo _variables.scss o pasados a la raíz SCSS.

$spacer: 1rem;
$border-radius: 12px;
$border-radius-sm: 8px;

.resumen-card {
  display: flex;
  align-items: center;
  gap: $spacer; /* Espacio entre icono y texto */
  padding: $spacer; 
  border-radius: $border-radius;
  background-color: var(--card-bg); /* Fondo de la tarjeta */
  border: 1px solid var(--card-border);
  box-shadow: var(--shadow-color);
  transition: all 0.2s ease-in-out;
  height: 100%; 
  min-height: 80px; /* Altura mínima para asegurar que el contenido entre */

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  }

  .card-icon {
    font-size: 1.5rem; /* Icono un poco más pequeño para caber */
    color: $PRIMARY-PURPLE;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: $spacer * 0.5;
    background-color: rgba($PRIMARY-PURPLE, 0.15); /* Fondo morado opaco */
    border-radius: $border-radius-sm;
    min-width: 50px; /* Ancho fijo para el icono */
  }

  .card-content {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    min-width: 1; 
  }

  .card-title {
    margin-bottom: $spacer * 0.1;
    font-size: 0.85rem; /* Título pequeño y conciso */
    color: var(--text-color-secondary); 
    font-weight: 500;
    line-height: 1.1;
    /* 🎯 PERMITE EL AJUSTE DE PALABRA Y ELIPSIS */
    white-space: normal; 
    word-break: break-word; 
    overflow: hidden;
    text-overflow: ellipsis; 
    display: -webkit-box;
    -webkit-box-orient: vertical;
  }

  .card-value {
    font-size: 1.3rem; /* Valor principal, prominente */
    font-weight: 700;
    color: var(--text-color-primary); 
    margin-bottom: 0;
    white-space: nowrap; /* Mantiene el valor principal en una línea */
    overflow: hidden;
    text-overflow: ellipsis;
  }

  /* ------------------- TEMA OSCURO ------------------- */
  &.theme-dark {
    .card-title {
      /* Color blanco opaco para el título en modo oscuro */
      color: color.adjust($LIGHT-TEXT, $alpha: -0.3); 
    }
    .card-value {
      /* Color blanco puro para el valor principal */
      color: $LIGHT-TEXT; 
    }
  }
}
</style>