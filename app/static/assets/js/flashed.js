document.addEventListener('DOMContentLoaded', function () {
    const flashMessagesContainer = document.getElementById('flashMessages');
  
    // Verificar si hay mensajes flash
    if (flashMessagesContainer) {
      const rawMessages = flashMessagesContainer.getAttribute('data-messages');
      console.log('Contenido de data-messages:', rawMessages); // Depuración
  
      let messages = [];
  
      try {
        if (rawMessages && rawMessages.trim() !== "") {
          messages = JSON.parse(rawMessages);
          console.log('Mensajes procesados:', messages); // Depuración
        } else {
          console.log('No hay mensajes flash disponibles.');
        }
      } catch (error) {
        console.error('Error al analizar los mensajes flash:', error);
      }
  
      // Si hay mensajes, creamos los toasts
      if (messages.length > 0) {
        const toastContainer = document.getElementById('toast-container');
  
        messages.forEach(message => {
          // Crear un contenedor de toast
          const toast = document.createElement('div');
          toast.className = 'toast align-items-center text-white bg-primary border-0';
          toast.role = 'alert';
          toast.setAttribute('aria-live', 'assertive');
          toast.setAttribute('aria-atomic', 'true');
  
          // Contenido del toast
          toast.innerHTML = `
            <div class="d-flex">
              <div class="toast-body">
                ${message}
              </div>
              <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
          `;
  
          // Agregar el toast al contenedor de toasts
          toastContainer.appendChild(toast);
  
          // Inicializar el toast con Bootstrap
          const bootstrapToast = new bootstrap.Toast(toast, { delay: 5000 }); // 5 segundos de duración
          bootstrapToast.show();
  
          // Eliminar el toast del DOM después de que desaparezca
          toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
          });
        });
      }
    } else {
      console.warn('No se encontró el contenedor con id="flashMessages".');
    }
  });
  

  document.addEventListener("DOMContentLoaded", function () {
    // Inicializar todos los toasts automáticamente
    const toastElements = document.querySelectorAll('.toast');
    toastElements.forEach(toastEl => {
      const toast = new bootstrap.Toast(toastEl);
      toast.show();
    });
  });
