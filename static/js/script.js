document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('consultation-form');
    const endSessionBtn = document.getElementById('end-session-btn');
    
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            console.log('Form submitted');
            
            const message = document.getElementById('message').value;
            const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
            
            try {
                console.log('Sending request to /consultations/send');
                const response = await fetch('/consultations/send', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({ message: message })
                });
                
                console.log('Response received:', response.status);
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                console.log('Response data:', data);
                
                if (data.success) {
                    document.getElementById('message').value = '';
                    const userMessage = `
                        <div class="dialog-message card mb-3 bg-light">
                            <div class="card-body">
                                <div class="d-flex justify-content-between">
                                    <span class="text-muted">User</span>
                                    <small class="text-muted">${new Date().toLocaleTimeString()}</small>
                                </div>
                                <p class="card-text mt-2">${message}</p>
                            </div>
                        </div>
                    `;
                    document.getElementById('current-dialog').insertAdjacentHTML('beforeend', userMessage);
                    
                    if (data.response) {
                        const assistantMessage = `
                            <div class="dialog-message card mb-3">
                                <div class="card-body">
                                    <div class="d-flex justify-content-between">
                                        <span class="text-muted">Assistant</span>
                                        <small class="text-muted">${new Date().toLocaleTimeString()}</small>
                                    </div>
                                    <p class="card-text mt-2">${data.response}</p>
                                </div>
                            </div>
                        `;
                        document.getElementById('current-dialog').insertAdjacentHTML('beforeend', assistantMessage);
                    }
                } else {
                    alert(data.message || 'Произошла ошибка');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Произошла ошибка при отправке');
            }
        });
    }

    if (endSessionBtn) {
        endSessionBtn.addEventListener('click', async function() {
            if (confirm('Завершить текущую консультацию? История диалога будет сохранена.')) {
                const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
                
                try {
                    console.log('Ending session...');
                    const response = await fetch('/consultations/end_session', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken
                        }
                    });
                    
                    console.log('End session response:', response.status);
                    
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    
                    const data = await response.json();
                    console.log('End session data:', data);
                    
                    if (data.success) {
                        window.location.href = '/history';
                    } else {
                        alert('Ошибка при завершении консультации');
                    }
                } catch (error) {
                    console.error('Error:', error);
                    alert('Произошла ошибка');
                }
            }
        });
    }
});
    