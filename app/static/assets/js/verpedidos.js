flatpickr("#fecha_pedido", {
    dateFormat: "Y-m-d",  // Formato: Año-Mes-Día
    enableTime: false,     // Deshabilitar hora (solo fecha)
    locale: "es"           // Español
});
flatpickr("#fecha_inicio_trabajo", {
    dateFormat: "Y-m-d",  // Formato: Año-Mes-Día
    enableTime: false,     // Deshabilitar hora (solo fecha)
    locale: "es"           // Español
});

flatpickr("#fecha_fin_trabajo", {
    dateFormat: "Y-m-d",  // Formato: Año-Mes-Día
    enableTime: false,     // Deshabilitar hora (solo fecha)
    locale: "es"           // Español
});
flatpickr("#fecha_pago", {
    dateFormat: "Y-m-d",  // Formato: Año-Mes-Día
    enableTime: false,     // Deshabilitar hora (solo fecha)
    locale: "es"           // Español
});
document.addEventListener('DOMContentLoaded', () => {
const elementosFechaPago = document.querySelectorAll('.fecha_pago2'); // Seleccionar por clase

elementosFechaPago.forEach(elemento => {
  flatpickr(elemento, {
    dateFormat: "Y-m-d",
    enableTime: false,
    locale: "es"
  });
});
});


// Inicialización de checkboxes y campos dependientes
document.querySelectorAll(".modal").forEach(modal => {  // Iterar sobre *cada* modal
          modal.addEventListener('shown.bs.modal', () => { // Escuchar el evento 'shown.bs.modal'
              const codigo_pedido = modal.id.replace(/[^0-9]/g, ''); // Extraer el código del pedido del ID del modal
              const checkbox = modal.querySelector(`#cancelado${codigo_pedido}`);
              const detallesPago = modal.querySelector(`#detallesPago${codigo_pedido}`);
              const tipoMoneda = modal.querySelector(`#tipo_moneda${codigo_pedido}`);
              const metodoPago = modal.querySelector(`#metodo_pago${codigo_pedido}`);
              const metodoPagoContainer = modal.querySelector(`#metodoPagoContainer${codigo_pedido}`);
              const referenciaContainer = modal.querySelector(`#referenciaContainer${codigo_pedido}`);
              

              if (!checkbox || !detallesPago || !tipoMoneda || !metodoPago || !metodoPagoContainer || !referenciaContainer) {
                  console.warn(`Algunos elementos del modal ${codigo_pedido} no se encontraron.`);
                  return;
              }

              function actualizarCampos() {
                  detallesPago.style.display = checkbox.checked ? "block" : "none";
                  if (!checkbox.checked) {
                      metodoPagoContainer.style.display = "none";
                      referenciaContainer.style.display = "none";
                  }
              }

              function actualizarMetodosPago() {
                  metodoPago.innerHTML = "";
                  metodoPagoContainer.style.display = "block";
                  if (tipoMoneda.value === "bolivares") {
                      metodoPago.innerHTML = `<option value="efectivo">Efectivo</option><option value="pago_movil">Pago Móvil</option>`;
                  } else {
                      metodoPago.innerHTML = `<option value="efectivo">Efectivo</option><option value="transferencia">Transferencia</option>`;
                  }
              }

              function actualizarReferencia() {
                  referenciaContainer.style.display = (metodoPago.value === "pago_movil" || metodoPago.value === "transferencia") ? "block" : "none";
              }

              checkbox.addEventListener("change", actualizarCampos);
              tipoMoneda.addEventListener("change", actualizarMetodosPago);
              metodoPago.addEventListener("change", actualizarReferencia);

              actualizarCampos();
              actualizarMetodosPago();
              actualizarReferencia();

              
          });
      });

      function filtrarPedidos(filtro) {
  let pedidos = document.querySelectorAll('.pedido-item');

  pedidos.forEach(pedido => {
      if (filtro === 'todos') {
          pedido.style.display = 'flex';
      } else if (pedido.classList.contains(filtro)) {
          pedido.style.display = 'flex';
      } else {
          pedido.style.display = 'none';
      }
  });
      };
