
const createdAtFeld = document.querySelector("#created_at")
const role = document.querySelector("#role")
const email = document.querySelector("#email")
const status = document.querySelector("#status")

const logoutBtn = document.querySelector(".abmelden-button")
const user = JSON.parse(sessionStorage.getItem("pendingUser"))


function render() {
    if (user === null) {
        /*location.replace("index.html")*/
        return
    }

    const createdAt = new Date(user.created_at)

    const datePart = createdAt.toLocaleDateString("de-DE", { day: "2-digit", month: "2-digit", year: "numeric" })
    const timePart = createdAt.toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit" })

    createdAtFeld.textContent = `${datePart} · ${timePart}`
    role.textContent = user.role === "driver" ? "Fahrer" : "Disponent"
    email.textContent = user.email
    status.textContent = "In Prüfung"
}

render()

logoutBtn.addEventListener("click", () => {
    sessionStorage.removeItem("pendingUser")
    location.replace("index.html")
})