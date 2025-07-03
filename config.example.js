// Dashboard Configuration Template
// Copy this file to config.js and add your actual configuration

window.OPENWEATHER_API_KEY = 'YOUR_API_KEY_HERE';

// Other configuration options
window.DASHBOARD_CONFIG = {
    slideInterval: 60000, // 60 seconds per slide (default for slides not in slideDurations)
    weatherUpdateInterval: 600000, // 10 minutes
    autoReloadInterval: 300000, // 5 minutes
    location: {
        name: 'Chicago',
        lat: 41.8781,
        lon: -87.6298
    },
    
    // Individual slide durations (optional)
    // Override the default slideInterval for specific slides
    slideDurations: {
        // 'gantt_2025_07.png': 30000,     // 30 seconds
        // 'gantt_2025_08.png': 15000,     // 15 seconds
        // 'gantt_daily_2025_07_02.png': 30000,   // 30 seconds
        // 'announcements': 90000  // 90 seconds
    },
    
    // Slide order configuration (optional)
    // Order: 1 = first (after announcements), higher numbers = later
    slideOrder: {
        'daily': 1,    // Happening Today
        'weekly': 2,   // Happening This Week
        'current': 3,  // This Month
        'next': 4,     // Next Month
        'third': 5,    // Third Month
        'calendar': 6  // Calendar
    },
    
    // Raspberry Pi Performance Settings
    // These settings are automatically applied when Pi is detected
    // You can override the detection or force Pi mode
    raspberryPi: {
        // Force Pi mode on/off (overrides auto-detection)
        // forceMode: true,        // Force Pi optimizations on
        // forceMode: false,       // Force Pi optimizations off
        
        // Pi-specific timing (applied automatically when Pi detected)
        slideInterval: 90000,      // 90 seconds per slide (longer for Pi)
        weatherUpdateInterval: 1200000, // 20 minutes (less frequent)
        autoReloadInterval: 600000,     // 10 minutes (less frequent)
        
        // Pi visual optimizations
        disableAnimations: true,    // Disable all animations
        disableBackdropFilter: true, // Disable backdrop filters
        disableShadows: true,       // Disable all shadows
        useSystemFonts: true,       // Use system fonts instead of web fonts
        reduceImageQuality: true,   // Optimize images for speed over quality
        
        // Pi memory optimizations
        hideInactiveSlides: true,   // Hide inactive slides to save memory
        limitStorageSize: true,     // Limit localStorage usage
        enableGarbageCollection: true, // Enable periodic garbage collection
        
        // Pi network optimizations
        reducedUpdateFrequency: true, // Less frequent updates
        disableServiceWorker: true,   // Disable service worker
        
        // Advanced Pi settings
        customStyles: {
            // Add custom CSS for Pi mode
            // Example: Force specific colors or layouts
            // 'body.raspberry-pi-mode': {
            //     background: '#1a1a2e !important'
            // }
        }
    },
    
    // Cloud sync for announcements (optional but recommended for multi-device use)
    cloudSync: {
        enabled: true, // Cloud sync enabled for multi-device announcements
        url: 'https://api.jsonbin.io/v3/b/686350a78a456b7966b930b1' // Public JSONBin for collaborative announcements
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
    //
    // RASPBERRY PI OPTIMIZATION NOTES:
    // 🍓 Pi mode is auto-detected based on:
    //    - ARM architecture + Linux + Chromium
    //    - Raspberry Pi user agent strings
    //    - Low core count (≤4 cores)
    //    - Other Pi-specific indicators
    //
    // 🚀 Pi optimizations automatically applied:
    //    - All animations disabled
    //    - Backdrop filters removed
    //    - Shadows and effects disabled
    //    - System fonts used
    //    - Memory usage optimized
    //    - Update frequencies reduced
    //    - Image quality optimized for speed
    //
    // 🔧 To force Pi mode on any device:
    //    Set raspberryPi.forceMode: true
    //
    // 🔧 To disable Pi mode on actual Pi:
    //    Set raspberryPi.forceMode: false
    //
    // 📊 Pi performance tips:
    //    - Use lower resolution images (1080p max)
    //    - Increase slide intervals to 90+ seconds
    //    - Reduce announcement count for better performance
    //    - Consider using wired ethernet over WiFi
    //    - Use a high-quality SD card (Class 10 or better)
    //    - Ensure adequate power supply (2.5A minimum)
}; 