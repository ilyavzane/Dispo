import { sendRequest, API, getToken } from "./app.js";


const username = document.querySelector("#rail-name")
const userRole = document.querySelector("#rail-role")

const errorPage = document.querySelector("#page-error")

const activeLoads = document.querySelector("#kpi-active")
const newLoads = document.querySelector("#kpi-unassigned")
const loadsInTransit = document.querySelector("#kpi-weight")
const loadsPreis = document.querySelector("#kpi-open")
const tbody = document.querySelector("#loads-tbody")
const allLoadsInHistory = document.querySelector("#head-count")

let currentLoads = [];
let selectedLoad = null;

const detailId = document.querySelector("#detail-id")
const detailStatus = document.querySelector("#detail-status")
const detailOrigin = document.querySelector("#detail-origin")
const detailPickUp = document.querySelector("#detail-pickup")
const detailDestination = document.querySelector("#detail-destination")
const detailDriver = document.querySelector("#detail-driver")
const detailWeight = document.querySelector("#detail-weight")
const detailRate = document.querySelector("#detail-rate")
const detailCreated = document.querySelector("#detail-created")

const loadDialog = document.querySelector("#load-dialog")
const editButton = document.querySelector("#detail-edit")
const dialogCancel = document.querySelector("#dialog-cancel")
const dialogNum = document.querySelector("#dialog-num")
const dialogError = document.querySelector("#dialog-error")
const dialogSave = document.querySelector("#dialog-save")
const loadForm = document.querySelector('#load-form')

const fOrigin = document.querySelector("#f-origin")
const fDestination = document.querySelector("#f-destination")
const fPickup = document.querySelector("#f-pickup")
const fWeight = document.querySelector("#f-weight")
const fRate = document.querySelector("#f-rate")

const pageOk = document.querySelector("#page-ok")
let pageOkTimer = null;

const detailEmpty = document.querySelector("#detail-empty")
const detailBody = document.querySelector("#detail-body")

const logout = document.querySelector("#logout")
const railAvatar = document.querySelector("#rail-avatar")
const railCountLoads = document.querySelector("#rail-count-loads")

const filters = document.querySelector("#filters")
// "" = кнопка "Alle", иначе значение data-status
let activeStatus = ""

const STATUS_LABELS = {
    new: "Neu",
    assigned: "Zugewiesen",
    in_transit: "Unterwegs",
    delivered: "Zugestellt",

}

// Имена полей из схемы LoadUpdate -> подписи из <label> в диалоге.
const FIELD_LABELS = {
    origin: "Von",
    destination: "Nach",
    pickup_date: "Abholung",
    weight: "Gewicht",
    rate: "Preis"
}

// Ключ - поле "type" из ошибки Pydantic. Это машинный код, он стабилен;
// "msg" - человеческий текст на английском, на него завязываться нельзя.
const ERROR_TEXTS = {
    value_error: "muss in der Zukunft liegen",
    greater_than: "muss größer als 0 sein",
    decimal_max_places: "darf höchstens 2 Nachkommastellen haben",
    decimal_max_digits: "ist zu groß",
    string_too_short: "darf nicht leer sein",
    timezone_aware: "hat ein ungültiges Format"
}

function showDialogError(message) {
    dialogError.textContent = message
    dialogError.hidden = false
}

function showPageOk(message) {
    pageOk.hidden = false
    pageOk.textContent = message

    clearTimeout(pageOkTimer)
    pageOkTimer = setTimeout(() => {
        pageOk.hidden = true
    }, 3500)
}

// 422 от Pydantic: detail - МАССИВ объектов {loc, msg, type}.
// Во всех остальных ошибках (400/403/404) detail - обычная строка.
function errorMessage(response) {
    const detail = response.data?.detail

    if (typeof detail === "string") {
        return detail
    }

    if (Array.isArray(detail) && detail.length > 0) {
        return detail.map(error => {
            const name = error.loc[error.loc.length - 1]
            const field = FIELD_LABELS[name] ?? name
            const text = ERROR_TEXTS[error.type] ?? "ist ungültig"

            return `${field} ${text}`
        }).join("\n")
    }

    return "Unbekannter Fehler"
}


async function checkUser() {
    let response;

    try {
        response = await sendRequest("me", "get")
    }
    catch (error) {
        errorPage.hidden = false
        errorPage.textContent = error
        return
    }

    if (response.status === 401 || response.status === 403) {
        location.replace("index.html")
        return
    }

    if (!response.ok) {
        errorPage.hidden = false
        errorPage.textContent = response.data
        return
    }

    errorPage.hidden = true
    return response.data
}


async function getLoads() {
    errorPage.hidden = true
    let response;

    try {
        response = await sendRequest("loads", "get")
    } catch (error) {
        errorPage.hidden = false
        errorPage.textContent = error
        return
    }

    if (!response.ok) {
        errorPage.hidden = false
        errorPage.textContent = response.data
        return
    }


    return response.data
}

function formDate(pickUpDate) {
    const loadPickUpDate = new Date(pickUpDate)

    const datePart = loadPickUpDate.toLocaleDateString("de-DE", { day: "2-digit", month: "2-digit", year: "numeric" })
    const timePart = loadPickUpDate.toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit" })

    return `${datePart} ${timePart}`
}

