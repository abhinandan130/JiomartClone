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


/* ===============================
   CART HOVER LOGIC (NO HTML HERE)
=============================== */

document.addEventListener("DOMContentLoaded", () => {
    const cartHover = document.querySelector(".cart-hover");
    const emptyBox = document.getElementById("cart-hover-empty");
    const itemsBox = document.getElementById("cart-hover-items");
    const itemsContainer = document.getElementById("cart-hover-content");
    const totalContainer = document.getElementById("cart-hover-total");

    if (!cartHover || !itemsBox || !itemsContainer || !totalContainer) return;

    const hideAll = () => {
        emptyBox?.classList.add("d-none");
        itemsBox.classList.add("d-none");
    };

    const loadCartPreview = async () => {
        try {
            const res = await fetch("/api/cart/preview/");
            if (!res.ok) return;

            const data = await res.json();
            hideAll();

            // EMPTY CART
            if (!data.items || data.items.length === 0) {
                emptyBox?.classList.remove("d-none");
                return;
            }

            // ITEMS
            itemsContainer.innerHTML = "";

            data.items.forEach(item => {
                const row = document.createElement("div");
                row.className = "d-flex align-items-center justify-content-between gap-2 small";

                row.innerHTML = `
                    <div class="d-flex align-items-center gap-2">
                        <img src="${item.image}"
                            alt="${item.name}"
                            style="width:38px;height:38px;object-fit:contain;"
                            class="border rounded">

                        <div>
                            <strong>${item.name}</strong><br>
                            <span class="text-muted">Qty: ${item.quantity ?? item.qty}</span>
                        </div>
                    </div>

                    <div class="fw-semibold">₹${item.subtotal}</div>
                `;

                itemsContainer.appendChild(row);
            });


            totalContainer.textContent = `Total: ₹${data.total ?? data.total_amount}`;
            itemsBox.classList.remove("d-none");

        } catch (err) {
            console.error("Cart hover error:", err);
        }
    };

    cartHover.addEventListener("mouseenter", loadCartPreview);
});

/* ===============================
   LIVE SEARCH SUGGESTIONS
=============================== */

document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("search-input");
    const dropdown = document.getElementById("search-dropdown");

    if (!input || !dropdown) return;

    let controller = null;

    input.addEventListener("input", async () => {
        const query = input.value.trim();

        if (query.length < 2) {
            dropdown.classList.remove("show");
            dropdown.innerHTML = "";
            return;
        }

        if (controller) controller.abort();
        controller = new AbortController();

        try {
            const res = await fetch(
                `/api/search/suggestions/?q=${encodeURIComponent(query)}`,
                { signal: controller.signal }
            );

            const data = await res.json();

            if (!data.results.length) {
                dropdown.innerHTML = `
                    <div class="search-item text-muted">
                        No results found
                    </div>
                `;
                dropdown.classList.add("show");
                return;
            }

            dropdown.innerHTML = data.results.map(item => `
                <div class="search-item"
                     onclick="window.location.href='/?q=${encodeURIComponent(item.name)}'">
                    ${item.name}
                </div>
            `).join("");

            dropdown.classList.add("show");

        } catch (err) {
            if (err.name !== "AbortError") {
                console.error("Search error:", err);
            }
        }
    });

    document.addEventListener("click", (e) => {
        if (!e.target.closest(".search")) {
            dropdown.classList.remove("show");
        }
    });
});