document.getElementById("orden-fecha").addEventListener("change", function() {
  let orden = this.value;
  let contenedor = document.getElementById("pedidos-container");
  let pedidos = Array.from(contenedor.getElementsByClassName("pedido-item"));

  pedidos.sort((a, b) => {
      let fechaA = new Date(a.getAttribute("data-fecha"));
      let fechaB = new Date(b.getAttribute("data-fecha"));

      return orden === "reciente" ? fechaB - fechaA : fechaA - fechaB;
  });

  pedidos.forEach(pedido => contenedor.appendChild(pedido));
});
document.addEventListener('DOMContentLoaded', function() {
  // Tu código aquí
  const tasaBCV = parseFloat("{{ tasa_bcv }}");
  console.log("Tasa BCV:", tasaBCV);

  document.querySelectorAll('.total_a_pagar').forEach(function(input) {
      input.addEventListener('input', function() {
          const valorFormateado = this.value;
          const montoUSD = parseFloat(valorFormateado) || 0;
          console.log("Monto USD:", montoUSD);

          const montoBsElement = this.closest('.modal').querySelector('.monto_bs');

          if (montoBsElement){
              if (!isNaN(montoUSD)) {
                  const montoBS = montoUSD * tasaBCV;
                  montoBsElement.textContent = montoBS.toFixed(2);
              } else {
                  montoBsElement.textContent = "0.00";
              }
          } else {
              console.log("No se encontro el elemento monto_bs")
          }
      });
  });
});
$(document).ready(function() {
  $('.tecnicos-select').each(function() {
      let $select = $(this);
      
      // Inicializar Select2 en cada select
      $select.select2({
          placeholder: "--- Seleccione Técnicos ---",
          allowClear: true
      });

      function actualizarListaSeleccionados($select) {
          let lista = $select.closest('div').siblings('.seleccionados').find('.listaSeleccionados');
          lista.empty();

          // Obtener los técnicos seleccionados
          let seleccionados = $select.val() || [];

          // Mostrar los técnicos seleccionados en la lista
          $select.find('option:selected').each(function() {
              let tecnico = $(this).text();
              lista.append('<li>' + tecnico + '</li>');
          });
      }

      // Escuchar cambios en la selección y actualizar la lista
      $select.on('change', function() {
          actualizarListaSeleccionados($(this));
      });

      // Cargar técnicos seleccionados al inicio
      actualizarListaSeleccionados($select);
  });
});
$(document).ready(function() {
  // Inicializar Select2 en todos los selects con la clase "servicios-select"
  $('.servicios-select').select2({
      placeholder: "--- Seleccione Servicios ---",
      allowClear: true,
      tags: true
  });

  // Función para actualizar la lista de servicios seleccionados
  function actualizarListaServicios(container) {
      let lista = container.find('.lista-seleccionados-servicios');
      lista.empty();

      // Obtener los servicios seleccionados dentro de este contenedor específico
      let seleccionados = container.find('.servicios-select').val() || [];

      // Mostrar los servicios seleccionados en la lista
      container.find('.servicios-select option:selected').each(function() {
          lista.append('<li>' + $(this).text() + '</li>');
      });
  }

  // Manejar cambios en los selects dentro de cada modal
  $('.servicios-container').each(function() {
      let container = $(this).closest('.modal'); // Detectar el modal específico
      container.find('.servicios-select').on('change', function() {
          actualizarListaServicios(container);
      });

      // Cargar servicios seleccionados al inicio
      actualizarListaServicios(container);
  });
});
document.addEventListener("DOMContentLoaded", function() {
  function actualizarListaSeleccionados(selectElement, listaId) {
      let lista = document.getElementById(listaId);
      lista.innerHTML = "";
      
      Array.from(selectElement.selectedOptions).forEach(option => {
          let li = document.createElement("li");
          li.textContent = option.text;
          lista.appendChild(li);
      });
  }

  // Capturar los select de servicios correctivos y preventivos
  let selectCorrectivo = document.querySelector(".servicios-correctivo");
  let selectPreventivo = document.querySelector(".servicios-preventivo");

  // Actualizar la lista de servicios seleccionados al cargar
  actualizarListaSeleccionados(selectCorrectivo, "listaSeleccionadosServicios");
  actualizarListaSeleccionados(selectPreventivo, "listaSeleccionadosServicios");

  // Escuchar cambios en los selects
  selectCorrectivo.addEventListener("change", function() {
      actualizarListaSeleccionados(selectCorrectivo, "listaSeleccionadosServicios");
  });

  selectPreventivo.addEventListener("change", function() {
      actualizarListaSeleccionados(selectPreventivo, "listaSeleccionadosServicios");
  });
});
document.addEventListener('DOMContentLoaded', function () {
  const tasaBCV = parseFloat("{{ tasa_bcv }}");
  console.log("Tasa BCV:", tasaBCV);

  function actualizarMontoBs(input) {
      const montoUSD = parseFloat(input.value) || 0;
      const montoBS = montoUSD * tasaBCV;
      const montoBsElement = input.closest('.modal').querySelector('.monto_bs');

      if (montoBsElement) {
          montoBsElement.textContent = montoBS.toFixed(2);
      }
  }

  const inputs = document.querySelectorAll('.total_a_pagar');

  inputs.forEach(input => {
      const valorInicial = input.dataset.valorInicial;

      if (valorInicial) {
          input.value = parseFloat(valorInicial).toFixed(2);
          actualizarMontoBs(input); // Actualizar monto Bs al cargar el modal
      } else {
          input.value = '0.00';
      }

      input.addEventListener('input', function (e) {
          let value = e.target.value.replace(/[^0-9]/g, '');

          if (!value) {
              e.target.value = '0.00';
              return;
          }

          while (value.length < 3) {
              value = '0' + value;
          }

          const integerPart = value.slice(0, -2);
          const decimalPart = value.slice(-2);

          const trimmedIntegerPart = integerPart.replace(/^0+/, '');
          const finalIntegerPart = trimmedIntegerPart || '0';

          const formattedValue = `${finalIntegerPart}.${decimalPart}`;

          e.target.value = formattedValue;
          actualizarMontoBs(input); // Actualizar monto Bs al cambiar el valor
      });

      input.addEventListener('focus', function (e) {
          e.target.select();
      });
  });
});
$(document).ready(function() {
$('.tecnicos-select').select2({
    width: '100%', // 🔥 Esto hace que el select ocupe todo el ancho disponible
    allowClear: true , // 🔥 Habilita la X para limpiar
    placeholder: "---Seleccione---"
});
$('.servicios-select').select2({
    width: '100%', // 🔥 Esto hace que el select ocupe todo el ancho disponible
    allowClear: true,
    placeholder: "---Seleccione---"

});
});