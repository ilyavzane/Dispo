
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
