document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('certificateForm');
    const submitBtn = document.getElementById('submitBtn');
    const errorMessage = document.getElementById('errorMessage');

    const showMessage = (msg, isError = true) => {
        errorMessage.textContent = msg;
        errorMessage.className = `error-message show ${isError ? '' : 'success'}`;

        if (!isError) {
            setTimeout(() => {
                errorMessage.className = 'error-message';
            }, 5000);
        }
    };

    const hideMessage = () => {
        errorMessage.className = 'error-message';
    };

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const name = document.getElementById('name').value;
        const enrollment = document.getElementById('enrollment').value;

        hideMessage();
        submitBtn.classList.add('loading');
        submitBtn.disabled = true;

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name, enrollment })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ message: 'Server error occurred' }));
                throw new Error(errorData.message || 'Failed to generate certificate');
            }

            const blob = await response.blob();

            let filename = 'Certificate.pdf';
            const disposition = response.headers.get('content-disposition');
            if (disposition && disposition.indexOf('attachment') !== -1) {
                const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
                const matches = filenameRegex.exec(disposition);
                if (matches != null && matches[1]) {
                    filename = matches[1].replace(/['"]/g, '');
                }
            }

            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();

            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            showMessage('Certificate downloaded successfully!', false);
            form.reset();
        } catch (error) {
            showMessage(error.message);
        } finally {
            submitBtn.classList.remove('loading');
            submitBtn.disabled = false;
        }
    });
});
