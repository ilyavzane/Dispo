
export const API = "http://127.0.0.1:8000";

export function getToken() {
    return localStorage.getItem("token")

}

export async function sendRequest(path, payload) {
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
