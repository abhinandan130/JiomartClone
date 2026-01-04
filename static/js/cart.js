document.addEventListener("DOMContentLoaded", () => {
    if (typeof refreshCartCount === "function") {
        refreshCartCount();
    }
});

/* =========================
   + / - QUANTITY HANDLER
   ========================= */
document.addEventListener("click", async (e) => {
    const btn =
        e.target.classList.contains("qty-btn")
            ? e.target
            : e.target.closest("button.qty-btn");

    if (!btn) return;

    const itemId = btn.dataset.id;
    const action = btn.dataset.action;

    try {
        const res = await fetch(`/api/cart/update/${itemId}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify({ action })
        });

        if (!res.ok) {
            console.warn("Cart update failed:", res.status);
            return;
        }

        const data = await res.json();

        const rowEl = document.getElementById(`row-${itemId}`);
        const qtyEl = document.getElementById(`qty-${itemId}`);
        const subtotalEl = document.getElementById(`subtotal-${itemId}`);
        const totalEl = document.getElementById("cart-total");

        if (data.quantity === 0) {
            if (rowEl) rowEl.remove();
            if (totalEl) totalEl.textContent = `$ ${data.cart_total}`;

            if (typeof refreshCartCount === "function") {
                refreshCartCount();
            }

            if (data.cart_total === 0) {
                location.reload();
            }
            return;
        }

        if (qtyEl) qtyEl.textContent = data.quantity;
        if (subtotalEl) subtotalEl.textContent = `$ ${data.subtotal}`;
        if (totalEl) totalEl.textContent = `$ ${data.cart_total}`;

        if (typeof refreshCartCount === "function") {
            refreshCartCount();
        }

    } catch (err) {
        console.error("Cart update error:", err);
    }
});

/* =========================
   CSRF TOKEN
   ========================= */
function getCSRFToken() {
    return document.querySelector("[name=csrfmiddlewaretoken]")?.value;
}
