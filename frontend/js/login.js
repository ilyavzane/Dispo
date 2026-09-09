import { API } from "./app.js";

const form = document.querySelector("form")
const errorText = document.querySelector(".login-error-block")
const submitButton = document.querySelector(".submit-button")

form.addEventListener("submit", async (e) => {
    e.preventDefault()
    submitButton.disabled = true

    const payload = Object.fromEntries(new FormData(form))
    let response;
    let data;

    try {
        response = await fetch(`${API}/auth/login`,
            {
                method: "post",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            }
        )

        data = await response.json()
    } catch (error) {
        errorText.hidden = false
        errorText.textContent = "Server nicht erreichbar. Bitte später erneut versuchen."
        return
    } finally {
        submitButton.disabled = false
    }

    if (response.status === 401) {
        errorText.textContent = "E-Mail oder Passwort ist falsch"
        errorText.hidden = false
        return
    }

    if (response.status === 423) {
        errorText.textContent = "Ihr Antrag wurde abgelehnt"
        errorText.hidden = false
        return
    }

    if (response.status === 403) {
        errorText.textContent = "Ihr Konto wartet auf Freigabe"
        errorText.hidden = false
        return
    }

    if (!response.ok) {
        errorText.textContent = "Etwas ist schief gegangen"
        errorText.hidden = false
        return
    }

    errorText.hidden = true
    localStorage.setItem("token", data.access_token)

})