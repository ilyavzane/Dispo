import { sendRequest, formDate, renderRail, homePageFor, escapeHtml, ROLE_LABELS } from "./app.js"

const logout = document.querySelector("#logout")
const errorPage = document.querySelector("#page-error")
const pageOk = document.querySelector("#page-ok")
const tbody = document.querySelector("#users-tbody")
const filters = document.querySelector("#status-filters")
const headCount = document.querySelector("#head-count")

const loadsAmount = document.querySelector("#rail-count-loads")
const newLoadsAmount = document.querySelector("#rail-count-unassigned")
const pendingAmount = document.querySelector("#rail-count-pending")

const SERVER_ERROR = "Server ist nicht erreichbar"

const EMPTY_TEXTS = {
    pending: "Keine offenen Anträge",
    approved: "Keine freigeschalteten Konten",
    rejected: "Keine abgelehnten Anträge"
}

// Какие кнопки показывать в строке в зависимости от текущего статуса
const ACTIONS = {
    pending: [["approved", "Freischalten", "primary"], ["rejected", "Ablehnen", ""]],
    approved: [["rejected", "Sperren", ""]],
    rejected: [["approved", "Freischalten", "primary"]]
}

const OK_TEXTS = {
    approved: "Konto freigeschaltet",
    rejected: "Konto abgelehnt"
}

let activeStatus = "pending"
let users = []
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

async function getUsers(status) {
    let response

    try {
        response = await sendRequest(`users?status=${status}`, "get")
    } catch {
        showError(SERVER_ERROR)
        return
    }

    if (!response.ok) {
        showError("Anträge konnten nicht geladen werden")
        return
    }

    return response.data
}

function renderUsers() {
    headCount.textContent = users.length

    if (users.length === 0) {
        tbody.innerHTML = `<tr class="rows-empty"><td colspan="5">${EMPTY_TEXTS[activeStatus]}</td></tr>`
        return
    }

    tbody.innerHTML = users.map(user => {
        // статус админа бэкенд менять не даёт (403), поэтому кнопок у него нет
        const buttons = user.role === "admin"
            ? `<span class="muted">—</span>`
            : ACTIONS[user.status].map(([newStatus, label, kind]) =>
                `<button class="btn sm ${kind}" type="button" data-user-id="${user.id}" data-new-status="${newStatus}">${label}</button>`
            ).join("")

        return `<tr>
                    <td class="user-name">${escapeHtml(user.name)}</td>
                    <td class="muted mono">${escapeHtml(user.email)}</td>
                    <td>${ROLE_LABELS[user.role] ?? user.role}</td>
                    <td class="muted mono">${formDate(user.created_at)}</td>
                    <td class="right actions">${buttons}</td>
                </tr>`
    }).join("")
}

async function loadUsers() {
    errorPage.hidden = true
    const status = activeStatus
    const data = await getUsers(status)

    // пока ждали ответ, фильтр могли переключить — старый ответ не рисуем
    if (!data || status !== activeStatus) {
        return
    }

    users = data
    renderUsers()

    if (status === "pending") {
        pendingAmount.textContent = users.length
    }
}

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

async function refreshPendingCount() {
    const pending = await getUsers("pending")

    if (pending) {
        pendingAmount.textContent = pending.length
    }
}

filters.addEventListener("click", (event) => {
    const btn = event.target.closest("button")

    if (!btn) {
        return
    }

    activeStatus = btn.dataset.status

    for (const button of filters.querySelectorAll("button")) {
        button.classList.toggle("on", button === btn)
    }

    loadUsers()
})

tbody.addEventListener("click", async (event) => {
    const btn = event.target.closest("button[data-user-id]")

    if (!btn) {
        return
    }

    const userId = Number(btn.dataset.userId)
    const newStatus = btn.dataset.newStatus

    // обе кнопки строки блокируем, пока идёт запрос
    const rowButtons = btn.closest("tr").querySelectorAll("button")
    for (const button of rowButtons) {
        button.disabled = true
    }

    errorPage.hidden = true
    let response

    try {
        response = await sendRequest(`users/${userId}/status`, "patch", { new_status: newStatus })
    } catch {
        showError(SERVER_ERROR)
        for (const button of rowButtons) {
            button.disabled = false
        }
        return
    }

    if (response.status === 401) {
        localStorage.clear()
        location.replace("index.html")
        return
    }

    if (!response.ok) {
        showError(response.status === 404 ? "Konto wurde nicht gefunden" : "Status konnte nicht geändert werden")
        for (const button of rowButtons) {
            button.disabled = false
        }
        return
    }

    // пользователь сменил статус → в текущем фильтре его больше нет
    users = users.filter(u => u.id !== userId)
    renderUsers()
    refreshPendingCount()
    showPageOk(`${OK_TEXTS[newStatus]}: ${response.data.name}`)
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

    // экран только для админа: остальных отправляем на их главную
    if (user.role !== "admin") {
        location.replace(homePageFor(user.role))
        return
    }

    renderRail(user)
    renderCounts()
    loadUsers()
}

init()
