// Main JavaScript for Connect+

document.addEventListener('DOMContentLoaded', function() {
    // Enable tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Enable popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Auto-focus on search inputs
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.focus();
    }
    
    // Handle friend request buttons
    const friendButtons = document.querySelectorAll('.friend-action-btn');
    friendButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Show loading spinner
            const originalText = this.innerHTML;
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
            this.disabled = true;
            
            // Allow form submission to continue
            setTimeout(() => {
                this.closest('form').submit();
            }, 100);
        });
    });
    
    // Message textarea auto-resize
    const messageInput = document.querySelector('#message-input');
    if (messageInput) {
        messageInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
        
        // Focus on message input when page loads
        messageInput.focus();
    }
    
    // Scroll to bottom of message container
    const messageContainer = document.querySelector('.message-container');
    if (messageContainer) {
        messageContainer.scrollTop = messageContainer.scrollHeight;
    }
    
    // Confirmation dialogs
    const confirmActions = document.querySelectorAll('[data-confirm]');
    confirmActions.forEach(action => {
        action.addEventListener('click', function(e) {
            if (!confirm(this.dataset.confirm)) {
                e.preventDefault();
            }
        });
    });
    
    // Registration steps indicator
    const registrationStep = document.querySelector('#registration-step');
    if (registrationStep) {
        const step = parseInt(registrationStep.value);
        const steps = document.querySelectorAll('.step');
        
        for (let i = 0; i < steps.length; i++) {
            if (i < step - 1) {
                steps[i].classList.add('completed');
            } else if (i === step - 1) {
                steps[i].classList.add('active');
            }
        }
    }
}); 