 // Main JavaScript for MTJ Bank

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

  

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Add animation to cards on scroll
    const cards = document.querySelectorAll('.card');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, {
        threshold: 0.1
    });

    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'all 0.5s ease-out';
        observer.observe(card);
    });

    // Handle mobile menu
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        document.addEventListener('click', function(e) {
            if (!navbarCollapse.contains(e.target) && !navbarToggler.contains(e.target)) {
                if (navbarCollapse.classList.contains('show')) {
                    navbarToggler.click();
                }
            }
        });
    }

    // Initialize password toggle for login page
    const loginPasswordToggle = document.querySelector('.login-password-toggle');
    const loginPasswordInput = document.getElementById('password');
    
    if (loginPasswordToggle && loginPasswordInput) {
        loginPasswordToggle.addEventListener('click', function() {
            const icon = this.querySelector('i');
            const passwordInput = loginPasswordInput;
            
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                passwordInput.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    }

    // Initialize password toggle for register page
    const registerPasswordToggle = document.querySelector('.register-password-toggle');
    const registerPasswordInput = document.getElementById('register-password');
    
    if (registerPasswordToggle && registerPasswordInput) {
        registerPasswordToggle.addEventListener('click', function() {
            const icon = this.querySelector('i');
            const passwordInput = registerPasswordInput;
            
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                passwordInput.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    }

    // Initialize password toggle for confirm password in register page
    const confirmPasswordToggle = document.querySelector('.confirm-password-toggle');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    
    if (confirmPasswordToggle && confirmPasswordInput) {
        confirmPasswordToggle.addEventListener('click', function() {
            const icon = this.querySelector('i');
            const passwordInput = confirmPasswordInput;
            
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                passwordInput.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    }

    // Password validation
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

    const passwordInput = document.getElementById('password');
    const passwordRequirements = document.querySelector('.password-requirements');
    
    if (passwordInput && passwordRequirements) {
        passwordInput.addEventListener('input', function() {
            const isValid = validatePassword(this.value);
            passwordRequirements.style.display = this.value.length > 0 ? 'block' : 'none';
            
            // Show password strength indicator
            const strengthIndicator = document.querySelector('.password-strength');
            if (strengthIndicator) {
                const strength = calculatePasswordStrength(this.value);
                strengthIndicator.style.width = `${strength}%`;
                strengthIndicator.className = `password-strength strength-${getStrengthClass(strength)}`;
            }
        });
    }

    // Password visibility toggle
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
});

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
    if (strength >= 80) return 'strong';
    if (strength >= 40) return 'medium';
    return 'weak';
}