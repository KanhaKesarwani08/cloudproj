document.addEventListener('DOMContentLoaded', function() {
    console.log("Budget Tracker App JS Loaded - Custom Auth Version");

    // REMOVED unused global variable `currentIdToken`
    // let currentIdToken = null;

    // Keep the first instance of UI Elements, Paths, and Helper Functions
    const TOKEN_KEY = 'budget_tracker_auth_token';

    // --- UI Elements ---
    const navLoginLink = document.getElementById('navLoginLink');
    const navRegisterLink = document.getElementById('navRegisterLink');
    const navDashboardLink = document.getElementById('navDashboardLink');
    const navLogoutLink = document.getElementById('navLogoutLink');
    const userInfoDisplay = document.getElementById('userInfo');

    // Login Page Elements
    const loginForm = document.getElementById('loginForm');
    const loginEmailInput = loginForm ? loginForm.querySelector('#email') : null;
    const loginPasswordInput = loginForm ? loginForm.querySelector('#password') : null;
    const loginAuthError = loginForm ? loginForm.querySelector('#authError') : null;
    const loginButton = loginForm ? loginForm.querySelector('#loginButton') : null;

    // Register Page Elements
    const registerForm = document.getElementById('registerForm');
    const regEmailInput = registerForm ? registerForm.querySelector('#email') : null;
    const regFullNameInput = registerForm ? registerForm.querySelector('#full_name') : null;
    const regPasswordInput = registerForm ? registerForm.querySelector('#password') : null;
    const regConfirmPasswordInput = registerForm ? registerForm.querySelector('#confirm_password') : null;
    const regAuthMessage = registerForm ? registerForm.querySelector('#authMessage') : null;

    // Dashboard Page Elements
    const expenseForm = document.getElementById('expenseForm');
    const expenseListUl = document.getElementById('expenseList');
    const noExpensesMessage = document.getElementById('noExpensesMessage');
    const expenseMessage = document.getElementById('expenseMessage');

    const dashboardPath = "/expenses/dashboard";
    const loginPath = "/auth/login";
    const registerPath = "/auth/register";
    const homePath = "/";

    // --- Helper Functions ---
    function storeToken(token) {
        localStorage.setItem(TOKEN_KEY, token);
    }

    function getToken() {
        return localStorage.getItem(TOKEN_KEY);
    }

    function removeToken() {
        localStorage.removeItem(TOKEN_KEY);
    }

    function showAuthMessage(element, message, isError = false) {
        if (element) {
            element.textContent = message;
            element.style.color = isError ? 'red' : 'green';
        }
    }

    async function fetchWithAuth(url, options = {}) {
        const token = getToken();
        const headers = {
            ...options.headers,
            'Content-Type': options.body instanceof URLSearchParams || options.body instanceof FormData ? undefined : 'application/json',
        };
        if (options.body instanceof URLSearchParams || options.body instanceof FormData) delete headers['Content-Type'];
        
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(url, { ...options, headers });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: `Request failed with status: ${response.status}` }));
            console.error("API Error:", errorData);
            let detail = "An error occurred.";
            if (errorData && errorData.detail) {
                if (typeof errorData.detail === 'string') {
                    detail = errorData.detail;
                } else if (Array.isArray(errorData.detail) && errorData.detail.length > 0 && errorData.detail[0].msg) {
                    detail = errorData.detail[0].msg; // Handle FastAPI validation errors
                }
            }
            throw new Error(detail);
        }
        // For 204 No Content, response.json() will fail. Handle it.
        if (response.status === 204) return null; 
        return response.json(); 
    }

    function updateNavUI(isLoggedIn, userEmail = null) {
        if (navLoginLink) navLoginLink.style.display = isLoggedIn ? 'none' : 'inline';
        if (navRegisterLink) navRegisterLink.style.display = isLoggedIn ? 'none' : 'inline';
        if (navDashboardLink) navDashboardLink.style.display = isLoggedIn ? 'inline' : 'none';
        if (navLogoutLink) navLogoutLink.style.display = isLoggedIn ? 'inline' : 'none';
        if (userInfoDisplay) {
            userInfoDisplay.textContent = isLoggedIn && userEmail ? `Logged in: ${userEmail}` : '';
            userInfoDisplay.style.display = isLoggedIn && userEmail ? 'inline' : 'none';
        }
    }

    async function checkLoginState() {
        const token = getToken();
        if (token) {
            try {
                // Verify token by fetching user profile
                console.log("Checking token validity...");
                const userData = await fetchWithAuth('/auth/users/me');
                if (userData && userData.email) {
                    console.log("Token valid, user:", userData.email);
                    updateNavUI(true, userData.email);
                    // Only redirect if on login/register page
                    if (window.location.pathname === loginPath || window.location.pathname === registerPath) {
                        console.log("Redirecting to dashboard...");
                        window.location.href = dashboardPath;
                    }
                    // If on dashboard, fetch expenses
                    if (window.location.pathname.startsWith(dashboardPath)){
                        fetchAndDisplayExpenses();
                    }
                } else {
                    // This case might occur if /users/me doesn't return expected data
                    console.warn("Token verified but user data incomplete:", userData);
                    throw new Error("Invalid user data received from /users/me");
                }
            } catch (error) {
                console.warn("Session invalid or expired, clearing token:", error.message);
                removeToken();
                updateNavUI(false);
                if (window.location.pathname.startsWith(dashboardPath)) {
                    console.log("User not authenticated on dashboard, redirecting to login.");
                    window.location.href = loginPath; 
                }
            }
        } else {
            console.log("No token found.");
            updateNavUI(false);
            if (window.location.pathname.startsWith(dashboardPath)) {
                console.log("User not authenticated on dashboard, redirecting to login.");
                window.location.href = loginPath;
            }
        }
    }

    // --- Event Handlers ---
    if (loginButton) {
        console.log("Attaching click listener to login button...");
        loginButton.addEventListener('click', async (event) => {
            console.log("Login button CLICKED!");
            // event.preventDefault(); // Not needed for type="button"
            showAuthMessage(loginAuthError, '');
            
            const email = loginEmailInput ? loginEmailInput.value : null;
            const password = loginPasswordInput ? loginPasswordInput.value : null;

            if (!email || !password) {
                 showAuthMessage(loginAuthError, "Email and password are required.", true);
                 return;
            }

            // FastAPI's OAuth2PasswordRequestForm expects x-www-form-urlencoded
            const formData = new URLSearchParams();
            formData.append('username', email);
            formData.append('password', password);

            try {
                console.log("Attempting login fetch...");
                const data = await fetchWithAuth('/auth/token', {
                    method: 'POST',
                    body: formData
                });
                console.log("Login fetch successful, received token.");
                storeToken(data.access_token);
                await checkLoginState();
            } catch (error) {
                console.error("Login fetch failed:", error);
                showAuthMessage(loginAuthError, error.message, true);
            }
        });
        console.log("Click listener ATTACHED to login button.");
    } else {
        console.log("Login button not found, listener not attached.");
    }

    if (registerForm) {
        registerForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            showAuthMessage(regAuthMessage, '');
            const email = regEmailInput.value;
            const fullName = regFullNameInput.value;
            const password = regPasswordInput.value;
            const confirmPassword = regConfirmPasswordInput.value;

            if (password !== confirmPassword) {
                showAuthMessage(regAuthMessage, "Passwords do not match.", true);
                return;
            }

            try {
                console.log("Attempting registration...");
                await fetchWithAuth('/auth/register', {
                    method: 'POST',
                    body: JSON.stringify({ email, full_name: fullName, password })
                });
                console.log("Registration successful.");
                showAuthMessage(regAuthMessage, "Registration successful! Redirecting to login...", false);
                setTimeout(() => { window.location.href = loginPath; }, 2000);
            } catch (error) {
                console.error("Registration failed:", error);
                showAuthMessage(regAuthMessage, error.message, true);
            }
        });
    }

    if (navLogoutLink) {
        navLogoutLink.addEventListener('click', (event) => {
            event.preventDefault();
            console.log("Logging out...");
            removeToken();
            updateNavUI(false);
            window.location.href = homePath;
        });
    }

    async function fetchAndDisplayExpenses() {
        if (!expenseListUl || !noExpensesMessage) return;
        console.log("Fetching expenses...");
        try {
            const expenses = await fetchWithAuth('/expenses/'); // GET request to our API
            expenseListUl.innerHTML = ''; 
            if (expenses && expenses.length > 0) {
                console.log("Expenses received:", expenses);
                noExpensesMessage.style.display = 'none';
                expenses.forEach(exp => {
                    const li = document.createElement('li');
                    li.textContent = `${exp.expense_date}: ${exp.description} - $${exp.amount.toFixed(2)} (${exp.category})`;
                    expenseListUl.appendChild(li);
                });
                renderCharts(expenses);
            } else {
                console.log("No expenses found for user.");
                noExpensesMessage.style.display = 'block';
                document.getElementById('categoryChart').style.display = 'none';
                document.getElementById('monthlyChart').style.display = 'none';
            }
        } catch (error) {
            console.error("Failed to fetch expenses:", error);
            if (expenseListUl) expenseListUl.innerHTML = `<li>Error loading expenses: ${error.message}</li>`;
            noExpensesMessage.style.display = 'none';
            document.getElementById('categoryChart').style.display = 'none';
            document.getElementById('monthlyChart').style.display = 'none';
        }
    }

    let categoryChart = null;
    let monthlyChart = null;

    function renderCharts(expenses) {
        renderCategoryChart(expenses);
        renderMonthlyChart(expenses);
        document.getElementById('categoryChart').style.display = 'block';
        document.getElementById('monthlyChart').style.display = 'block';
    }

    function renderCategoryChart(expenses) {
        const canvas = document.getElementById('pieChart');
        if (!canvas) {
            console.error("Category chart canvas element not found!");
            return;
        }

        // Destroy existing chart if it exists
        const existingChart = Chart.getChart(canvas);
        if (existingChart) {
            existingChart.destroy();
        }

        // Aggregate expenses by category
        const expensesByCategory = expenses.reduce((acc, expense) => {
            acc[expense.category] = (acc[expense.category] || 0) + expense.amount;
            return acc;
        }, {});

        const labels = Object.keys(expensesByCategory);
        const data = Object.values(expensesByCategory);

        // Generate colors for each category
        const colors = generateColors(labels.length);

        categoryChart = new Chart(canvas, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: colors.background,
                    borderColor: colors.border,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: $${value.toFixed(2)} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    function renderMonthlyChart(expenses) {
        const canvas = document.getElementById('lineChart');
        if (!canvas) {
            console.error("Monthly chart canvas element not found!");
            return;
        }

        // Destroy existing chart if it exists
        const existingChart = Chart.getChart(canvas);
        if (existingChart) {
            existingChart.destroy();
        }

        // Aggregate expenses by month
        const expensesByMonth = expenses.reduce((acc, expense) => {
            const date = new Date(expense.expense_date);
            const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
            acc[monthKey] = (acc[monthKey] || 0) + expense.amount;
            return acc;
        }, {});

        // Sort months chronologically
        const sortedMonths = Object.keys(expensesByMonth).sort();
        const monthlyData = sortedMonths.map(month => expensesByMonth[month]);

        monthlyChart = new Chart(canvas, {
            type: 'line',
            data: {
                labels: sortedMonths.map(month => {
                    const [year, monthNum] = month.split('-');
                    const date = new Date(year, parseInt(monthNum) - 1);
                    return date.toLocaleString('default', { month: 'short', year: 'numeric' });
                }),
                datasets: [{
                    label: 'Monthly Expenses',
                    data: monthlyData,
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const value = context.raw || 0;
                                return `Total: $${value.toFixed(2)}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toFixed(0);
                            }
                        }
                    }
                }
            }
        });
    }

    function generateColors(count) {
        const colors = [
            { bg: 'rgba(37, 99, 235, 0.2)', border: 'rgb(37, 99, 235)' },
            { bg: 'rgba(236, 72, 153, 0.2)', border: 'rgb(236, 72, 153)' },
            { bg: 'rgba(34, 197, 94, 0.2)', border: 'rgb(34, 197, 94)' },
            { bg: 'rgba(234, 179, 8, 0.2)', border: 'rgb(234, 179, 8)' },
            { bg: 'rgba(168, 85, 247, 0.2)', border: 'rgb(168, 85, 247)' },
            { bg: 'rgba(239, 68, 68, 0.2)', border: 'rgb(239, 68, 68)' },
            { bg: 'rgba(20, 184, 166, 0.2)', border: 'rgb(20, 184, 166)' },
            { bg: 'rgba(245, 158, 11, 0.2)', border: 'rgb(245, 158, 11)' }
        ];

        // If we need more colors than we have predefined, generate them
        while (colors.length < count) {
            const hue = (colors.length * 137.508) % 360; // Use golden angle approximation
            colors.push({
                bg: `hsla(${hue}, 70%, 60%, 0.2)`,
                border: `hsl(${hue}, 70%, 60%)`
            });
        }

        return {
            background: colors.slice(0, count).map(c => c.bg),
            border: colors.slice(0, count).map(c => c.border)
        };
    }

    if (expenseForm) {
        expenseForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            showAuthMessage(expenseMessage, ''); 
            const description = document.getElementById('description').value;
            const amount = parseFloat(document.getElementById('amount').value);
            const category = document.getElementById('category').value;
            const expense_date = document.getElementById('expense_date').value;

            if (!description || isNaN(amount) || !category) {
                showAuthMessage(expenseMessage, "Please fill in description, amount, and category.", true);
                return;
            }

            const formData = new FormData();
            formData.append('description', description);
            formData.append('amount', amount.toString());
            formData.append('category', category);
            if (expense_date) formData.append('expense_date_str', expense_date);

            try {
                console.log("Submitting new expense...");
                // The backend /expenses/add endpoint expects form data and redirects.
                // We need to handle this without JS trying to parse a JSON response from a redirect.
                const response = await fetch('/expenses/add', { // Not using fetchWithAuth to handle redirect manually
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${getToken()}`,
                    },
                    body: formData,
                    redirect: 'manual' // Important to handle redirect from server
                });

                if (response.type === 'opaqueredirect' || (response.status >= 300 && response.status < 400)) {
                    // Successful form submission leading to a redirect
                    console.log("Expense added, backend redirecting...");
                    window.location.href = dashboardPath; // Go to dashboard to see change
                } else if (response.ok) {
                     // This case might occur if the server doesn't redirect but returns 200/201 with JSON
                    console.log("Expense added (no redirect from backend).");
                    showAuthMessage(expenseMessage, "Expense added! Refreshing list...", false);
                    fetchAndDisplayExpenses(); 
                    expenseForm.reset();
                } else {
                    // Handle actual error responses
                    const errorData = await response.json().catch(() => ({ detail: 'Failed to add expense.' }));
                    console.error("Error adding expense (response not ok):", errorData);
                    showAuthMessage(expenseMessage, errorData.detail, true);
                }
            } catch (error) {
                console.error("Failed to add expense (fetch error):", error);
                showAuthMessage(expenseMessage, error.message || "Error adding expense.", true);
            }
        });
    }

    // --- Initial Page Load Logic ---
    console.log("Initial check of login state...");
    checkLoginState();

}); 