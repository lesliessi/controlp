function togglePassword() {
    var passwordField = document.getElementById("contraseña");
    if (passwordField.type === "password") {
        passwordField.type = "text";
    } else {
        passwordField.type = "password";   

    }
}