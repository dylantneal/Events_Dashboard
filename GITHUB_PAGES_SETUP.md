# GitHub Pages Deployment Guide

This guide shows how to deploy your EncoreDashboard with announcements board to GitHub Pages for free, secure hosting.

## Quick Setup (5 minutes)

### 1. Repository Setup
```bash
# Make sure your repository is pushed to GitHub
git add -A
git commit -m "Prepare for GitHub Pages deployment"
git push origin main
```

### 2. Enable GitHub Pages
1. Go to your GitHub repository
2. Click **Settings** → **Pages**
3. Under **Source**, select **GitHub Actions**
4. The workflow will automatically deploy on the next push

### 3. Access Your Dashboard
- Your dashboard will be available at: `https://yourusername.github.io/EncoreDashboard/`
- Announcements board is fully functional on the live site
- All features work exactly as in local development

## Features on GitHub Pages

### ✅ Fully Functional
- **Announcements Board**: Complete CRUD operations
- **Real-time Weather**: Using Open-Meteo API (no key required)
- **Live Clock**: Works perfectly with time zones
- **Slide Rotation**: Automatic slideshow with Gantt charts
- **Export/Import**: Backup and restore announcements
- **Responsive Design**: Works on all devices

### 📱 Cross-Device Considerations
- **Announcements are stored per-device** (localStorage)
- **To share announcements between devices:**
  1. Press `Ctrl+E` to export from Device A
  2. Press `Ctrl+I` to import to Device B
  3. Or use this for backup before clearing browser data

### 🔧 Configuration Options

#### Weather API (Optional)
```javascript
// In config.js, you can:
// Option 1: Use free Open-Meteo (default, no key needed)
window.OPENWEATHER_API_KEY = 'YOUR_API_KEY_HERE';

// Option 2: Use OpenWeatherMap for more accuracy
window.OPENWEATHER_API_KEY = 'your-actual-api-key-here';
```

#### Custom Settings
```javascript
// Adjust timing and behavior
window.DASHBOARD_CONFIG = {
    slideDuration: 60000,        // 60 seconds per slide
    weatherUpdateInterval: 600000, // 10 minutes
    autoReloadInterval: 600000    // 10 minutes
};
```

## Deployment Process

### Automatic Deployment
- **Push to main** → Automatic deployment
- **Build time**: ~30-60 seconds
- **Zero downtime**: Atomic deployments
- **HTTPS**: Automatically secured

### Manual Deployment
```bash
# Update content and deploy
git add -A
git commit -m "Update announcements or content"
git push origin main
# GitHub Actions automatically deploys
```

## Multi-Device Usage

### Kiosk Deployment
```bash
# For Raspberry Pi or dedicated displays
chromium-browser --kiosk --incognito \
  https://yourusername.github.io/EncoreDashboard/
```

### Mobile/Tablet Access
- Works perfectly on iOS/Android
- Add to home screen for app-like experience
- Responsive design adapts to any screen size

### Office Computers
- Bookmark the GitHub Pages URL
- Auto-refresh keeps content current
- Each computer maintains its own announcements

## Announcement Management

### Single Administrator
```javascript
// Admin manages all announcements on one device
// Export backups regularly with Ctrl+E
```

### Multiple Administrators
```javascript
// Method 1: Shared export/import
// 1. Primary admin exports announcements
// 2. Secondary admins import the file
// 3. Both can create new announcements
// 4. Periodic sync via export/import

// Method 2: Time-based coordination
// 1. Morning admin: 6 AM - 12 PM announcements
// 2. Afternoon admin: 12 PM - 6 PM announcements
// 3. Evening admin: 6 PM - 6 AM announcements
```

## Security & Privacy

### Data Storage
- **Announcements**: Stored in browser localStorage (per device)
- **No server storage**: No data leaves your control
- **Private by default**: Only accessible via your GitHub Pages URL

### Access Control
```bash
# Option 1: Private repository (GitHub Pro required)
# Dashboard only accessible to repository collaborators

# Option 2: Public repository with security through obscurity
# Use a non-obvious repository name
```

## Content Updates

### Gantt Charts
```bash
# Generate new charts locally
python3 flex_gantt.py pipeline.xlsx --rolling-window --dashboard

# Deploy to GitHub Pages
git add slides/
git commit -m "Update Gantt charts"
git push origin main
```

### Announcements
- Create directly on the live site
- No deployment needed - instant updates
- Export backups regularly

## Troubleshooting

### Common Issues

**Announcements not appearing on other devices?**
- Expected behavior - use export/import to sync

**Weather not loading?**
- Check browser console for API errors
- Open-Meteo should work without API key

**Slides not displaying?**
- Ensure slide images are in `slides/` directory
- Check that `slides.json` is properly formatted

**404 Error on GitHub Pages?**
- Verify repository name matches URL
- Check that GitHub Pages is enabled in Settings

### Performance Tips
```javascript
// For slower networks, increase timeouts
slideTimeout: 120000,  // 2 minutes instead of 1
weatherTimeout: 900000 // 15 minutes instead of 10
```

## Advanced Configuration

### Custom Domain (Optional)
1. Add `CNAME` file with your domain
2. Configure DNS with your provider
3. Enable HTTPS in repository settings

### Analytics (Optional)
```html
<!-- Add to index.html head section -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
```

### Backup Strategy
```bash
# Weekly announcements backup
# 1. Export announcements (Ctrl+E)
# 2. Save to cloud storage or email
# 3. Keep 4 weeks of backups
```

## Production Checklist

- [ ] Repository pushed to GitHub
- [ ] GitHub Pages enabled with GitHub Actions
- [ ] Weather API configured (or using Open-Meteo default)
- [ ] Test announcements created and working
- [ ] Export/import tested for backup
- [ ] Dashboard accessible at GitHub Pages URL
- [ ] Responsive design tested on target devices
- [ ] Backup procedure established

## Support

### Getting Help
1. **Check browser console** (F12) for errors
2. **Test locally first** with `python3 -m http.server 8080`
3. **Verify GitHub Actions** completed successfully
4. **Check repository settings** for Pages configuration

### Common Solutions
- **Cache issues**: Hard refresh with `Ctrl+Shift+R`
- **API problems**: Check network connectivity
- **Permission errors**: Verify repository permissions
- **Build failures**: Check GitHub Actions tab for errors

Your dashboard is now ready for professional deployment on GitHub Pages! 🚀 