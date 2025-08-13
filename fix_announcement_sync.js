// Fix for announcement synchronization issues - DISABLED DURING PHASE 2 CLEANUP
// This script was creating aggressive sync timing that may cause rate limits
// Disabled to allow original system to work properly

console.log('⚠️ ANNOUNCEMENT SYNC FIX: DISABLED - Using original system instead');
// Early return to prevent any interference
if (true) {
    console.log('🚫 fix_announcement_sync.js is disabled - original sync system has proper timing');
    // Exit immediately without making any changes
}

// Wait for dashboard to be ready
function waitForDashboard() {
    return new Promise((resolve) => {
        if (window.dashboard) {
            resolve(window.dashboard);
        } else {
            const checkInterval = setInterval(() => {
                if (window.dashboard) {
                    clearInterval(checkInterval);
                    resolve(window.dashboard);
                }
            }, 100);
        }
    });
}

// Enhanced cloud sync functionality
async function enhancedCloudSync() {
    const dashboard = await waitForDashboard();
    
    // Override the saveToCloud function with better error handling
    dashboard.saveToCloud = async function(announcements) {
        if (!this.cloudSyncUrl) {
            throw new Error('Cloud sync URL not configured');
        }

        const payload = { announcements: announcements };
        console.log('💾 ENHANCED SAVE TO CLOUD:', announcements.length, 'announcements');
        
        // For public bins, we need to use a different approach
        const saveUrl = this.cloudSyncUrl.replace('/latest', '');
        console.log('Save URL:', saveUrl);
        
        try {
            const response = await fetch(saveUrl, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    // Don't include API key for public bins
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                // If PUT fails, try POST (for creating new public bins)
                console.log('PUT failed, trying POST...');
                const createUrl = 'https://api.jsonbin.io/v3/b';
                const createResponse = await fetch(createUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Bin-Private': 'false' // Make it public
                    },
                    body: JSON.stringify(payload)
                });
                
                if (createResponse.ok) {
                    const result = await createResponse.json();
                    console.log('✅ Created new public bin:', result.metadata.id);
                    // Update the URL to use the new bin
                    const newUrl = `https://api.jsonbin.io/v3/b/${result.metadata.id}/latest`;
                    this.cloudSyncUrl = newUrl;
                    console.log('📝 Updated cloud sync URL to:', newUrl);
                    return result;
                } else {
                    throw new Error(`Failed to create bin: ${createResponse.status}`);
                }
            }

            const result = await response.json();
            console.log('✅ Cloud save successful');
            return result;
        } catch (error) {
            console.error('❌ Cloud save failed:', error);
            throw error;
        }
    };

    // Enhanced time checking with better timezone handling
    dashboard.getCurrentAnnouncements = function() {
        const now = new Date();
        console.log('🕐 Checking announcements at:', now.toLocaleString());
        
        const currentAnnouncements = this.announcements.filter(announcement => {
            // Create date objects in local timezone
            const startDateTime = new Date(announcement.startDate + 'T' + announcement.startTime);
            const endDateTime = new Date(announcement.endDate + 'T' + announcement.endTime);
            
            const isActive = now >= startDateTime && now <= endDateTime;
            
            console.log(`📋 ${announcement.text.substring(0, 30)}...`);
            console.log(`   Start: ${startDateTime.toLocaleString()}`);
            console.log(`   End: ${endDateTime.toLocaleString()}`);
            console.log(`   Active: ${isActive ? '✅' : '❌'}`);
            
            return isActive;
        }).sort((a, b) => {
            // Sort by start date/time
            const aStart = new Date(a.startDate + 'T' + a.startTime);
            const bStart = new Date(b.startDate + 'T' + b.startTime);
            return aStart - bStart;
        });
        
        console.log(`📊 Found ${currentAnnouncements.length} active announcements`);
        return currentAnnouncements;
    };

    // Enhanced save function with immediate cloud sync
    const originalSaveAnnouncements = dashboard.saveAnnouncements.bind(dashboard);
    dashboard.saveAnnouncements = async function() {
        console.log('💾 ENHANCED SAVE: Saving announcements...');
        
        // Track when we make local changes
        this.lastLocalSaveTime = Date.now();
        
        // Always save to localStorage first (immediate backup)
        localStorage.setItem('dashboard_announcements', JSON.stringify(this.announcements));
        console.log('✅ Saved to localStorage:', this.announcements.length, 'items');
        
        // Force immediate cloud sync if enabled
        if (this.cloudSyncEnabled && this.cloudSyncUrl && !this.syncInProgress) {
            this.syncInProgress = true;
            try {
                console.log('🔄 Force syncing to cloud...');
                await this.saveToCloud(this.announcements);
                console.log('✅ Immediate cloud sync successful');
                this.lastSyncTime = Date.now();
                
                // Trigger update on all other devices by forcing a reload check
                setTimeout(() => {
                    console.log('📢 Broadcasting update signal...');
                    // This will be picked up by other devices on their next sync check
                }, 1000);
                
            } catch (cloudError) {
                console.warn('⚠️ Immediate cloud sync failed:', cloudError.message);
                // Don't fail the save operation if cloud sync fails
            } finally {
                this.syncInProgress = false;
            }
        }
    };

    // More frequent announcement updates
    if (dashboard.announcementUpdateInterval) {
        clearInterval(dashboard.announcementUpdateInterval);
    }
    
    dashboard.announcementUpdateInterval = setInterval(() => {
        console.log('🔄 Periodic announcement update...');
        if (dashboard.currentSlideIndex === dashboard.announcementsSlideIndex) {
            dashboard.updateAnnouncementsDisplay();
        }
        
        // Also sync from cloud more frequently
        if (dashboard.cloudSyncEnabled) {
            dashboard.syncAnnouncementsFromCloud();
        }
    }, 15000); // Every 15 seconds instead of 30
    
    console.log('✅ Enhanced announcement sync applied');
}

// Quick test function for announcements
async function createTestAnnouncement() {
    const dashboard = await waitForDashboard();
    
    const now = new Date();
    const testAnnouncement = {
        id: 'sync_test_' + Date.now(),
        text: `🧪 SYNC TEST: Created at ${now.toLocaleTimeString()} - should sync to cloud and other devices!`,
        startDate: now.toISOString().split('T')[0],
        startTime: now.toTimeString().split(' ')[0].slice(0, 5),
        endDate: now.toISOString().split('T')[0],
        endTime: '23:59',
        createdAt: now.toISOString(),
        lastModified: now.toISOString()
    };
    
    dashboard.announcements.push(testAnnouncement);
    await dashboard.saveAnnouncements();
    dashboard.updateAnnouncementsDisplay();
    
    console.log('✅ Test announcement created and should sync to cloud');
    alert('Test announcement created! Check if it appears on other devices.');
}

// Apply fixes when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', enhancedCloudSync);
} else {
    enhancedCloudSync();
}

// Make test function available globally
window.createTestAnnouncement = createTestAnnouncement;

console.log('🎯 Announcement sync fixes loaded. Use createTestAnnouncement() to test.'); 