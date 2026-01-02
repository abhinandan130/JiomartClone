document.addEventListener("DOMContentLoaded", () => {
    const options = $$(".payment-option");
    const paymentInput = $("#payment_method");
    const confirmBtn = $("#confirmBtn");

    if (!options.length) return;

    options.forEach(option => {
        option.addEventListener("click", () => {
            toggleActive(options, option);
            paymentInput.value = option.dataset.method;
            confirmBtn.disabled = false;
            confirmBtn.innerText = "Place Order • ₹" + confirmBtn.dataset.total;
        });
    });
});
