
export const API = "http://127.0.0.1:8000";

export function getToken() {
    return localStorage.getItem("token")

}

export async function sendRequest(path, method_type, payload) {
    const option = {
        method: method_type,
        headers: {
            "Authorization": `Bearer ${getToken()}`
        }
    }

    if (payload) {
        option.body = JSON.stringify(payload)
    }

    if (method_type !== "get") {
        option.headers["Content-Type"] = "application/json"
    }

    const response = await fetch(`${API}/${path}`, option)

    return {
        data: await response.json(),
        ok: response.ok,
        status: response.status
    }
}

export async function sendAuthRequest(path, payload) {
    const response = await fetch(`${API}/auth/${path}`,
        {
            method: "post",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        }
    )

    return {
        data: await response.json(),
        ok: response.ok,
        status: response.status,
    }
}

export function formDate(pickUpDate) {
    const loadPickUpDate = new Date(pickUpDate)

    const datePart = loadPickUpDate.toLocaleDateString("de-DE", { day: "2-digit", month: "2-digit", year: "numeric" })
    const timePart = loadPickUpDate.toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit" })

    return `${datePart} ${timePart}`
}

// "Max Müller" → "MM"
export function getInitials(name) {
    return name.split(" ").map(word => word[0]).join("").toUpperCase()
}

// Имена полей из схем LoadCreate/LoadUpdate -> подписи из <label> в формах.
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

// 422 от Pydantic: detail - МАССИВ объектов {loc, msg, type}.
// Во всех остальных ошибках (400/403/404) detail - обычная строка.
export function errorMessage(response) {
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

export const ROLE_LABELS = {
    dispatcher: "Disponent",
    driver: "Fahrer",
    admin: "Verwaltung"
}

// Общая левая панель рабочих экранов: имя, роль, аватар.
// Раздел "Verwaltung" (Anträge) показываем только админу — остальным бэкенд всё равно ответит 403.
export function renderRail(user) {
    document.querySelector("#rail-avatar").textContent = getInitials(user.name)
    document.querySelector("#rail-name").textContent = user.name
    document.querySelector("#rail-role").textContent = ROLE_LABELS[user.role] ?? user.role

    const adminBlock = document.querySelector("#rail-admin")

    if (adminBlock) {
        adminBlock.hidden = user.role !== "admin"
    }
}

// Куда отправить пользователя после входа или если он открыл чужой экран
export function homePageFor(role) {
    return role === "driver" ? "tours.html" : "loads.html"
}

// Текст от пользователей (имена, города) вставляем в innerHTML только через эту функцию,
// иначе "<b>" в имени станет настоящим тегом
export function escapeHtml(text) {
    return String(text)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
}
