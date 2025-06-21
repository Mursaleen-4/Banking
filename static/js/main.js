// Main JavaScript for Secure Bank

document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // Password requirements validation (for register page)
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    const passwordRequirements = document.querySelector('.password-requirements');
    const passwordRequirementsList = document.querySelector('.password-requirements-list');
    const passwordStrengthBar = document.querySelector('.password-strength-bar');
    const passwordStrength = document.querySelector('.password-strength');

    if (passwordInput && passwordRequirements) {
        passwordInput.addEventListener('input', function() {
            const password = this.value;
            validatePassword(password);
            passwordRequirements.style.display = password.length > 0 ? 'block' : 'none';
            if (passwordStrength) {
                const strength = calculatePasswordStrength(password);
                passwordStrength.style.width = `${strength}%`;
                passwordStrength.className = `password-strength ${getStrengthClass(strength)}`;
            }
        });
    }
    if (passwordInput && confirmPasswordInput) {
        function validatePasswordsMatch() {
            if (passwordInput.value !== confirmPasswordInput.value) {
                confirmPasswordInput.setCustomValidity('Passwords do not match');
            } else {
                confirmPasswordInput.setCustomValidity('');
            }
        }
        passwordInput.addEventListener('input', validatePasswordsMatch);
        confirmPasswordInput.addEventListener('input', validatePasswordsMatch);
    }

    // Dashboard Recent Transactions Filtering
    const transactionFilter = document.querySelector('.transaction-card .filters select');
    if (transactionFilter) {
        transactionFilter.addEventListener('change', function() {
            const selected = this.value;
            document.querySelectorAll('.transaction-list .transaction-item').forEach(item => {
                const type = item.getAttribute('data-type');
                if (selected === 'all' ||
                    (selected === 'deposit' && (type === 'deposit' || type === 'transfer_received')) ||
                    (selected === 'withdraw' && type === 'withdraw') ||
                    (selected === 'transfer' && (type === 'transfer_sent' || type === 'transfer_received'))
                ) {
                    item.style.display = '';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    }

    // Dashboard Load More Transactions
    const loadMoreBtn = document.getElementById('loadMoreTransactions');
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', function() {
            const loaded = parseInt(this.getAttribute('data-loaded'));
            const lastDocId = this.getAttribute('data-last-doc-id');
            fetch(`/load_more_transactions?last_doc_id=${lastDocId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.transactions && data.transactions.length > 0) {
                        const list = document.querySelector('.transaction-list');
                        data.transactions.forEach(txn => {
                            const div = document.createElement('div');
                            div.className = 'transaction-item';
                            div.setAttribute('data-type', txn.type);
                            div.setAttribute('data-timestamp', txn.timestamp);
                            div.innerHTML = `
                                <div class="transaction-icon">
                                    <div class="transaction-type ${['deposit','transfer_received'].includes(txn.type) ? 'success' : 'danger'}">
                                        <i class="fas ${['deposit','transfer_received'].includes(txn.type) ? 'fa-arrow-up' : 'fa-arrow-down'}"></i>
                                    </div>
                                </div>
                                <div class="transaction-details">
                                    <div class="transaction-info">
                                        <h6 class="mb-1">${txn.description}</h6>
                                        <small class="text-muted">${txn.timestamp_str}</small>
                                    </div>
                                    <div class="transaction-status">
                                        <span class="badge ${txn.status === 'completed' ? 'bg-success' : (txn.status === 'pending' ? 'bg-warning' : 'bg-danger')}">
                                            ${txn.status.charAt(0).toUpperCase() + txn.status.slice(1)}
                                        </span>
                                    </div>
                                </div>
                                <div class="transaction-amount">
                                    <div class="amount-container">
                                        <span class="currency">$</span>
                                        <span class="amount ${['deposit','transfer_received'].includes(txn.type) ? 'text-success' : 'text-danger'}">
                                            ${parseFloat(txn.amount).toFixed(2)}
                                        </span>
                                    </div>
                                    <div class="transaction-category">
                                        <span class="badge bg-secondary">${txn.category}</span>
                                    </div>
                                </div>
                            `;
                            list.appendChild(div);
                        });
                        loadMoreBtn.setAttribute('data-loaded', loaded + data.transactions.length);
                        if (data.last_doc_id) {
                            loadMoreBtn.setAttribute('data-last-doc-id', data.last_doc_id);
                        }
                        if (!data.has_more) {
                            loadMoreBtn.style.display = 'none';
                        }
                    } else {
                        loadMoreBtn.style.display = 'none';
                    }
                });
        });
    }
});

// Global function for password toggle (works for any page)
function togglePassword(inputId, button) {
    const passwordInput = document.getElementById(inputId);
    const icon = button.querySelector('i');
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        passwordInput.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

// Optional password validation logic (used in register page)
function validatePassword(password) {
    const requirements = [
        { regex: /^.{8,}$/, text: 'At least 8 characters', valid: false },
        { regex: /[A-Z]/, text: 'One uppercase letter', valid: false },
        { regex: /[a-z]/, text: 'One lowercase letter', valid: false },
        { regex: /[0-9]/, text: 'One number', valid: false },
        { regex: /[!@#$%^&*]/, text: 'One special character (!@#$%^&*)', valid: false }
    ];

    requirements.forEach(req => {
        req.valid = req.regex.test(password);
        const requirementElement = document.querySelector(`[data-requirement="${req.text}"]`);
        if (requirementElement) {
            requirementElement.classList.toggle('valid', req.valid);
            requirementElement.classList.toggle('invalid', !req.valid);
        }
    });

    return requirements.every(req => req.valid);
}

function calculatePasswordStrength(password) {
    const requirements = [
        { regex: /^.{8,}$/, points: 20 },
        { regex: /[A-Z]/, points: 20 },
        { regex: /[a-z]/, points: 20 },
        { regex: /[0-9]/, points: 20 },
        { regex: /[!@#$%^&*]/, points: 20 }
    ];
    
    let strength = 0;
    requirements.forEach(req => {
        if (req.regex.test(password)) strength += req.points;
    });
    
    return strength;
}

function getStrengthClass(strength) {
    if (strength >= 80) return 'strength-strong';
    if (strength >= 40) return 'strength-medium';
    return 'strength-weak';
}
