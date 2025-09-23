// Minimal working functions for business dashboard
function showSection(sectionName) {
    console.log('Showing section:', sectionName);
    
    // Hide all sections
    const sections = document.querySelectorAll('.section-content');
    sections.forEach(section => section.style.display = 'none');
    
    // Remove active class from all nav buttons
    const navBtns = document.querySelectorAll('.nav-btn');
    navBtns.forEach(btn => btn.classList.remove('active'));
    
    // Show selected section
    const targetSection = document.getElementById(sectionName);
    if (targetSection) {
        targetSection.style.display = 'block';
    }
    
    // Add active class to clicked button
    const activeBtn = document.getElementById(sectionName + '-btn');
    if (activeBtn) {
        activeBtn.classList.add('active');
    }
    
    // Load section-specific data
    if (sectionName === 'live-orders') {
        loadDashboard();
    } else if (sectionName === 'analytics') {
        loadSales('day');
    } else if (sectionName === 'qr-codes') {
        loadQRCodes();
    } else if (sectionName === 'waiters-new') {
        loadWaiters();
    } else if (sectionName === 'menu-management') {
        loadMenuItems();
    }
}

function logout() {
    const currentPath = window.location.pathname;
    if (currentPath.includes('/r/')) {
        const subdomain = currentPath.split('/r/')[1].split('/')[0];
        window.location.href = `/r/${subdomain}/business/login`;
    } else {
        window.location.href = '/business/login';
    }
}

// Placeholder functions to prevent errors
function loadDashboard() { console.log('loadDashboard called'); }
function loadSales(period) { console.log('loadSales called:', period); }
function loadQRCodes() { console.log('loadQRCodes called'); }
function loadWaiters() { console.log('loadWaiters called'); }
function loadMenuItems() { console.log('loadMenuItems called'); }
function addWaiter() { console.log('addWaiter called'); }
function cancelOrder() { console.log('cancelOrder called'); }
function openQRCodesWindow() { console.log('openQRCodesWindow called'); }
function printAllQRCodes() { console.log('printAllQRCodes called'); }

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    showSection('live-orders');
});