function renderLoads(loads) {
    if (loads.length === 0) {
        tbody.innerHTML = `<tr class="rows-empty"><td colspan="7">Keine Ladungen</td></tr>`
        return
    }

    const html = loads.map(load => `<tr data-load-id="${load.id}">
                        <td class="stripe ${load.status}"></td>
                        <td class="route">${load.origin} <span class="route-arrow">→</span> ${load.destination}
                        <span class="load-id mono">#${load.id}</span>
                        </td>
                        <td class="muted mono">${formDate(load.pickup_date)}</td>
                        <td class="muted">${load.assigned_driver_id ? `Fahrer #${load.assigned_driver_id}` : "—"}</td>
                        <td><span class="status ${load.status}">${STATUS_LABELS[load.status]}</span></td>
                        <td class="right mono">${load.weight} t</td>
                        <td class="right mono">${load.rate} €</td>
                        </tr >`).join("")

    tbody.innerHTML = html
}

function renderLoadDetails(load) {
    detailEmpty.hidden = true
    detailBody.hidden = false

    detailStatus.className = `status ${load.status}`

    detailId.textContent = `#${load.id}`
    detailStatus.textContent = STATUS_LABELS[load.status]
    detailOrigin.textContent = load.origin
    detailPickUp.textContent = formDate(load.pickup_date)
    detailDestination.textContent = load.destination
    detailDriver.textContent = load.assigned_driver_id ?? "-"
    detailWeight.textContent = `${load.weight} t`
    detailRate.textContent = `${load.rate} €`
    detailCreated.textContent = formDate(load.created_at)
}

function renderKpi(loads) {
    const active = loads.filter(l => l.status !== "delivered")

    const activeCount = active.length
    const allCount = loads.length
    const newCount = loads.filter(l => l.status === "new").length
    const transitCount = loads.filter(l => l.status === "in_transit").length
    const sum = active.reduce((total, load) => total + Number(load.rate), 0)

    allLoadsInHistory.textContent = allCount
    railCountLoads.textContent = allCount
    activeLoads.textContent = activeCount
    newLoads.textContent = newCount
    loadsInTransit.textContent = transitCount
    loadsPreis.textContent = `${sum.toFixed(2)} €`
}

function renderVisibleLoads() {
    const visible = activeStatus
        ? currentLoads.filter(load => load.status === activeStatus)
        : currentLoads

    renderLoads(visible)
}

// один обработчик на контейнер вместо пяти на кнопки (делегирование)
filters.addEventListener("click", (event) => {
    const button = event.target.closest("button")

    if (!button) {
        return
    }

    activeStatus = button.dataset.status

    for (const item of filters.querySelectorAll("button")) {
        item.classList.toggle("on", item === button)
    }

    renderVisibleLoads()
})

tbody.addEventListener("click", (event) => {
    const tr = event.target.closest("tr")
    if (!tr) {
        return
    }
    const load = currentLoads.find(l => l.id === Number(tr.dataset.loadId))
    selectedLoad = load
    console.log(load)

    renderLoadDetails(load)
})

editButton.addEventListener("click", () => {
    if (!selectedLoad) {
        return
    }

    dialogError.hidden = true
    dialogNum.textContent = `#${selectedLoad.id}`

    fOrigin.value = selectedLoad.origin
    fDestination.value = selectedLoad.destination
    fPickup.value = selectedLoad.pickup_date.slice(0, 16)
    fWeight.value = selectedLoad.weight
    fRate.value = selectedLoad.rate

    loadDialog.showModal()
})

dialogCancel.addEventListener("click", () => {
    loadDialog.close()
})

loadForm.addEventListener("submit", async (event) => {
    event.preventDefault()

    const fields = {
        origin: fOrigin,
        destination: fDestination,
        pickup_date: fPickup,
        weight: fWeight,
        rate: fRate
    }

    let payload = {};

    for (const [name, input] of Object.entries(fields)) {
        let original = String(selectedLoad[name])

        if (name === "pickup_date") {
            original = original.slice(0, 16)
        }

        if (input.value !== original) {
            // datetime-local отдаёт "2026-09-20T14:30" без часового пояса,
            // а схема ждёт AwareDatetime. Date разбирает это как локальное
            // время, toISOString() переводит в UTC и дописывает "Z".
            payload[name] = name === "pickup_date"
                ? new Date(input.value).toISOString()
                : input.value
        }
    }

    dialogError.hidden = true

    if (Object.keys(payload).length === 0) {
        showDialogError("Keine Änderungen")
        return
    }

    let response

    try {
        response = await sendRequest(`loads/${selectedLoad.id}`, "patch", payload)
    } catch {
        showDialogError("Server nicht erreichbar")
        return
    }

    if (response.status === 401) {
        localStorage.clear()
        location.replace("index.html")
        return
    }

    if (response.status === 404) {
        loadDialog.close()
        errorPage.hidden = false
        errorPage.textContent = "Ladung nicht gefunden"
        return
    }

    if (!response.ok) {
        showDialogError(errorMessage(response))
        return
    }

    if (response.ok) {
        loadDialog.close()
        const index = currentLoads.findIndex(l => l.id === selectedLoad.id)
        currentLoads[index] = response.data
        selectedLoad = response.data
        renderLoadDetails(selectedLoad)
        renderVisibleLoads()
        renderKpi(currentLoads)
        showPageOk("Ladung gespeichert")
    }
})


logout.addEventListener("click", () => {
    localStorage.clear()
    location.replace("index.html")
})

async function init() {

    const userData = await checkUser()

    if (userData === undefined) {
        return
    }

    username.textContent = userData.name
    userRole.textContent = userData.role
    railAvatar.textContent = userData.name.slice(0, 2).toUpperCase()

    currentLoads = await getLoads()

    if (currentLoads === undefined) {
        return
    }

    renderVisibleLoads()
    renderKpi(currentLoads)
}

init()