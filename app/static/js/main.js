/* =====================================================
   INTERVIEW PREP TRACKER - MAIN JAVASCRIPT
   ===================================================== */

// =====================================================
// 1. DOM READY
// =====================================================
document.addEventListener('DOMContentLoaded', function() {
    initNavbar();
    initAnimations();
    initTooltips();
    initAutoHideAlerts();
    initFormValidation();
    initSmoothScroll();
});

// =====================================================
// 2. NAVBAR FUNCTIONS
// =====================================================
function initNavbar() {
    const navbar = document.querySelector('.navbar');
    
    if (navbar) {
        // Navbar scroll effect
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
                navbar.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.1)';
            } else {
                navbar.classList.remove('scrolled');
                navbar.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.1)';
            }
        });
    }
}

// =====================================================
// 3. ANIMATION FUNCTIONS
// =====================================================
function initAnimations() {
    // Intersection Observer for scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate__animated', 'animate__fadeInUp');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe elements with animate-on-scroll class
    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        observer.observe(el);
    });
    
    // Feature cards stagger animation
    document.querySelectorAll('.feature-card').forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
    });
    
    // Step cards stagger animation
    document.querySelectorAll('.step-card').forEach((card, index) => {
        card.style.animationDelay = `${index * 0.15}s`;
    });
}

// =====================================================
// 4. TOOLTIP INITIALIZATION
// =====================================================
function initTooltips() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// =====================================================
// 5. ALERT AUTO-HIDE
// =====================================================
function initAutoHideAlerts() {
    const alerts = document.querySelectorAll('.flash-messages .alert');
    
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.add('animate__fadeOutUp');
            setTimeout(() => {
                alert.remove();
            }, 500);
        }, 5000);
    });
}

// =====================================================
// 6. FORM VALIDATION
// =====================================================
function initFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // Password strength indicator
    const passwordInputs = document.querySelectorAll('input[type="password"][id="password"]');
    passwordInputs.forEach(input => {
        input.addEventListener('input', function() {
            updatePasswordStrength(this.value);
        });
    });
    
    // Password confirmation matching
    const confirmPasswordInputs = document.querySelectorAll('input[id="confirm_password"]');
    confirmPasswordInputs.forEach(input => {
        input.addEventListener('input', function() {
            const password = document.getElementById('password').value;
            if (this.value !== password) {
                this.setCustomValidity('Passwords do not match');
            } else {
                this.setCustomValidity('');
            }
        });
    });
}

// Password strength calculator
function updatePasswordStrength(password) {
    let strength = 0;
    
    if (password.length >= 8) strength++;
    if (password.match(/[a-z]/)) strength++;
    if (password.match(/[A-Z]/)) strength++;
    if (password.match(/[0-9]/)) strength++;
    if (password.match(/[^a-zA-Z0-9]/)) strength++;
    
    const strengthIndicator = document.querySelector('.password-strength');
    if (strengthIndicator) {
        strengthIndicator.className = 'password-strength';
        if (strength <= 2) {
            strengthIndicator.classList.add('weak');
            strengthIndicator.textContent = 'Weak';
        } else if (strength <= 3) {
            strengthIndicator.classList.add('medium');
            strengthIndicator.textContent = 'Medium';
        } else {
            strengthIndicator.classList.add('strong');
            strengthIndicator.textContent = 'Strong';
        }
    }
}

// =====================================================
// 7. PASSWORD TOGGLE
// =====================================================
function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const icon = input.parentElement.querySelector('.password-toggle i');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('bi-eye');
        icon.classList.add('bi-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('bi-eye-slash');
        icon.classList.add('bi-eye');
    }
}

// =====================================================
// 8. SMOOTH SCROLL
// =====================================================
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
}

