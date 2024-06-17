// Login Form

const showPasswordCheckbox = document.getElementById("show-password");

if (showPasswordCheckbox) {
    showPasswordCheckbox.addEventListener("change", () => {
        const passwords = document.querySelectorAll(".password");
        passwords.forEach(password => {
            if (showPasswordCheckbox.checked) {
                password.type = "text";
            } else {
                password.type = "password";
            }
        });
    });
}
