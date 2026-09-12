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

const detailId = document.querySelector("#detail-id")
const detailStatus = document.querySelector("#detail-status")
const detailOrigin = document.querySelector("#detail-origin")
const detailPickUp = document.querySelector("#detail-pickup")
const detailDestination = document.querySelector("#detail-destination")
const detailDriver = document.querySelector("#detail-driver")
const detailWeight = document.querySelector("#detail-weight")
const detailRate = document.querySelector("#detail-rate")
const detailCreated = document.querySelector("#detail-created")

const detailEmpty = document.querySelector("#detail-empty")
const detailBody = document.querySelector("#detail-body")

const logout = document.querySelector("#logout")

const STATUS_LABELS = {
    new: "Neu",
    assigned: "Zugewiesen",
    in_transit: "Unterwegs",
    delivered: "Zugestellt",

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


    return {
        loads: response.data,
        activeLoadsAmount: response.data.filter(l => l.status !== "delivered").length,
        allLoadsAmount: response.data.length,
        newLoads: response.data.filter(l => l.status === "new").length,
        loadsInTransit: response.data.filter(l => l.status === "in_transit").length,
        loadsPreis: response.data.filter(l => l.status !== "delivered").reduce((a, b) => a + Number(b.rate), 0)
    }
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
                        <td class="stripe ${STATUS_LABELS[load.status]}"></td>
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

tbody.addEventListener("click", (event) => {
    const tr = event.target.closest("tr")
    if (!tr) {
        return
    }
    const load = currentLoads.loads.find(l => l.id === Number(tr.dataset.loadId))
    console.log(load)

    renderLoadDetails(load)
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

    currentLoads = await getLoads()

    if (currentLoads) {
        allLoadsInHistory.textContent = currentLoads.allLoadsAmount
        activeLoads.textContent = currentLoads.activeLoadsAmount
        newLoads.textContent = currentLoads.newLoads
        loadsInTransit.textContent = currentLoads.loadsInTransit
        loadsPreis.textContent = `${currentLoads.loadsPreis.toFixed(2)
            } €`

        renderLoads(currentLoads.loads)
    }
}

init()