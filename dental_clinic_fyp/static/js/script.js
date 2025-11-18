// Example: Confirm before deleting a doctor or appointment
function confirmDelete(itemType) {
    return confirm(`Are you sure you want to delete this ${itemType}?`);
}

// Toggle password visibility in forms
function togglePassword(inputId, toggleBtnId) {
    const input = document.getElementById(inputId);
    const btn = document.getElementById(toggleBtnId);
    if (input.type === "password") {
        input.type = "text";
        btn.innerText = "Hide";
    } else {
        input.type = "password";
        btn.innerText = "Show";
    }
}

// Simple alert for form submissions
function showAlert(message, type = "success") {
    const alertDiv = document.createElement("div");
    alertDiv.className = `alert alert-${type} mt-3`;
    alertDiv.innerText = message;
    const container = document.querySelector(".container, .row");
    container.prepend(alertDiv);
    setTimeout(() => alertDiv.remove(), 3000);
}
