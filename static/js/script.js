// Main JavaScript file for Food Distribution System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-warning)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Fingerprint scanner simulation
    function setupFingerprintScanner() {
        const scanButton = document.getElementById('scan_fingerprint');
        if (!scanButton) return;
        
        scanButton.addEventListener('click', function() {
            this.classList.add('scanning');
            this.disabled = true;
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Scanning...';
            
            // Simulate fingerprint scanning (in a real app, this would interface with actual hardware)
            setTimeout(() => {
                // Generate a random fingerprint ID
                const fingerprintId = 'FP' + Math.floor(Math.random() * 1000000).toString().padStart(6, '0');
                const fingerprintInput = document.getElementById('fingerprint_id');
                
                if (fingerprintInput) {
                    fingerprintInput.value = fingerprintId;
                    
                    // If we're on the identification form, submit it automatically
                    const form = document.getElementById('identification-form');
                    if (form) {
                        // Show a message before submitting
                        const alertDiv = document.createElement('div');
                        alertDiv.className = 'alert alert-info mt-2';
                        alertDiv.textContent = 'Fingerprint scanned. Verifying...';
                        this.parentNode.parentNode.appendChild(alertDiv);
                        
                        // Submit the form after a short delay
                        setTimeout(() => {
                            form.submit();
                        }, 1500);
                    } else {
                        // Show success message
                        const alertDiv = document.createElement('div');
                        alertDiv.className = 'alert alert-success mt-2';
                        alertDiv.textContent = 'Fingerprint scanned successfully!';
                        this.parentNode.parentNode.appendChild(alertDiv);
                        
                        // Remove the alert after 3 seconds
                        setTimeout(() => {
                            alertDiv.remove();
                        }, 3000);
                    }
                }
                
                // Reset the button
                this.classList.remove('scanning');
                this.disabled = false;
                this.innerHTML = 'Scan Fingerprint';
            }, 2000);
        });
    }
    
    // Setup fingerprint scanner functionality
    setupFingerprintScanner();
    
    // Date of birth validation
    const dobInput = document.getElementById('date_of_birth');
    if (dobInput) {
        dobInput.addEventListener('change', function() {
            const selectedDate = new Date(this.value);
            const today = new Date();
            
            if (selectedDate > today) {
                this.setCustomValidity('Date of birth cannot be in the future');
                this.reportValidity();
            } else {
                this.setCustomValidity('');
            }
        });
    }
    
    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // Add current year to footer
    const yearElement = document.querySelector('.footer .text-muted');
    if (yearElement) {
        const currentYear = new Date().getFullYear();
        yearElement.textContent = yearElement.textContent.replace('{{ now.year }}', currentYear);
    }
});
