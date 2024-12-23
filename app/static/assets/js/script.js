// script.js
document.addEventListener('DOMContentLoaded', () => {
    const botonesEliminar = document.querySelectorAll('.eliminar');

    const modal = document.getElementById('myModal');
    const btnCerrar = document.querySelector('.close');
    const btnConfirmar = document.getElementById('confirmarEliminar');
    const btnCancelar = document.getElementById('cancelarEliminar');
    let filaAEliminar; // Variable para almacenar la fila a eliminar

    botonesEliminar.forEach(boton => {
        boton.addEventListener('click', function() {
            filaAEliminar = this.closest('tr'); // Guarda la fila que se va a eliminar
            modal.style.display = "block"; // Muestra el modal
        });
    });

    btnCerrar.onclick = function() {
        modal.style.display = "none"; // Cierra el modal
    };

    btnCancelar.onclick = function() {
        modal.style.display = "none"; // Cierra el modal al cancelar
    };

    btnConfirmar.onclick = function() {
        if (filaAEliminar) {
            filaAEliminar.remove(); // Elimina la fila del DOM
            filaAEliminar = null; // Resetea la variable
        }
        modal.style.display = "none"; // Cierra el modal después de eliminar
    };

    // Cierra el modal si se hace clic fuera de él
    window.onclick = function(event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    };
});
