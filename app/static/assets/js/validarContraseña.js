function togglePassword() {
    const passwordField = document.getElementById("password");
    const type = passwordField.type === "password" ? "text" : "password";
    passwordField.type = type;   
  
  
    // Cambia el icono del ojo según el tipo de input
    const eyeIcon = document.querySelector('.fa-eye');
    eyeIcon.classList.toggle('fa-eye-slash');
  }

function validarContraseña() {
    var password = document.getElementById("password").value;
    var regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    return regex.test(password);
}

