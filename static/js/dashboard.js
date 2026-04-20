// Dashboard JavaScript functions

function refreshData() {
    const btn = document.getElementById('refreshBtn');
    const icon = btn.querySelector('i');
    
    btn.disabled = true;
    icon.classList.remove('fa-rotate');
    icon.classList.add('fa-arrows-rotate', 'spin-fast');
    btn.classList.add('opacity-75');
    
    fetch('/api/refresh')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Add a cool fade out effect before reload
                document.body.style.opacity = '0';
                document.body.style.transition = 'opacity 0.4s ease';
                setTimeout(() => {
                    location.reload();
                }, 400);
            } else {
                alert('Error refreshing data: ' + data.error);
                resetButton(btn, icon);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to refresh data');
            resetButton(btn, icon);
        });
}

function resetButton(btn, icon) {
    btn.disabled = false;
    icon.classList.remove('fa-arrows-rotate', 'spin-fast');
    icon.classList.add('fa-rotate');
    btn.classList.remove('opacity-75');
}

function calculateDays() {
    const dayBadges = document.querySelectorAll('.days-badge');
    const today = new Date();
    
    dayBadges.forEach(badge => {
        // Extract date from the row
        const row = badge.closest('tr');
        if (row) {
            const dateCell = row.cells[2].textContent.trim(); // "Date Engaged" cell (has icon text too)
            const dateStr = dateCell.trim();
            if(dateStr) {
                const appliedDate = new Date(dateStr);
                if (!isNaN(appliedDate.getTime())) {
                    const diffTime = Math.abs(today - appliedDate);
                    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
                    
                    if (diffDays === 0) badge.textContent = 'Today';
                    else if (diffDays === 1) badge.textContent = '1 day';
                    else badge.textContent = diffDays + ' days';
                    
                    // Add color coding based on wait time
                    if (diffDays > 14) badge.classList.add('text-danger');
                    else if (diffDays > 7) badge.classList.add('text-warning');
                } else {
                    badge.textContent = 'Unknown';
                }
            }
        }
    });
}

function updateStats() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            console.log('System telemetry connected.', data);
        })
        .catch(error => console.error('Comms error:', error));
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    updateStats();
    calculateDays();
    
    // Update last updated time
    const now = new Date();
    const timeStr = now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', second:'2-digit'});
    const lastUpdateEl = document.getElementById('lastUpdate');
    if (lastUpdateEl) {
        lastUpdateEl.textContent = timeStr;
    }
});
