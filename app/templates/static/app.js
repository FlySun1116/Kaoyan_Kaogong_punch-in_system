/** 轻量提示，替代 alert */
function showToast(message, isError = false) {
    let el = document.getElementById("appToast");
    if (!el) {
        el = document.createElement("div");
        el.id = "appToast";
        el.className = "toast-app";
        el.setAttribute("role", "status");
        document.body.appendChild(el);
    }
    el.textContent = message;
    el.classList.toggle("is-error", isError);
    el.classList.add("show");
    clearTimeout(el._hideTimer);
    el._hideTimer = setTimeout(() => el.classList.remove("show"), 2800);
}

async function parseError(res) {
    try {
        const data = await res.json();
        return data.detail || JSON.stringify(data);
    } catch {
        return "请求失败";
    }
}

/** 高亮当前导航 */
document.addEventListener("DOMContentLoaded", () => {
    const path = window.location.pathname;
    document.querySelectorAll(".site-header .nav-link").forEach((link) => {
        const href = link.getAttribute("href");
        if (href === path || (path !== "/" && href !== "/" && path.startsWith(href))) {
            link.classList.add("active");
        }
    });
});