// =====================================================
// 9. CHART UTILITIES
// =====================================================
function createLineChart(canvasId, data, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: {
                display: false
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                max: 100,
                grid: {
                    color: 'rgba(0, 0, 0, 0.05)'
                }
            },
            x: {
                grid: {
                    display: false
                }
            }
        }
    };
    
    return new Chart(ctx, {
        type: 'line',
        data: data,
        options: { ...defaultOptions, ...options }
    });
}

function createRadarChart(canvasId, data, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: true,
        scales: {
            r: {
                beginAtZero: true,
                max: 100,
                ticks: {
                    stepSize: 20
                }
            }
        }
    };
    
    return new Chart(ctx, {
        type: 'radar',
        data: data,
        options: { ...defaultOptions, ...options }
    });
}

function createBarChart(canvasId, data, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: {
                display: false
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                max: 100,
                grid: {
                    color: 'rgba(0, 0, 0, 0.05)'
                }
            },
            x: {
                grid: {
                    display: false
                }
            }
        }
    };
    
    return new Chart(ctx, {
        type: 'bar',
        data: data,
        options: { ...defaultOptions, ...options }
    });
}

// =====================================================
// 10. UTILITY FUNCTIONS
// =====================================================

// Format date
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

// Format time
function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

// Format file size
function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Throttle function
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Copy to clipboard
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showToast('Copied to clipboard!', 'success');
    } catch (err) {
        showToast('Failed to copy', 'error');
    }
}

// Show toast notification
function showToast(message, type = 'info') {
    const toastContainer = document.querySelector('.toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    document.body.appendChild(container);
    return container;
}

// =====================================================
// 11. API UTILITIES
// =====================================================
async function fetchAPI(endpoint, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    try {
        const response = await fetch(endpoint, { ...defaultOptions, ...options });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// =====================================================
// 12. LOCAL STORAGE UTILITIES
// =====================================================
const storage = {
    set: function(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.error('LocalStorage Error:', e);
        }
    },
    
    get: function(key) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : null;
        } catch (e) {
            console.error('LocalStorage Error:', e);
            return null;
        }
    },
    
    remove: function(key) {
        try {
            localStorage.removeItem(key);
        } catch (e) {
            console.error('LocalStorage Error:', e);
        }
    },
    
    clear: function() {
        try {
            localStorage.clear();
        } catch (e) {
            console.error('LocalStorage Error:', e);
        }
    }
};

// =====================================================
// 13. LOADING STATES
// =====================================================
function showLoading(element) {
    element.classList.add('loading');
    element.disabled = true;
    const originalContent = element.innerHTML;
    element.setAttribute('data-original-content', originalContent);
    element.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
}

function hideLoading(element) {
    element.classList.remove('loading');
    element.disabled = false;
    const originalContent = element.getAttribute('data-original-content');
    if (originalContent) {
        element.innerHTML = originalContent;
    }
}

// =====================================================
// 14. CONFIRMATION DIALOGS
// =====================================================
function confirmAction(message, callback) {
    const modal = new bootstrap.Modal(document.getElementById('confirmModal') || createConfirmModal());
    document.querySelector('#confirmModal .modal-body p').textContent = message;
    document.querySelector('#confirmModal .btn-confirm').onclick = function() {
        callback();
        modal.hide();
    };
    modal.show();
}

function createConfirmModal() {
    const modalHtml = `
        <div class="modal fade" id="confirmModal" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-body text-center p-4">
                        <i class="bi bi-question-circle text-warning" style="font-size: 3rem;"></i>
                        <p class="mt-3 mb-0"></p>
                    </div>
                    <div class="modal-footer justify-content-center border-0">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary btn-confirm">Confirm</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    return document.getElementById('confirmModal');
}

// =====================================================
// 15. EXPORT FUNCTIONS
// =====================================================
window.InterviewPrep = {
    togglePassword,
    formatDate,
    formatTime,
    formatFileSize,
    showToast,
    fetchAPI,
    storage,
    showLoading,
    hideLoading,
    confirmAction,
    createLineChart,
    createRadarChart,
    createBarChart
};