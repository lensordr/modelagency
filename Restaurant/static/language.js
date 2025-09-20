// Language switching functionality
let currentLanguage = 'en';

function setLanguage(lang) {
    currentLanguage = lang;
    localStorage.setItem('tablelink_language', lang);
    
    // Update language buttons
    document.querySelectorAll('.lang-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById(`lang-${lang}`).classList.add('active');
    
    // Update all elements with language attributes
    document.querySelectorAll('[data-en]').forEach(element => {
        const text = element.getAttribute(`data-${lang}`);
        if (text) {
            if (element.tagName === 'INPUT' && element.type === 'button') {
                element.value = text;
            } else if (element.tagName === 'BUTTON') {
                element.textContent = text;
            } else {
                element.textContent = text;
            }
        }
    });
    
    // Update total display
    updateTotalDisplay();
    
    // Update menu items
    updateMenuLanguage();
}

function updateTotalDisplay() {
    const totalElement = document.getElementById('total');
    if (totalElement && window.orderTotal !== undefined) {
        const totalText = currentLanguage === 'es' ? 'Total: $' : 'Total: $';
        totalElement.textContent = totalText + window.orderTotal.toFixed(2);
    }
}

// Initialize language on page load
document.addEventListener('DOMContentLoaded', function() {
    const savedLanguage = localStorage.getItem('tablelink_language') || 'en';
    setLanguage(savedLanguage);
});

// Translations object for dynamic content
const translations = {
    en: {
        'add_to_order': 'Add to Order',
        'remove': 'Remove',
        'total': 'Total',
        'no_tip': 'No Tip',
        'custom': 'Custom',
        'pay_with_cash': '💵 Pay with Cash',
        'pay_with_card': '💳 Pay with Card',
        'request_checkout': '💳 Request Checkout',
        'select_tip': '💰 Select Tip Amount',
        'selected_tip': 'Selected Tip',
        'enter_custom_tip': 'Enter custom tip amount'
    },
    es: {
        'add_to_order': 'Agregar al Pedido',
        'remove': 'Eliminar',
        'total': 'Total',
        'no_tip': 'Sin Propina',
        'custom': 'Personalizado',
        'pay_with_cash': '💵 Pagar en Efectivo',
        'pay_with_card': '💳 Pagar con Tarjeta',
        'request_checkout': '💳 Solicitar Cuenta',
        'select_tip': '💰 Seleccionar Propina',
        'selected_tip': 'Propina Seleccionada',
        'enter_custom_tip': 'Ingresa cantidad de propina personalizada'
    }
};

function t(key) {
    return translations[currentLanguage][key] || translations['en'][key] || key;
}

// Menu item translations
const menuTranslations = {
    en: {
        'Margherita Pizza': 'Margherita Pizza',
        'Pepperoni Pizza': 'Pepperoni Pizza',
        'Caesar Salad': 'Caesar Salad',
        'Greek Salad': 'Greek Salad',
        'Coca Cola': 'Coca Cola',
        'Orange Juice': 'Orange Juice',
        'Coffee': 'Coffee',
        'Tea': 'Tea',
        'Tiramisu': 'Tiramisu',
        'Cheesecake': 'Cheesecake'
    },
    es: {
        'Margherita Pizza': 'Pizza Margherita',
        'Pepperoni Pizza': 'Pizza Pepperoni',
        'Caesar Salad': 'Ensalada César',
        'Greek Salad': 'Ensalada Griega',
        'Coca Cola': 'Coca Cola',
        'Orange Juice': 'Jugo de Naranja',
        'Coffee': 'Café',
        'Tea': 'Té',
        'Tiramisu': 'Tiramisú',
        'Cheesecake': 'Tarta de Queso',
        'Salmon Fillet': 'Filete de Salmón',
        'Vegetarian Pasta': 'Pasta Vegetariana'
    }
};

function translateMenuItem(itemName) {
    return menuTranslations[currentLanguage][itemName] || itemName;
}

// Function to update menu items when language changes
function updateMenuLanguage() {
    document.querySelectorAll('.menu-item-name').forEach(element => {
        const originalName = element.getAttribute('data-original-name');
        if (originalName) {
            element.textContent = translateMenuItem(originalName);
        }
    });
    
    document.querySelectorAll('.order-item-name').forEach(element => {
        const originalName = element.getAttribute('data-original-name');
        if (originalName) {
            element.textContent = translateMenuItem(originalName);
        }
    });
}