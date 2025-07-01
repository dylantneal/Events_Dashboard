# Cloud Sync Setup for Announcements

The EncoreDashboard now supports automatic cloud synchronization for announcements, allowing them to appear instantly across all devices. This guide will help you set up cloud sync using JSONBin.io (free service).

## Why Enable Cloud Sync?

**Without Cloud Sync (Default Behavior):**
- Announcements are stored locally in each browser
- An announcement created on Computer A won't appear on Computer B
- Manual export/import required to share announcements between devices

**With Cloud Sync Enabled:**
- Announcements automatically sync across all devices
- Create an announcement on any device, it appears everywhere within 30 seconds
- No manual intervention needed
- Works perfectly with GitHub Pages hosting

## Quick Setup (5 minutes)

### Step 1: Create a JSONBin Account
1. Go to [https://jsonbin.io](https://jsonbin.io)
2. Click "Sign Up" and create a free account
3. The free tier includes 100,000 requests/month (more than enough)

### Step 2: Create a Storage Bin
1. After logging in, click "Create Bin"
2. Replace the default content with just an empty array: `[]`
3. Click "Create"
4. Copy the bin URL from the address bar (looks like: `https://api.jsonbin.io/v3/b/YOUR_BIN_ID`)

### Step 3: Get Your API Key (Recommended)
1. Click on your profile (top right)
2. Go to "API Keys"
3. Click "Create Access Key"
4. Give it a name like "Dashboard Announcements"
5. Copy the generated key (starts with `$2a$`)

### Step 4: Update Your Configuration
1. Copy `config.example.js` to `config.js` if you haven't already
2. Update the cloud sync section:

```javascript
cloudSync: {
    enabled: true, // Enable cloud sync
    url: 'https://api.jsonbin.io/v3/b/YOUR_BIN_ID/latest', // Your bin URL + /latest
    key: '$2a$10$YOUR_API_KEY_HERE' // Your API key
}
```

### Step 5: Test the Setup
1. Refresh your dashboard
2. Check the browser console (F12) for cloud sync messages
3. Create a test announcement
4. Open the dashboard on another device/browser
5. The announcement should appear automatically within 30 seconds

## Configuration Examples

### Minimal Setup (No API Key)
```javascript
cloudSync: {
    enabled: true,
    url: 'https://api.jsonbin.io/v3/b/YOUR_BIN_ID/latest'
    // key not required but recommended for security
}
```

### Recommended Setup (With API Key)
```javascript
cloudSync: {
    enabled: true,
    url: 'https://api.jsonbin.io/v3/b/YOUR_BIN_ID/latest',
    key: '$2a$10$abcdef1234567890...' // Your actual API key
}
```

### Disabled (Default)
```javascript
cloudSync: {
    enabled: false
    // When disabled, uses localStorage only
}
```

## How It Works

### Sync Frequency
- **Auto-sync**: Every 30 seconds in the background
- **Save-sync**: Immediately when creating/editing/deleting announcements
- **Load-sync**: When the dashboard first loads

### Fallback Behavior
- If cloud sync fails, announcements still work using localStorage
- Local storage acts as a backup even when cloud sync is enabled
- No data loss if the cloud service is temporarily unavailable

### Multi-Device Workflow
1. **Device A**: Creates an announcement → Saves to cloud immediately
2. **Device B**: Automatically detects the change within 30 seconds
3. **All devices**: Display the same announcements in real-time

## Troubleshooting

### Check Browser Console
Open browser console (F12) and look for these messages:

**✅ Working correctly:**
```
Cloud sync is enabled - announcements will sync across devices
✓ Loaded announcements from cloud: 3 items
✓ Synced announcements to cloud
```

**❌ Configuration issues:**
```
Cloud sync failed, falling back to localStorage: [error details]
```

### Common Issues

**"Failed to fetch" Error:**
- Check that your JSONBin URL is correct
- Ensure the URL ends with `/latest`
- Verify your internet connection

**"401 Unauthorized" Error:**
- Your API key might be incorrect
- Try without the API key first (remove the `key` field)

**"404 Not Found" Error:**
- Your bin ID is incorrect
- Double-check the URL from JSONBin

**Announcements not syncing:**
- Check that `enabled: true` is set
- Verify the URL format includes `/latest`
- Look for error messages in console

### Testing Cloud Sync
Use these browser console commands to test:

```javascript
// Check current sync status
console.log('Cloud sync enabled:', dashboard.cloudSyncEnabled);
console.log('Last sync:', new Date(dashboard.lastSyncTime));

// Force a sync check
dashboard.syncAnnouncementsFromCloud();

// View all announcements
dashboard.debugAnnouncements();
```

## Security & Privacy

### Data Handling
- Only announcement data is stored in the cloud
- No personal information or analytics collected
- Data is stored in your own JSONBin account

### API Key Benefits
- Prevents unauthorized access to your announcements
- Allows you to revoke access if needed
- Required for private bins (if needed)

### Alternative Services
While this guide uses JSONBin.io, the cloud sync system can work with any JSON REST API that supports GET and PUT operations. Other options include:
- Pastebin.com
- GitHub Gists
- Your own server endpoint

## Migration from Local-Only

If you have existing announcements stored locally:

1. **Before enabling cloud sync**: Export your announcements (Ctrl+E)
2. **Enable cloud sync** following the steps above
3. **Import your announcements** (Ctrl+I) to upload them to the cloud
4. All future announcements will sync automatically

## Support

### GitHub Issues
Report bugs or request features at: [Your GitHub Repository]

### Console Debugging
Enable detailed logging by adding this to your config:
```javascript
window.DASHBOARD_DEBUG = true;
```

### JSONBin Support
For JSONBin-specific issues, visit: [https://jsonbin.io/support](https://jsonbin.io/support) 