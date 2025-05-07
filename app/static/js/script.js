// Placeholder for JavaScript functionality

// 0. Firebase Configuration (REPLACE with your actual config!)
const firebaseConfig = {
    apiKey: "YOUR_API_KEY",
    authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
    projectId: "YOUR_PROJECT_ID",
    storageBucket: "YOUR_PROJECT_ID.appspot.com",
    messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
    appId: "YOUR_APP_ID"
    // measurementId: "YOUR_MEASUREMENT_ID" // Optional
};

// 1. Initialize Firebase
if (typeof firebase !== 'undefined') {
    firebase.initializeApp(firebaseConfig);
    const auth = firebase.auth();
    console.log("Firebase Initialized");

    // Global state
    let currentIdToken = null;

    // UI Elements
    const navLoginLink = document.getElementById('navLoginLink');
    const navDashboardLink = document.getElementById('navDashboardLink');
    const navLogoutLink = document.getElementById('navLogoutLink');
    const userInfoDisplay = document.getElementById('userInfo');

    const loginSection = document.getElementById('loginSection');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const loginButton = document.getElementById('loginButton');
    const registerButton = document.getElementById('registerButton');
    const authErrorDisplay = document.getElementById('authError');
    const postLoginMessage = document.getElementById('postLoginMessage');

    const expenseForm = document.getElementById('expenseForm');
    const expenseListUl = document.getElementById('expenseList');
    const noExpensesMessage = document.getElementById('noExpensesMessage');
    const expenseMessage = document.getElementById('expenseMessage');
    
    const dashboardPath = "/expenses/dashboard"; // As defined in expenses router
    const loginPath = "/auth/login"; // As defined in auth router

    // --- Helper Functions ---
    function showAuthError(message) {
        if (authErrorDisplay) authErrorDisplay.textContent = message;
    }

    function clearAuthError() {
        if (authErrorDisplay) authErrorDisplay.textContent = '';
    }

    function showExpenseMessage(message, isError = false) {
        if (expenseMessage) {
            expenseMessage.textContent = message;
            expenseMessage.style.color = isError ? 'red' : 'green';
            setTimeout(() => { expenseMessage.textContent = ''; }, 3000);
        }
    }

    async function fetchWithAuth(url, options = {}) {
        if (!currentIdToken) {
            console.error("No ID token available for authenticated request.");
            // Potentially redirect to login or show error
            // window.location.href = loginPath;
            throw new Error("User not authenticated.");
        }
        const headers = {
            ...options.headers,
            'Authorization': `Bearer ${currentIdToken}`,
            'Content-Type': options.body instanceof FormData ? undefined : 'application/json' // Let browser set for FormData
        };
        if (options.body instanceof FormData) delete headers['Content-Type'];

        const response = await fetch(url, { ...options, headers });
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: response.statusText }));
            console.error("API Error:", errorData);
            throw new Error(errorData.detail || "API request failed");
        }
        return response.json().catch(() => ({})); // Return empty object if no JSON body (e.g. 204)
    }

    // --- Authentication State Listener ---
    auth.onAuthStateChanged(async (user) => {
        if (user) {
            // User is signed in.
            console.log("User signed in:", user.email);
            try {
                currentIdToken = await user.getIdToken();
                console.log("Firebase ID Token obtained.");

                // Sync with backend
                try {
                    const backendAuthResponse = await fetchWithAuth('/auth/token', { method: 'POST' });
                    console.log("Backend sync successful:", backendAuthResponse);
                    if(userInfoDisplay) {
                        userInfoDisplay.textContent = `Logged in as: ${backendAuthResponse.email || user.email}`;
                        userInfoDisplay.style.display = 'inline';
                    }
                } catch (err) {
                    console.error("Backend sync failed:", err);
                    showAuthError("Failed to sync with backend. Please try logging out and in.");
                    // Potentially log out user if backend sync is critical
                    // auth.signOut(); 
                    // return;
                }

                // Update UI for logged-in state
                if (navLoginLink) navLoginLink.style.display = 'none';
                if (navDashboardLink) navDashboardLink.style.display = 'inline';
                if (navLogoutLink) navLogoutLink.style.display = 'inline';
                if (loginSection && window.location.pathname.includes('login')) {
                    loginSection.style.display = 'none';
                    if(postLoginMessage) postLoginMessage.style.display = 'block';
                    setTimeout(() => { window.location.href = dashboardPath; }, 1500);
                } else if (window.location.pathname.startsWith(dashboardPath)) {
                    fetchAndDisplayExpenses();
                }

            } catch (error) {
                console.error("Error getting ID token:", error);
                currentIdToken = null;
                // Handle error, maybe sign out user
            }
        } else {
            // User is signed out.
            console.log("User signed out.");
            currentIdToken = null;
            if (navLoginLink) navLoginLink.style.display = 'inline';
            if (navDashboardLink) navDashboardLink.style.display = 'none';
            if (navLogoutLink) navLogoutLink.style.display = 'none';
            if (userInfoDisplay) userInfoDisplay.style.display = 'none';
            
            if (window.location.pathname.startsWith(dashboardPath)) {
                 // If on dashboard and logs out, redirect to login
                window.location.href = loginPath;
            }
            if (loginSection) loginSection.style.display = 'block';
            if (postLoginMessage) postLoginMessage.style.display = 'none';
            if (expenseListUl) expenseListUl.innerHTML = ''; // Clear expenses
            if (noExpensesMessage) noExpensesMessage.style.display = 'block';
        }
    });

    // --- Auth Event Handlers (Login Page) ---
    if (loginButton) {
        loginButton.addEventListener('click', async () => {
            clearAuthError();
            const email = emailInput.value;
            const password = passwordInput.value;
            if (!email || !password) {
                showAuthError("Please enter email and password.");
                return;
            }
            try {
                console.log(`Attempting login for ${email}`);
                await auth.signInWithEmailAndPassword(email, password);
                // onAuthStateChanged will handle UI update and redirect
            } catch (error) {
                console.error("Login error:", error);
                showAuthError(error.message);
            }
        });
    }

    if (registerButton) {
        registerButton.addEventListener('click', async () => {
            clearAuthError();
            const email = emailInput.value;
            const password = passwordInput.value;
            if (!email || !password) {
                showAuthError("Please enter email and password for registration.");
                return;
            }
            try {
                console.log(`Attempting registration for ${email}`);
                await auth.createUserWithEmailAndPassword(email, password);
                // onAuthStateChanged will handle UI update. 
                // Backend sync happens on login after registration.
                showAuthError("Registration successful! Please login."); // Or auto-login
            } catch (error) {
                console.error("Registration error:", error);
                showAuthError(error.message);
            }
        });
    }

    // --- Logout Event Handler (Navbar) ---
    if (navLogoutLink) {
        navLogoutLink.addEventListener('click', async (event) => {
            event.preventDefault();
            try {
                await auth.signOut();
                // onAuthStateChanged will handle redirect and UI cleanup
                window.location.href = '/'; // Redirect to home on logout
            } catch (error) {
                console.error("Logout error:", error);
            }
        });
    }

    // --- Expense Management (Dashboard Page) ---
    async function fetchAndDisplayExpenses() {
        if (!expenseListUl || !noExpensesMessage) return;
        try {
            const expenses = await fetchWithAuth('/expenses/'); // GET request to API
            expenseListUl.innerHTML = ''; // Clear existing
            if (expenses && expenses.length > 0) {
                noExpensesMessage.style.display = 'none';
                expenses.forEach(exp => {
                    const li = document.createElement('li');
                    li.textContent = `${exp.expense_date}: ${exp.description} - $${exp.amount.toFixed(2)} (${exp.category})`;
                    // Add edit/delete buttons here if needed
                    expenseListUl.appendChild(li);
                });
            } else {
                noExpensesMessage.style.display = 'block';
            }
        } catch (error) {
            console.error("Failed to fetch expenses:", error);
            if (expenseListUl) expenseListUl.innerHTML = '<li>Error loading expenses.</li>';
            noExpensesMessage.style.display = 'none';
        }
    }

    if (expenseForm) {
        expenseForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const description = event.target.description.value;
            const amount = parseFloat(event.target.amount.value);
            const category = event.target.category.value;
            const expense_date = event.target.expense_date.value; // YYYY-MM-DD or empty

            if (!description || isNaN(amount) || !category) {
                showExpenseMessage("Please fill in all required fields correctly.", true);
                return;
            }

            const formData = new FormData();
            formData.append('description', description);
            formData.append('amount', amount.toString());
            formData.append('category', category);
            if (expense_date) {
                formData.append('expense_date_str', expense_date);
            }

            try {
                // The backend /expenses/add endpoint expects form data and redirects
                // For a pure API approach with JS handling, we might change backend to return JSON
                // and then call fetchAndDisplayExpenses() here.
                // For now, we submit the form which will cause a page reload via redirect.
                
                // To use the JSON API and update dynamically:
                // await fetchWithAuth('/expenses/add', { // This would need the backend to change
                //     method: 'POST',
                //     body: JSON.stringify({ description, amount, category, expense_date })
                // });
                // showExpenseMessage("Expense added successfully!");
                // fetchAndDisplayExpenses();
                // expenseForm.reset();

                // Current approach using form data and backend redirect for /expenses/add:
                const response = await fetch('/expenses/add', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${currentIdToken}`,
                        // 'Content-Type' will be set by browser for FormData
                    },
                    body: formData
                });

                if (response.ok && response.redirected) {
                    window.location.href = response.url; // Follow redirect
                } else if (!response.ok) {
                    const errorData = await response.json().catch(() => ({ detail: 'Failed to add expense.' }));
                    showExpenseMessage(errorData.detail, true);
                } else {
                    // Not redirected but OK, maybe an API that returns JSON on success.
                    // This path not expected with current /expenses/add redirect.
                    showExpenseMessage("Expense added! Refreshing...", false);
                    fetchAndDisplayExpenses(); // Refresh list
                }
                expenseForm.reset();

            } catch (error) {
                console.error("Failed to add expense:", error);
                showExpenseMessage(error.message || "Error adding expense.", true);
            }
        });
    }

    // Initial check if on dashboard page (in case user is already logged in and lands there)
    // The onAuthStateChanged listener will also call this.
    // if (window.location.pathname.startsWith(dashboardPath) && auth.currentUser) {
    //     fetchAndDisplayExpenses();
    // }

} else {
    console.error("Firebase SDK not loaded. Authentication and dynamic features will not work.");
    // Display a prominent error to the user on the page if Firebase doesn't load.
    const body = document.querySelector('body');
    if (body) {
        const errorDiv = document.createElement('div');
        errorDiv.textContent = 'Critical Error: Firebase could not be loaded. App functionality is limited.';
        errorDiv.style.color = 'white';
        errorDiv.style.backgroundColor = 'red';
        errorDiv.style.padding = '10px';
        errorDiv.style.textAlign = 'center';
        errorDiv.style.position = 'fixed';
        errorDiv.style.top = '0';
        errorDiv.style.width = '100%';
        errorDiv.style.zIndex = '1000';
        body.prepend(errorDiv);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    console.log("Budget Tracker App JS Loaded - Custom Auth Version");

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
                const userData = await fetchWithAuth('/auth/users/me');
                if (userData && userData.email) {
                    updateNavUI(true, userData.email);
                    if (window.location.pathname === loginPath || window.location.pathname === registerPath) {
                        window.location.href = dashboardPath;
                    }
                    if (window.location.pathname.startsWith(dashboardPath)){
                        fetchAndDisplayExpenses();
                    }
                } else {
                    throw new Error("Invalid user data from /users/me");
                }
            } catch (error) {
                console.warn("Session invalid or expired, clearing token:", error.message);
                removeToken();
                updateNavUI(false);
                if (window.location.pathname.startsWith(dashboardPath)) {
                    window.location.href = loginPath; 
                }
            }
        } else {
            updateNavUI(false);
            if (window.location.pathname.startsWith(dashboardPath)) {
                window.location.href = loginPath;
            }
        }
    }

    // --- Event Handlers ---
    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            showAuthMessage(loginAuthError, ''); // Clear previous errors
            const email = loginEmailInput.value;
            const password = loginPasswordInput.value;

            // FastAPI's OAuth2PasswordRequestForm expects x-www-form-urlencoded
            const formData = new URLSearchParams();
            formData.append('username', email); // FastAPI uses 'username' field for email here
            formData.append('password', password);

            try {
                const data = await fetchWithAuth('/auth/token', {
                    method: 'POST',
                    body: formData
                });
                storeToken(data.access_token);
                await checkLoginState(); // This will redirect to dashboard if successful
            } catch (error) {
                showAuthMessage(loginAuthError, error.message, true);
            }
        });
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
                await fetchWithAuth('/auth/register', {
                    method: 'POST',
                    body: JSON.stringify({ email, full_name: fullName, password })
                });
                showAuthMessage(regAuthMessage, "Registration successful! Please login.", false);
                setTimeout(() => { window.location.href = loginPath; }, 2000);
            } catch (error) {
                showAuthMessage(regAuthMessage, error.message, true);
            }
        });
    }

    if (navLogoutLink) {
        navLogoutLink.addEventListener('click', (event) => {
            event.preventDefault();
            removeToken();
            updateNavUI(false);
            window.location.href = homePath;
        });
    }

    async function fetchAndDisplayExpenses() {
        if (!expenseListUl || !noExpensesMessage) return;
        try {
            const expenses = await fetchWithAuth('/expenses/'); // GET request to our API
            expenseListUl.innerHTML = ''; 
            if (expenses && expenses.length > 0) {
                noExpensesMessage.style.display = 'none';
                expenses.forEach(exp => {
                    const li = document.createElement('li');
                    li.textContent = `${exp.expense_date}: ${exp.description} - $${exp.amount.toFixed(2)} (${exp.category})`;
                    expenseListUl.appendChild(li);
                });
            } else {
                noExpensesMessage.style.display = 'block';
            }
        } catch (error) {
            console.error("Failed to fetch expenses:", error);
            if (expenseListUl) expenseListUl.innerHTML = `<li>Error loading expenses: ${error.message}</li>`;
            noExpensesMessage.style.display = 'none';
        }
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
                    window.location.href = dashboardPath; // Or response.headers.get('Location') if available and reliable
                } else if (response.ok) {
                    // This case might occur if the server doesn't redirect but returns 200/201 with JSON
                    showAuthMessage(expenseMessage, "Expense added! Refreshing...", false);
                    fetchAndDisplayExpenses(); 
                    expenseForm.reset();
                } else {
                    // Handle actual error responses
                    const errorData = await response.json().catch(() => ({ detail: 'Failed to add expense.' }));
                    showAuthMessage(expenseMessage, errorData.detail, true);
                }
            } catch (error) {
                console.error("Failed to add expense:", error);
                showAuthMessage(expenseMessage, error.message || "Error adding expense.", true);
            }
        });
    }

    // --- Initial Page Load Logic ---
    checkLoginState();

}); 