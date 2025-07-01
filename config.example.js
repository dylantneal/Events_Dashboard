// Dashboard Configuration Template
// Copy this file to config.js and add your actual configuration

window.OPENWEATHER_API_KEY = 'YOUR_API_KEY_HERE';

// Other configuration options
window.DASHBOARD_CONFIG = {
    slideInterval: 60000, // 60 seconds per slide
    weatherUpdateInterval: 600000, // 10 minutes
    autoReloadInterval: 300000, // 5 minutes
    location: {
        name: 'Chicago',
        lat: 41.8781,
        lon: -87.6298
    },
    
    // Cloud sync for announcements (optional but recommended for multi-device use)
    cloudSync: {
        enabled: true, // Cloud sync enabled for multi-device announcements
        url: 'https://api.jsonbin.io/v3/b/686350a78a456b7966b930b1/latest' // Public JSONBin for collaborative announcements
        // No API key needed for public bins - perfect for collaborative announcements!
    }
    
    // CLOUD SYNC SETUP INSTRUCTIONS:
    // 1. Go to https://jsonbin.io and create a free account
    // 2. Create a new PUBLIC bin with content: { "announcements": [] }
    // 3. Copy the bin URL (change /edit to /latest)
    // 4. Replace YOUR_JSONBIN_URL_HERE with your bin URL
    // 5. Set enabled: true
    // 6. Save as config.js and deploy!
    // 
    // Example URL:
    // url: 'https://api.jsonbin.io/v3/b/YOUR_BIN_ID/latest'
    // 
    // Benefits:
    // ✅ Announcements sync across all devices automatically
    // ✅ Anyone can add announcements (collaborative bulletin board)
    // ✅ Works perfectly with GitHub Pages
    // ✅ Free service (100k requests/month)
}; 