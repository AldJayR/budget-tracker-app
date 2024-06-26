const introScreen = document.querySelector(".intro-screen")
const startBtn = document.getElementById("start-btn")
const setupContainer = document.querySelector(".setup-container")
const setupForm = document.getElementById("setup-form")
const username = document.getElementById("username")
const weeklyBudget = document.getElementById("weekly-budget")
const contactNumber = document.getElementById("contact-number")
const formResult = document.getElementById("result")

startBtn.addEventListener("click", () => {
    introScreen.innerHTML = "";

    setupContainer.classList.remove("d-none")
})
setupForm.addEventListener("submit", e => {
    if (username.value === '' || !weeklyBudget.value) {
        e.preventDefault();
        formResult.textContent = "Please fill in the required inputs"
    } else if (username.value.length < 7) {
        e.preventDefault();
        formResult.textContent = "Username must be longer than 7 characters"
    } else if(contactNumber.value.length < 11 || contactNumber.value.length > 11) {
        e.preventDefault();
        formResult.textContent = "Invalid phone number"
    }
})