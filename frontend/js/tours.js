import { sendRequest, formDate, getInitials, homePageFor, escapeHtml } from "./app.js"

const errorPage = document.querySelector("#page-error")
const pageOk = document.querySelector("#page-ok")

const listView = document.querySelector("#list-view")
const detailView = document.querySelector("#detail-view")

const driverName = document.querySelector("#driver-name")
const driverAvatar = document.querySelector("#driver-avatar")
const tabs = document.querySelector("#tour-tabs")
const toursList = document.querySelector("#tours-list")
const countActive = document.querySelector("#count-active")
const countDone = document.querySelector("#count-done")
const logout = document.querySelector("#logout")

const tourId = document.querySelector("#tour-id")
const tourRoute = document.querySelector("#tour-route")
const tourStatus = document.querySelector("#tour-status")
const tourSteps = document.querySelector("#tour-steps")
const tourOrigin = document.querySelector("#tour-origin")
const tourPickup = document.querySelector("#tour-pickup")
const tourDestination = document.querySelector("#tour-destination")
const tourWeight = document.querySelector("#tour-weight")
const statusButton = document.querySelector("#status-button")
const doneNote = document.querySelector("#tour-done-note")
const backButton = document.querySelector("#back-button")

const SERVER_ERROR = "Server ist nicht erreichbar"

const STATUS_LABELS = {
    new: "Neu",
    assigned: "Zugewiesen",
    in_transit: "Unterwegs",
    delivered: "Zugestellt"
}

// Следующий шаг для водителя — те же переходы, что в services/loads.py (allowed_transit)
const NEXT_STEP = {
    assigned: { status: "in_transit", label: "Tour starten", ok: "Tour gestartet" },
    in_transit: { status: "delivered", label: "Als zugestellt melden", ok: "Tour zugestellt" }
}

const STEP_ORDER = ["assigned", "in_transit", "delivered"]

const STATUS_ERRORS = {
    "Invalid status transition": "Dieser Statuswechsel ist nicht möglich",
    "This load is not assigned to you": "Diese Tour gehört nicht Ihnen",
    "Load not found": "Tour wurde nicht gefunden"
}

let tours = []
let activeTab = "active"
let openTourId = null
let pageOkTimer = null

function showError(text) {
    errorPage.hidden = false
    errorPage.textContent = text
}

function showPageOk(text) {
    pageOk.hidden = false
    pageOk.textContent = text

    clearTimeout(pageOkTimer)
    pageOkTimer = setTimeout(() => {
        pageOk.hidden = true
    }, 3500)
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

async function getTours() {
    let response

    try {
        response = await sendRequest("loads", "get")
    } catch {
        showError(SERVER_ERROR)
        return
    }

    if (!response.ok) {
        showError("Touren konnten nicht geladen werden")
        return
    }

    return response.data
}

function renderList() {
    const active = tours.filter(t => t.status !== "delivered")
    const done = tours.filter(t => t.status === "delivered")

    countActive.textContent = active.length
    countDone.textContent = done.length

    // актуальные — ближайшие сверху, выполненные — последние сверху
    const visible = activeTab === "active"
        ? active.toSorted((a, b) => new Date(a.pickup_date) - new Date(b.pickup_date))
        : done.toSorted((a, b) => new Date(b.pickup_date) - new Date(a.pickup_date))

    if (visible.length === 0) {
        toursList.innerHTML = `<p class="tours-empty">${activeTab === "active" ? "Keine aktuellen Touren" : "Noch keine erledigten Touren"}</p>`
        return
    }

    toursList.innerHTML = visible.map(tour => `
        <button type="button" class="tour" data-tour-id="${tour.id}">
            <span class="tour-stripe stripe ${tour.status}"></span>
            <span class="tour-text">
                <span class="tour-num mono">#${tour.id}</span>
                <span class="tour-route">${escapeHtml(tour.origin)} <span class="route-arrow">→</span> ${escapeHtml(tour.destination)}</span>
                <span class="tour-meta mono">${formDate(tour.pickup_date)} · ${tour.weight} t</span>
            </span>
            <span class="status ${tour.status}">${STATUS_LABELS[tour.status]}</span>
        </button>`).join("")
}

function renderDetail(tour) {
    tourId.textContent = `#${tour.id}`
    tourRoute.textContent = `${tour.origin} → ${tour.destination}`
    tourStatus.className = `status ${tour.status}`
    tourStatus.textContent = STATUS_LABELS[tour.status]

    const currentIndex = STEP_ORDER.indexOf(tour.status)

    for (const step of tourSteps.querySelectorAll("[data-step]")) {
        const index = STEP_ORDER.indexOf(step.dataset.step)
        step.classList.toggle("done", index < currentIndex)
        step.classList.toggle("now", index === currentIndex)
    }

    tourOrigin.textContent = tour.origin
    tourPickup.textContent = formDate(tour.pickup_date)
    tourDestination.textContent = tour.destination
    tourWeight.textContent = `${tour.weight} t`

    const next = NEXT_STEP[tour.status]

    statusButton.hidden = !next
    statusButton.disabled = false
    doneNote.hidden = Boolean(next)

    if (next) {
        statusButton.textContent = next.label
    }
}

function openTour(id) {
    const tour = tours.find(t => t.id === id)

    if (!tour) {
        return
    }

    openTourId = id
    errorPage.hidden = true
    renderDetail(tour)
    listView.hidden = true
    detailView.hidden = false
    scrollTo({ top: 0 })
}

function closeTour() {
    openTourId = null
    renderList()
    detailView.hidden = true
    listView.hidden = false
}

tabs.addEventListener("click", (event) => {
    const btn = event.target.closest("button")

    if (!btn) {
        return
    }

    activeTab = btn.dataset.tab

    for (const button of tabs.querySelectorAll("button")) {
        button.classList.toggle("on", button === btn)
    }

    renderList()
})

toursList.addEventListener("click", (event) => {
    const card = event.target.closest(".tour")

    if (!card) {
        return
    }

    openTour(Number(card.dataset.tourId))
})

backButton.addEventListener("click", closeTour)

statusButton.addEventListener("click", async () => {
    const tour = tours.find(t => t.id === openTourId)
    const next = tour && NEXT_STEP[tour.status]

    if (!next) {
        return
    }

    statusButton.disabled = true
    errorPage.hidden = true
    let response

    try {
        response = await sendRequest(`loads/${tour.id}/status`, "patch", { new_status: next.status })
    } catch {
        showError(SERVER_ERROR)
        statusButton.disabled = false
        return
    }

    if (response.status === 401) {
        localStorage.clear()
        location.replace("index.html")
        return
    }

    if (!response.ok) {
        showError(STATUS_ERRORS[response.data?.detail] ?? "Status konnte nicht geändert werden")
        statusButton.disabled = false
        return
    }

    tours = tours.map(t => t.id === tour.id ? response.data : t)
    renderDetail(response.data)
    showPageOk(next.ok)
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

    // экран только для водителя
    if (user.role !== "driver") {
        location.replace(homePageFor(user.role))
        return
    }

    driverName.textContent = `${user.name} · Fahrer`
    driverAvatar.textContent = getInitials(user.name)

    const data = await getTours()

    if (!data) {
        toursList.innerHTML = ""
        return
    }

    tours = data
    renderList()
}

init()
