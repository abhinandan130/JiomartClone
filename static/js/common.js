/* ===============================
   COMMON JS UTILITIES
   =============================== */

document.addEventListener("DOMContentLoaded", () => {
    console.log("Common JS loaded");

    // Run cart count once globally
    if (typeof refreshCartCount === "function") {
        refreshCartCount();
    }
});

/* ---------- DOM HELPERS ---------- */

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => document.querySelectorAll(selector);

/* ---------- FETCH HELPER ---------- */

const apiFetch = (url, onSuccess, onError = null, options = {}) => {
    fetch(url, options)
        .then(res => {
            if (!res.ok) throw new Error("Network response failed");
            return res.json();
        })
        .then(data => onSuccess(data))
        .catch(err => {
            console.error("API Error:", err);
            if (onError) onError(err);
        });
};

/* ---------- ACTIVE CLASS TOGGLER ---------- */

const toggleActive = (elements, activeEl, className = "active") => {
    elements.forEach(el => el.classList.remove(className));
    activeEl.classList.add(className);
};

/* ---------- SIMPLE TOAST (OPTIONAL) ---------- */

const showToast = (message, type = "success") => {
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.innerText = message;

    document.body.appendChild(toast);

    setTimeout(() => toast.classList.add("show"), 50);
    setTimeout(() => {
        toast.classList.remove("show");
        setTimeout(() => toast.remove(), 300);
    }, 3000);
};

/* ===============================
   CART COUNT (GLOBAL)
   =============================== */

window.refreshCartCount = async function () {
    try {
        const res = await fetch("/api/cart/count/");
        if (!res.ok) return;

        const data = await res.json();
        const badge = document.getElementById("cart-count");
        if (!badge) return;

        if (data.count > 0) {
            badge.textContent = data.count;
            badge.style.display = "inline-block";
        } else {
            badge.style.display = "none";
        }
    } catch (err) {
        console.error("Cart count error:", err);
    }
};
