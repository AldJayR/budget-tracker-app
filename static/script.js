// Login Form

const showPasswordCheckbox = document.getElementById("show-password")

if (showPasswordCheckbox) {
    showPasswordCheckbox.addEventListener("change", () => {
        if (showPasswordCheckbox.checked) {
            const passwords = document.querySelectorAll(".password")
            passwords.forEach(password => {
                password.type = "text"
            })
        } else {
            const passwords = document.querySelectorAll("password")
            passwords.forEach(password => {
                password.type = "password"
            })
        }
    })
}