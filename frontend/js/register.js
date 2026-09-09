import { API } from "./app.js";

const form = document.querySelector("form")
const errorText = document.querySelector(".login-error-block")
const submitButton = document.querySelector(".submit-button")

form.addEventListener("submit", async (e) => {
    e.preventDefault()
    submitButton.disabled = true;

    const payload = Object.fromEntries(new FormData(form))
    let response;
    let data;
    try {
        response = await fetch(`${API}/auth/register`,
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



    if (response.status === 422) {
        errorText.textContent = "Bitte prüfen Sie Ihre Eingaben"
        errorText.hidden = false
        return
    }

    if (response.status === 409) {
        errorText.textContent = "Diese E-mail ist bereits vergeben"
        errorText.hidden = false
        return
    }

    if (!response.ok) {
        errorText.textContent = "Etwas ist schief gelaufen. Bitte später erneut versuchen"
        errorText.hidden = false
        return
    }
    errorText.hidden = true
    location.replace("pending.html")
    sessionStorage.setItem("pendingUser", JSON.stringify(data))
})