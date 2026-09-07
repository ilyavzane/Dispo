import { API } from "./app.js";

const form = document.querySelector("form")
const errorText = document.querySelector(".login-error-block")
const submitButton = document.querySelector(".submit-button")

form.addEventListener("submit", async (e) => {
    e.preventDefault()
    submitButton.disabled = true

    const payload = Object.fromEntries(new FormData(form))
    let response;

    try {
        response = await fetch(`${API}/auth/login`,
            {
                method: "post",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    "email": payload.email,
                    "password": payload.password
                })
            }
        )
    } catch (error) {
        errorText.hidden = false
        errorText.textContent = "Server nicht erreichbar. Bitte später erneut versuchen."
        submitButton.disabled = false
        return
    }

    const data = await response.json()

    if (!response.ok) {
        errorText.textContent = data.detail
        errorText.hidden = false
        submitButton.disabled = false
        return
    }

    errorText.hidden = true
    localStorage.setItem("token", data.access_token)

})