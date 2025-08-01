# Raspberry Pi Optimization Guide 🍓

Your Encore Dashboard includes sophisticated **automatic optimization** for Raspberry Pi devices, ensuring smooth performance even on low-powered hardware.

## ⚡ Automatic Pi Detection

The dashboard automatically detects when it's running on a Raspberry Pi and applies optimizations:

### Detection Criteria:
- **ARM Architecture**: Detects ARM and aarch64 processors
- **Linux + Chromium**: Common Pi setup combination
- **User Agent**: Raspberry Pi, Raspbian, or Pi-specific strings
- **Hardware Limits**: Low core count (≤4 cores), limited memory (≤8GB)
- **GPU Capabilities**: Reduced graphics processing power

### Force Pi Mode:
```javascript
// In config.js - Force Pi mode on any device
window.DASHBOARD_CONFIG = {
    raspberryPi: {
        forceMode: true    // Force Pi optimizations ON
        // forceMode: false   // Force Pi optimizations OFF
    }
};
```

## 🚀 Performance Optimizations Applied

### Visual Optimizations:
- ✅ **All animations disabled** - Eliminates CPU-intensive animations
- ✅ **Backdrop filters removed** - Reduces GPU load
- ✅ **Box shadows disabled** - Simplifies rendering
- ✅ **Text shadows removed** - Faster text rendering
- ✅ **Floating elements hidden** - Reduces DOM complexity
- ✅ **Static backgrounds** - Replaces animated gradients
- ✅ **Simplified borders** - Reduces CSS complexity
- ✅ **System fonts used** - Eliminates web font loading

### Memory Optimizations:
- ✅ **Inactive slides hidden** - Saves memory by hiding non-visible slides
- ✅ **Limited DOM elements** - Reduces memory footprint
- ✅ **Garbage collection** - Automatic memory cleanup
- ✅ **Storage limits** - Prevents localStorage bloat
- ✅ **Service worker disabled** - Eliminates background processing

### Network Optimizations:
- ✅ **Reduced update frequencies** - Less network activity
- ✅ **Lazy image loading** - Images load only when needed
- ✅ **Optimized requests** - Fewer API calls

### CPU Optimizations:
- ✅ **Simplified transitions** - Immediate slide changes
- ✅ **Reduced calculations** - Fewer JavaScript operations
- ✅ **Optimized rendering** - Faster page updates
- ✅ **RequestAnimationFrame fallback** - Consistent 60fps

## 🔧 Configuration Options

### Timing Settings (Pi-specific):
```javascript
window.DASHBOARD_CONFIG = {
    raspberryPi: {
        slideInterval: 90000,           // 90 seconds per slide (vs 60s desktop)
        weatherUpdateInterval: 1200000, // 20 minutes (vs 10min desktop)
        autoReloadInterval: 600000,     // 10 minutes (vs 5min desktop)
    }
};
```

### Visual Settings:
```javascript
window.DASHBOARD_CONFIG = {
    raspberryPi: {
        disableAnimations: true,        // Disable all animations
        disableBackdropFilter: true,    // Remove backdrop filters
        disableShadows: true,          // Remove shadows
        useSystemFonts: true,          // Use system fonts
        reduceImageQuality: true,      // Optimize images for speed
    }
};
```

### Memory Settings:
```javascript
window.DASHBOARD_CONFIG = {
    raspberryPi: {
        hideInactiveSlides: true,       // Hide inactive slides
        limitStorageSize: true,         // Limit localStorage
        enableGarbageCollection: true,  // Enable memory cleanup
    }
};
```

### Custom Styles:
```javascript
window.DASHBOARD_CONFIG = {
    raspberryPi: {
        customStyles: {
            'body.raspberry-pi-mode': {
                background: '#1a1a2e !important'
            },
            '.raspberry-pi-mode .slide': {
                'border-radius': '4px !important'
            }
        }
    }
};
```

## 📊 Performance Comparison

| Feature | Desktop | Raspberry Pi |
|---------|---------|-------------|
| **Animations** | Smooth CSS animations | Disabled for performance |
| **Backdrop Filters** | Glass effects enabled | Disabled to reduce GPU load |
| **Slide Transitions** | Animated (0.6s) | Immediate |
| **Update Frequency** | Weather: 10min | Weather: 20min |
| **Memory Usage** | All slides loaded | Only active slide |
| **Font Loading** | Web fonts | System fonts |
| **Visual Effects** | Full shadows/gradients | Simplified solid colors |

## 🎯 Pi-Specific Features

### 1. **Smart Memory Management**
- Only the active slide is kept in memory
- Inactive slides are hidden with `display: none`
- Periodic garbage collection hints
- LocalStorage size limits

### 2. **Optimized Image Handling**
- Images set to `loading="lazy"`
- Image rendering optimized for speed over quality
- Large image warnings in console
- Automatic image optimization

