// Button Test Script for TableLink
console.log('🧪 Testing TableLink Button Functions...');

// Test functions that should exist
const requiredFunctions = [
    'showSection',
    'loadDashboard', 
    'showInstantOrderModal',
    'openKitchen',
    'logout',
    'loadMenuItems',
    'loadSales',
    'loadWaiters',
    'showOrderDetails',
    'finishTable',
    'cancelOrder',
    'addWaiter',
    'removeWaiter',
    'addMenuItem',
    'deleteMenuItem',
    'toggleProduct',
    'uploadMenu',
    'printQRCode',
    'openQRCodesWindow'
];

// Check if functions exist in global scope
requiredFunctions.forEach(funcName => {
    if (typeof window[funcName] === 'function') {
        console.log(`✅ ${funcName}: Available`);
    } else {
        console.log(`❌ ${funcName}: Missing`);
    }
});

// Test button click handlers
const buttonTests = [
    { id: 'live-orders-btn', expected: 'showSection' },
    { id: 'instant-order-btn', expected: 'showInstantOrderModal' },
    { id: 'kitchen-btn', expected: 'openKitchen' },
    { id: 'waiters-new-btn', expected: 'showSection' },
    { id: 'analytics-btn', expected: 'showSection' },
    { id: 'menu-management-btn', expected: 'showSection' },
    { id: 'qr-codes-btn', expected: 'showSection' }
];

console.log('\n🔘 Testing Button Click Handlers...');
buttonTests.forEach(test => {
    const button = document.getElementById(test.id);
    if (button && button.onclick) {
        console.log(`✅ ${test.id}: Has click handler`);
    } else {
        console.log(`❌ ${test.id}: Missing click handler`);
    }
});

console.log('\n✨ Button test completed!');