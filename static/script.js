document.getElementById('send-btn').addEventListener('click', async () => {
    const queryInput = document.getElementById('query-input');
    const responseContainer = document.getElementById('response-container');
    const query = queryInput.value.trim();

    if (!query) {
        alert('Please enter a query.');
        return;
    }

    responseContainer.textContent = 'Loading...';

    try {
        const response = await fetch('/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query }),
        });

        const data = await response.json();
        if (response.ok) {
            responseContainer.textContent = data.answer;
        } else {
            responseContainer.textContent = data.error || 'An error occurred.';
        }
    } catch (error) {
        responseContainer.textContent = 'An error occurred. Please try again.';
    }
});