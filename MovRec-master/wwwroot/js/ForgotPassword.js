document.addEventListener('DOMContentLoaded', function () {
    const forgotPasswordForm = document.getElementById('forgotPasswordForm');
    const messageDiv = document.getElementById('message');

    forgotPasswordForm.addEventListener('submit', async function (e) {
        e.preventDefault();

        const email = document.getElementById('email').value;
        messageDiv.textContent = 'Sending reset code...';
        messageDiv.className = 'message processing';

        try {
            const response = await fetch('/Account/ForgotPassword', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email: email })
            });

            const result = await response.json();

            if (response.ok) {
                messageDiv.textContent = result.message;
                messageDiv.className = 'message success';
                // Redirect to reset password page after 3 seconds
                setTimeout(() => {
                    window.location.href = '/Account/ResetPassword';
                }, 3000);
            } else {
                messageDiv.textContent = result.message || 'An error occurred. Please try again.';
                messageDiv.className = 'message error';
            }
        } catch (error) {
            messageDiv.textContent = 'An error occurred. Please try again.';
            messageDiv.className = 'message error';
            console.error('Error:', error);
        }
    });
}); 