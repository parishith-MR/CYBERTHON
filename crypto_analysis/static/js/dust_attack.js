async function sendDustAttack() {
    const walletsInput = document.getElementById("wallet-input").value.trim();
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
        const response = await fetch("/api/dust_attack/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken // Include CSRF token in headers
            },
            body: JSON.stringify({ wallets })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();

        if (!data.results || data.results.length === 0) {
            resultsList.innerHTML = `<li class='text-yellow-400'>⚠️ No transactions were processed.</li>`;
            return;
        }

        data.results.forEach(tx => {
            const listItem = document.createElement("li");
            listItem.classList.add("text-green-400", "mt-2");
            listItem.innerHTML = `✅ Sent dust to <strong>${tx.wallet}</strong>: Tx Hash - 
                <a href="https://etherscan.io/tx/${tx.tx_hash}" target="_blank" class="text-blue-400 underline">${tx.tx_hash}</a>`;
            resultsList.appendChild(listItem);
        });

        alert("Dust attack simulated! Check the console for details.");
        console.log("Dust Attack Results:", data.results);

    } catch (error) {
        console.error("Error sending dust attack:", error);
        resultsList.innerHTML = `<li class='text-red-400'>❌ Failed to send dust. Please try again.</li>`;
    }
}

// Attach event listener to the form
document.getElementById("dust-form").addEventListener("submit", function(event) {
    event.preventDefault();
    sendDustAttack();
});
