import { sendRequest, formDate, errorMessage, renderRail, homePageFor } from "./app.js"

const logout = document.querySelector("#logout")
const errorPage = document.querySelector("#page-error")
const pageOk = document.querySelector("#page-ok")

const loadsAmount = document.querySelector("#rail-count-loads")
const newLoadsAmount = document.querySelector("#rail-count-unassigned")

const form = document.querySelector("#new-load-form")
const formError = document.querySelector("#form-error")
const submitBtn = document.querySelector("#form-submit")

const fOrigin = document.querySelector("#f-origin")
const fDestination = document.querySelector("#f-destination")
const fPickup = document.querySelector("#f-pickup")
const fWeight = document.querySelector("#f-weight")
const fRate = document.querySelector("#f-rate")

const previewOrigin = document.querySelector("#preview-origin")
const previewDestination = document.querySelector("#preview-destination")
const previewPickup = document.querySelector("#preview-pickup")
const previewWeight = document.querySelector("#preview-weight")
const previewRate = document.querySelector("#preview-rate")
const previewPerTon = document.querySelector("#preview-per-ton")

const SERVER_ERROR = "Server ist nicht erreichbar"

let pageOkTimer = null

function showError(text) {
    errorPage.hidden = false
    errorPage.textContent = text
}

function showFormError(text) {
    formError.hidden = false
    formError.textContent = text
}

function showPageOk(text) {
    pageOk.hidden = false
    pageOk.textContent = text

    clearTimeout(pageOkTimer)
    pageOkTimer = setTimeout(() => {
        pageOk.hidden = true
    }, 3500)
}

// datetime-local ждёт "2026-09-20T14:30" в ЛОКАЛЬНОМ времени
function toLocalInputValue(date) {
    const pad = number => String(number).padStart(2, "0")

    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`
}

function renderPreview() {
    previewOrigin.textContent = fOrigin.value.trim() || "—"
    previewDestination.textContent = fDestination.value.trim() || "—"
    previewPickup.textContent = fPickup.value ? formDate(fPickup.value) : "—"

    const weight = Number(fWeight.value)
    const rate = Number(fRate.value)

    previewWeight.textContent = weight > 0 ? `${weight.toFixed(2)} t` : "—"
    previewRate.textContent = rate > 0 ? `${rate.toFixed(2)} €` : "—"
    previewPerTon.textContent = weight > 0 && rate > 0 ? `${(rate / weight).toFixed(2)} €/t` : "—"
}

// Проверка до отправки: те же правила, что в схеме LoadCreate,
// чтобы не гонять запрос ради очевидной ошибки
function validate() {
    const errors = []

    if (!fOrigin.value.trim()) {
        errors.push("Von darf nicht leer sein")
    }

    if (!fDestination.value.trim()) {
        errors.push("Nach darf nicht leer sein")
    }

    if (!fPickup.value) {
        errors.push("Abholung fehlt")
    } else if (new Date(fPickup.value) < new Date()) {
        errors.push("Abholung muss in der Zukunft liegen")
    }

    if (!(Number(fWeight.value) > 0)) {
        errors.push("Gewicht muss größer als 0 sein")
    }

    if (!(Number(fRate.value) > 0)) {
        errors.push("Preis muss größer als 0 sein")
    }

    return errors
}

async function checkUser() {
    let response

    try {
        response = await sendRequest("me", "get")
    } catch {
        showError(SERVER_ERROR)
        return
    }

    if (response.status === 401 || response.status === 403) {
        location.replace("index.html")
        return
    }

    if (!response.ok) {
        showError("Benutzerdaten konnten nicht geladen werden")
        return
    }

    return response.data
}

// Только для счётчиков в меню. Если не загрузились — страница всё равно работает.
async function renderCounts() {
    let response

    try {
        response = await sendRequest("loads", "get")
    } catch {
        return
    }

    if (!response.ok) {
        return
    }

    loadsAmount.textContent = response.data.length
    newLoadsAmount.textContent = response.data.filter(l => l.status === "new").length
}

form.addEventListener("input", renderPreview)

form.addEventListener("reset", () => {
    formError.hidden = true
    // reset очищает поля уже ПОСЛЕ этого события, поэтому превью обновляем в следующем тике
    setTimeout(renderPreview)
})

form.addEventListener("submit", async (event) => {
    event.preventDefault()
    formError.hidden = true
    errorPage.hidden = true

    const errors = validate()

    if (errors.length > 0) {
        showFormError(errors.join("\n"))
        return
    }

    const payload = {
        origin: fOrigin.value.trim(),
        destination: fDestination.value.trim(),
        // datetime-local без часового пояса, а схема ждёт AwareDatetime → переводим в UTC
        pickup_date: new Date(fPickup.value).toISOString(),
        weight: fWeight.value,
        rate: fRate.value,
    }

    let response
    submitBtn.disabled = true

    try {
        response = await sendRequest("loads", "post", payload)
    } catch {
        showFormError(SERVER_ERROR)
        submitBtn.disabled = false
        return
    }

    submitBtn.disabled = false

    if (response.status === 401) {
        localStorage.clear()
        location.replace("index.html")
        return
    }

    if (response.status === 403) {
        showFormError("Nur Disponenten dürfen Ladungen anlegen")
        return
    }

    if (!response.ok) {
        showFormError(errorMessage(response))
        return
    }

    form.reset()
    renderPreview()
    renderCounts()
    showPageOk(`Ladung #${response.data.id} angelegt`)
    fOrigin.focus()
})

logout.addEventListener("click", () => {
    localStorage.clear()
    location.replace("index.html")
})

async function init() {
    const user = await checkUser()

    if (!user) {
        return
    }

    if (user.role === "driver") {
        location.replace(homePageFor(user.role))
        return
    }

    renderRail(user)

    // нельзя выбрать дату в прошлом
    fPickup.min = toLocalInputValue(new Date())

    renderCounts()
    renderPreview()
}

init()
