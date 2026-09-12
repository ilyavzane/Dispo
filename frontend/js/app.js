
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