### 3. **Reduced Network Activity**
- Less frequent weather updates
- Longer slide intervals
- Reduced API call frequency
- Disabled service workers

### 4. **CPU-Friendly Rendering**
- Static color cycles instead of complex gradients
- Simplified CSS selectors
- Reduced DOM complexity
- Optimized font rendering

## 🛠️ Pi Setup Best Practices

### 1. **Hardware Recommendations**
```bash
# Minimum Requirements
- Raspberry Pi 3B+ or newer
- 16GB+ SD card (Class 10 or better)
- 2.5A power supply
- Wired ethernet (recommended over WiFi)

# Optimal Setup
- Raspberry Pi 4 with 4GB+ RAM
- 32GB+ SD card (Class 10 or better)  
- 3A power supply
- Wired ethernet connection
```

### 2. **OS Configuration**
```bash
# Disable unnecessary services
sudo systemctl disable bluetooth
sudo systemctl disable wifi-powersave

# Optimize memory
echo "gpu_mem=64" | sudo tee -a /boot/config.txt

# Disable swap for better SD card life
sudo dphys-swapfile swapoff
sudo systemctl disable dphys-swapfile
```

### 3. **Browser Launch**
```bash
# Optimal Chromium flags for Pi
chromium-browser \
  --kiosk \
  --incognito \
  --disable-pinch \
  --disable-dev-shm-usage \
  --no-sandbox \
  --disable-setuid-sandbox \
  --disable-features=VizDisplayCompositor \
  --disable-background-timer-throttling \
  --disable-backgrounding-occluded-windows \
  --disable-renderer-backgrounding \
  --disable-background-networking \
  --memory-pressure-off \
  --max_old_space_size=100 \
  --js-flags="--max-old-space-size=100" \
  https://yourusername.github.io/EncoreDashboard/
```

## 🔍 Troubleshooting

### Performance Issues:
1. **Check Pi detection**: Look for "🍓 RASPBERRY PI DETECTED" in console
2. **Verify optimizations**: Body should have `raspberry-pi-mode` class
3. **Monitor memory**: Use `free -h` to check available memory
4. **Check network**: Ensure stable internet connection

### Force Pi Mode:
```javascript
// If Pi isn't detected automatically
window.DASHBOARD_CONFIG = {
    raspberryPi: {
        forceMode: true
    }
};
```

### Debugging:
```javascript
// Check if Pi mode is active
console.log('Pi mode:', document.body.classList.contains('raspberry-pi-mode'));

// View detection details
// Look for "🔍 Device detection analysis" in console
```

## 📈 Performance Monitoring

### Browser Console:
- **Pi Detection**: Shows detailed analysis of device capabilities
- **Memory Warnings**: Alerts for large operations
- **Image Optimization**: Reports on image processing
- **Update Frequency**: Shows reduced timing on Pi

### Performance Metrics:
- **Memory Usage**: Significantly reduced vs desktop
- **CPU Usage**: Lower due to disabled animations
- **Network Usage**: Reduced update frequency
- **Battery Life**: Extended on portable devices

## 🎨 Visual Differences

### Desktop Mode:
- Smooth animations and transitions
- Glass effects with backdrop filters
- Floating particle effects
- Animated gradients and shadows
- Web font loading

### Pi Mode:
- Immediate transitions
- Solid color backgrounds
- No floating elements
- Static colors
- System fonts only

**The dashboard still looks great on Pi** - just optimized for performance over visual flair!

## 🚀 Advanced Optimization

### Custom Pi Styles:
```javascript
// Add custom optimizations
window.DASHBOARD_CONFIG = {
    raspberryPi: {
        customStyles: {
            // Further reduce visual complexity
            '.raspberry-pi-mode .announcement-item': {
                'border': '1px solid #333 !important',
                'background': '#2a2a4e !important'
            },
            // Optimize for specific screen size
            '.raspberry-pi-mode .slide img': {
                'max-width': '1920px !important',
                'max-height': '1080px !important'
            }
        }
    }
};
```

### Performance Monitoring:
```javascript
// Log performance metrics
setInterval(() => {
    if (performance.memory) {
        console.log('Memory usage:', {
            used: Math.round(performance.memory.usedJSHeapSize / 1024 / 1024) + 'MB',
            total: Math.round(performance.memory.totalJSHeapSize / 1024 / 1024) + 'MB'
        });
    }
}, 60000); // Every minute
```

## 📋 Optimization Checklist

- [ ] Pi detection working (check console)
- [ ] `raspberry-pi-mode` class applied to body
- [ ] Animations disabled
- [ ] Backdrop filters removed
- [ ] System fonts loading
- [ ] Reduced update frequencies
- [ ] Memory optimizations active
- [ ] Image optimization enabled
- [ ] Network requests reduced
- [ ] Performance monitoring active

---

**Your dashboard automatically optimizes for Raspberry Pi - no manual configuration needed!** 🍓✨

The optimizations ensure smooth performance while maintaining the dashboard's functionality and visual appeal. 