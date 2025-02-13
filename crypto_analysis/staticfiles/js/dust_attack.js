async function sendDustAttack() {
    const walletsInput = document.getElementById("wallets").value;
    const resultsList = document.getElementById("results");
    resultsList.innerHTML = ""; // Clear previous results

    if (!walletsInput) {
        alert("Please enter wallet addresses.");
        return;
    }

    const wallets = walletsInput.split(",").map(addr => addr.trim());

    // Fetch CSRF token from Django's cookie
    function getCSRFToken() {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith("csrftoken=")) {
                    cookieValue = cookie.substring("csrftoken=".length, cookie.length);
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrfToken = getCSRFToken(); // Get CSRF token

    try {
        const response = await axios.post("/api/dust_attack/", { wallets }, {
            headers: { "X-CSRFToken": csrfToken } // Include CSRF token in headers
        });
        
        const data = response.data;

        data.results.forEach(tx => {
            const listItem = document.createElement("li");
            listItem.classList.add("text-green-400", "mt-2");
            listItem.innerHTML = `✅ Sent dust to <strong>${tx.wallet}</strong>: Tx Hash - <a href="${tx.tx_link}" target="_blank" class="text-blue-400 underline">${tx.tx_hash}</a>`;
            resultsList.appendChild(listItem);
        });
    } catch (error) {
        console.error("Error sending dust attack:", error);
        resultsList.innerHTML = `<li class='text-red-400'>❌ Failed to send dust. Please try again.</li>`;
    }
}
document.getElementById("dust-form").addEventListener("submit", function(event) {
    event.preventDefault();
    
    let wallets = document.getElementById("wallet-input").value.split(",");
    
    fetch("/api/dust_attack/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ wallets: wallets })
    })
    .then(response => response.json())
    .then(data => {
        console.log("Dust Attack Results:", data.results);
        alert("Dust attack simulated! Check console for details.");
    })
    .catch(error => console.error("Error:", error));
});
