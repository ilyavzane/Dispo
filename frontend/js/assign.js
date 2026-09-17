import { sendRequest, formDate, getInitials } from "./app.js"

const logout = document.querySelector("#logout")
const errorPage = document.querySelector("#page-error")
const pageOk = document.querySelector("#page-ok")
const tbody = document.querySelector("#loads-tbody")

const avatar = document.querySelector("#rail-avatar")
const username = document.querySelector("#rail-name")
const userRole = document.querySelector("#rail-role")

const newLoadsAmount = document.querySelector("#rail-count-unassigned")
const loadsAmount = document.querySelector("#rail-count-loads")
const headCount = document.querySelector("#head-count")

const detailBody = document.querySelector("#detail-body")
const detailEmpty = document.querySelector("#detail-empty")
const detailId = document.querySelector("#detail-id")
const detailOrigin = document.querySelector("#detail-origin")
const detailPickupDate = document.querySelector("#detail-pickup")
const detailDestination = document.querySelector("#detail-destination")
const detailWeight = document.querySelector("#detail-weight")
const detailRate = document.querySelector("#detail-rate")

const driverFilters = document.querySelector("#driver-filters")
const drivers = document.querySelector("#drivers-list")

let pageOkTimer = null;
let selectedDriverId = null
let selectedLoadId = null;
let newLoads = null;
let selectedFilter = "true";
// номер последнего запроса водителей: ответы старых запросов игнорируем
let driversRequestId = 0

const assignBtn = document.querySelector("#assign-button")

const SERVER_ERROR = "Server ist nicht erreichbar"

// detail с бэкенда (services/loads.py) → текст для пользователя
const ASSIGN_ERRORS = {
    "Load not found": "Ladung wurde nicht gefunden",
    "Driver not found": "Fahrer wurde nicht gefunden",
    "User with this id is not driver": "Dieser Benutzer ist kein Fahrer",
    "Driver is not approved": "Fahrer ist noch nicht freigeschaltet",
    "Load is already delivered": "Ladung ist bereits zugestellt",
}

function showError(text) {
    errorPage.hidden = false
    errorPage.textContent = text
}

