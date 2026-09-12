import { sendAuthRequest } from "./app.js";

const form = document.querySelector("form")
const errorBlock = document.querySelector(".login-error-block")
const submitButton = document.querySelector(".submit-button")

function getErrorText(errorStatus) {
    switch (errorStatus) {
        case 403:
            return "Ihr Konto wartet auf Freigabe"
        case 423:
            return "Ihr Antrag wurde abgelehnt"
        case 401:
            return "E-Mail oder Passwort ist falsch"
    }
}

form.addEventListener("submit", async (e) => {
    e.preventDefault()
    submitButton.disabled = true

    const payload = Object.fromEntries(new FormData(form))
    let response;

    try {
        response = await sendAuthRequest("login", payload)
    } catch (error) {
        errorBlock.hidden = false
        errorBlock.textContent = "Server nicht erreichbar. Bitte später erneut versuchen."
        return
    } finally {
        submitButton.disabled = false
    }

    if (!response.ok) {
        errorBlock.textContent = getErrorText(response.status) ?? "Etwas ist schief gegangen"
        errorBlock.hidden = false
        return
    }

    errorBlock.hidden = true
    localStorage.setItem("token", response.data.access_token)
    location.href = "loads.html"

})