import { sendRequest } from "./app.js";

const form = document.querySelector("form")
const errorBlock = document.querySelector(".login-error-block")
const submitButton = document.querySelector(".submit-button")

function getErrorText(errorStatus) {
    switch (errorStatus) {
        case 422:
            return "Bitte prüfen Sie Ihre Eingaben"
        case 409:
            return "Diese E-Mail ist bereits vergeben"

    }
}

form.addEventListener("submit", async (e) => {
    e.preventDefault()
    submitButton.disabled = true;

    const payload = Object.fromEntries(new FormData(form))
    let response;
    try {
        response = await sendRequest("register", payload)
    } catch (error) {
        errorBlock.hidden = false
        errorBlock.textContent = "Server nicht erreichbar. Bitte später erneut versuchen."
        return
    } finally {
        submitButton.disabled = false
    }


    if (!response.ok) {
        errorBlock.textContent = getErrorText(response.status) ?? "Etwas ist schief gelaufen. Bitte später erneut versuchen"
        errorBlock.hidden = false
        return
    }

    errorBlock.hidden = true
    sessionStorage.setItem("pendingUser", JSON.stringify(response.data))
    location.replace("pending.html")
})