async function checkUser() {
    let response;

    try {
        response = await sendRequest("me", "get")
    }
    catch {
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

    errorPage.hidden = true
    return response.data
}

async function getDrivers(available) {
    errorPage.hidden = true
    let response;

    try {
        response = await sendRequest(available ? `drivers?available=${available}` : "drivers", "get")
    } catch {
        showError(SERVER_ERROR)
        return
    }

    if (!response.ok) {
        showError("Fahrer konnten nicht geladen werden")
        return
    }
    return response.data
}

function renderLoads(loads) {
    if (loads.length === 0) {
        tbody.innerHTML = `<tr class="rows-empty"><td colspan="6">Keine Ladungen</td></tr>`
        return
    }

    const html = loads.map(load => `<tr data-load-id= "${load.id}">
                            <td class="stripe new"></td>
                            <td class="route">${load.origin} <span class="route-arrow">→</span> ${load.destination}
                                <span class="load-id mono">#${load.id}</span>
                            </td>
                            <td class="muted mono">${formDate(load.pickup_date)}</td>
                            <td><span class="status new">Neu</span></td>
                            <td class="right mono">${load.weight} t</td>
                            <td class="right mono">${load.rate} €</td>
                        </tr>`).join("")

    tbody.innerHTML = html
}

function renderDetails(load) {
    detailBody.hidden = false
    detailEmpty.hidden = true

    detailId.textContent = `#${load.id}`
    detailOrigin.textContent = load.origin
    detailPickupDate.textContent = formDate(load.pickup_date)
    detailDestination.textContent = load.destination
    detailWeight.textContent = `${load.weight} t`
    detailRate.textContent = `${load.rate} €`
}

async function renderDrivers(available) {
    const requestId = ++driversRequestId

    const driversList = await getDrivers(available)

    // пока ждали ответ, пользователь кликнул ещё раз — этот ответ уже устарел
    if (requestId !== driversRequestId) {
        return
    }

    if (!driversList) {
        return
    }

    if (driversList.length === 0) {
        if (available) {
            drivers.innerHTML = `<p class="drivers-empty">Gerade ist kein Fahrer frei.</p>`
        }
        else {
            drivers.innerHTML = `<p class="drivers-empty">Es gibt noch keine Fahrer.</p>`
        }
        return
    }

    const html = driversList.map(driver =>
        `<button type="button" class="driver" data-driver-id="${driver.id}">
                        <span class="driver-avatar mono">${getInitials(driver.name)}</span>
                        <span class="driver-text">
                            <span class="driver-name">${driver.name}</span>
                            <span class="driver-mail mono">${driver.email}</span>
                        </span>
                        <span class="driver-free ${driver.is_available ? "yes" : "no"}">${driver.is_available ? "frei" : "belegt"}</span>
                    </button>`).join("")

    drivers.innerHTML = html
}

tbody.addEventListener("click", (event) => {
    const tr = event.target.closest("tr")

    if (!tr) {
        return
    }

    const load = newLoads.find(l => l.id === Number(tr.dataset.loadId))
    if (!load) {
        return
    }

    for (const row of tbody.querySelectorAll("tr")) {
        row.classList.toggle("selected", row === tr)
    }

    assignBtn.disabled = true
    selectedDriverId = null

    selectedLoadId = load.id
    renderDetails(load)
    renderDrivers(selectedFilter)
})

driverFilters.addEventListener("click", (event) => {
    const btn = event.target.closest("button")

    if (!btn) {
        return
    }

    selectedDriverId = null
    assignBtn.disabled = true

    selectedFilter = btn.dataset.available

    for (const button of driverFilters.querySelectorAll("button")) {
        button.classList.toggle("on", button === btn)
    }

    renderDrivers(selectedFilter)
})

drivers.addEventListener("click", (event) => {
    const btn = event.target.closest("button")

    if (!btn) {
        return
    }

    for (const card of drivers.querySelectorAll(".driver")) {
        card.classList.toggle("selected", card === btn)
    }
    selectedDriverId = Number(btn.dataset.driverId)
    assignBtn.disabled = false
})

assignBtn.addEventListener("click", async () => {
    let response;
    errorPage.hidden = true
    // блокируем кнопку на время запроса, чтобы двойной клик не отправил два PATCH
    assignBtn.disabled = true

    try {
        response = await sendRequest(`loads/${selectedLoadId}/assign`, "patch", { driver_id: selectedDriverId })
    }
    catch {
        showError(SERVER_ERROR)
        assignBtn.disabled = false
        return
    }

    if (response.status === 401) {
        location.replace("index.html")
        return
    }

    if (!response.ok) {
        showError(ASSIGN_ERRORS[response.data?.detail] ?? "Zuweisung fehlgeschlagen")
        assignBtn.disabled = false
        return
    }

    newLoads = newLoads.filter(l => l.id !== selectedLoadId)
    renderLoads(newLoads)
    newLoadsAmount.textContent = newLoads.length
    headCount.textContent = newLoads.length

    selectedDriverId = null
    selectedLoadId = null
    detailBody.hidden = true
    detailEmpty.hidden = false

    pageOk.hidden = false
    pageOk.textContent = "Fahrer zugewiesen"

    clearTimeout(pageOkTimer)

    pageOkTimer = setTimeout(() => {
        pageOk.hidden = true
    }, 3500)
})

async function getLoads() {
    errorPage.hidden = true
    let response;

    try {
        response = await sendRequest("loads", "get")
    } catch {
        showError(SERVER_ERROR)
        return
    }

    if (!response.ok) {
        showError("Ladungen konnten nicht geladen werden")
        return
    }
    return response.data
}


logout.addEventListener("click", () => {
    localStorage.clear()
    location.replace("index.html")
})

async function init() {
    const user = await checkUser()

    if (!user) {
        return
    }

    avatar.textContent = getInitials(user.name)
    username.textContent = user.name
    userRole.textContent = user.role

    const loads = await getLoads()

    if (!loads) {
        return
    }

    newLoads = loads.filter(l => l.status === "new")
    renderLoads(newLoads)

    newLoadsAmount.textContent = newLoads.length
    loadsAmount.textContent = loads.length

    headCount.textContent = newLoads.length
}

init()
