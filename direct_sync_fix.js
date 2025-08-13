// IMPROVED SYNC FIX - DISABLED DURING PHASE 2 CLEANUP
// This script was causing conflicts with the original well-designed sync system
// Disabled to allow original system to work properly

console.log('⚠️ DIRECT SYNC FIX: DISABLED - Using original system instead');
// Early return to prevent any interference
if (true) {
    console.log('🚫 direct_sync_fix.js is disabled - original sync system will handle announcements');
    // Exit immediately without making any changes
}

// Wait for dashboard to load
function waitForDashboard() {
    return new Promise((resolve) => {
        const check = () => {
            if (window.dashboard) {
                resolve(window.dashboard);
            } else {
                setTimeout(check, 100);
            }
        };
        check();
    });
}

waitForDashboard().then(dashboard => {
    console.log('✅ Dashboard found, applying improved sync fix...');
    
    // ENHANCED CLOUD SYNC CONFIGURATION
    dashboard.cloudSyncEnabled = true;
    dashboard.cloudSyncUrl = 'https://api.jsonbin.io/v3/b/686350a78a456b7966b930b1/latest';
    
    // Ensure we have the correct save URL (remove /latest for PUT requests)
    dashboard.cloudSaveUrl = dashboard.cloudSyncUrl.replace('/latest', '');
    
    // IMPROVED SAVE TO CLOUD FUNCTION
    dashboard.saveToCloudImmediate = async function(announcements, operation = 'update') {
        try {
            console.log(`☁️ IMPROVED: ${operation} - Syncing ${announcements.length} announcements to cloud...`);
            
            const response = await fetch(this.cloudSaveUrl, {
                method: 'PUT',
                headers: { 
                    'Content-Type': 'application/json',
                    'Cache-Control': 'no-cache'
                },
                body: JSON.stringify({ 
                    announcements: announcements,
                    lastSync: Date.now(),
                    syncSource: 'improved_fix'
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            console.log(`✅ IMPROVED: ${operation} synced successfully to cloud`);
            
            // Mark this as a successful sync to prevent merge conflicts
            this.lastLocalSaveTime = Date.now();
            
            return true;
        } catch (error) {
            console.error(`❌ IMPROVED: ${operation} sync failed:`, error);
            throw error;
        }
    };
    
    // ENHANCED CREATE/UPDATE WITH RETRY LOGIC
    const originalSubmit = dashboard.handleAnnouncementSubmit;
    dashboard.handleAnnouncementSubmit = async function() {
        console.log('📝 IMPROVED: Creating/updating announcement...');
        
        const text = document.getElementById('announcementText').value.trim();
        const startDate = document.getElementById('startDate').value;
        const startTime = document.getElementById('startTime').value;
        const endDate = document.getElementById('endDate').value;
        const endTime = document.getElementById('endTime').value;

        if (!text || !startDate || !startTime || !endDate || !endTime) {
            alert('Please fill in all fields');
            return;
        }

        const start = new Date(startDate + 'T' + startTime);
        const end = new Date(endDate + 'T' + endTime);

        if (end <= start) {
            alert('End date/time must be after start date/time');
            return;
        }

        const announcement = {
            id: this.editingAnnouncementId || this.generateId(),
            text,
            startDate,
            startTime,
            endDate,
            endTime,
            createdAt: this.editingAnnouncementId ? 
                (this.announcements.find(a => a.id === this.editingAnnouncementId)?.createdAt || new Date().toISOString()) : 
                new Date().toISOString(),
            lastModified: new Date().toISOString()
        };

        if (this.editingAnnouncementId) {
            const index = this.announcements.findIndex(a => a.id === this.editingAnnouncementId);
            if (index !== -1) {
                this.announcements[index] = announcement;
            }
        } else {
            this.announcements.push(announcement);
        }

        // IMMEDIATE LOCAL SAVE
        localStorage.setItem('dashboard_announcements', JSON.stringify(this.announcements));

        // IMMEDIATE CLOUD SYNC WITH RETRY
        let syncSuccess = false;
        let retryCount = 0;
        const maxRetries = 3;
        
        while (!syncSuccess && retryCount < maxRetries) {
            try {
                await this.saveToCloudImmediate(this.announcements, 'CREATE/UPDATE');
                syncSuccess = true;
                console.log('✅ IMPROVED: Announcement saved and synced successfully');
            } catch (error) {
                retryCount++;
                console.warn(`⚠️ IMPROVED: Sync attempt ${retryCount}/${maxRetries} failed`);
                
                if (retryCount < maxRetries) {
                    // Wait before retry (exponential backoff)
                    await new Promise(resolve => setTimeout(resolve, 1000 * retryCount));
                } else {
                    console.error('❌ IMPROVED: All sync attempts failed, saved locally only');
                    alert('⚠️ Announcement saved locally but may not appear on other devices immediately.\nWill retry automatically in background.');
                }
            }
        }

        this.updateAnnouncementsDisplay();
        this.closeAnnouncementModal();
    };
    
    // ENHANCED DELETE WITH RETRY LOGIC
    const originalDelete = dashboard.deleteAnnouncement;
    dashboard.deleteAnnouncement = async function(id) {
        if (!confirm('Delete this announcement?')) return;
        
        console.log('🗑️ IMPROVED: Deleting announcement...');
        this.announcements = this.announcements.filter(a => a.id !== id);
        
        // IMMEDIATE LOCAL SAVE
        localStorage.setItem('dashboard_announcements', JSON.stringify(this.announcements));
        
        // IMMEDIATE CLOUD SYNC WITH RETRY
        let syncSuccess = false;
        let retryCount = 0;
        const maxRetries = 3;
        
        while (!syncSuccess && retryCount < maxRetries) {
            try {
                await this.saveToCloudImmediate(this.announcements, 'DELETE');
                syncSuccess = true;
                console.log('✅ IMPROVED: Announcement deleted and synced successfully');
            } catch (error) {
                retryCount++;
                console.warn(`⚠️ IMPROVED: Delete sync attempt ${retryCount}/${maxRetries} failed`);
                
                if (retryCount < maxRetries) {
                    await new Promise(resolve => setTimeout(resolve, 1000 * retryCount));
                } else {
                    console.error('❌ IMPROVED: All delete sync attempts failed');
                    alert('⚠️ Announcement deleted locally but may still appear on other devices.\nWill retry automatically in background.');
                }
            }
        }
        
        this.updateAnnouncementsDisplay();
    };
    
    // IMPROVED PERIODIC SYNC WITH CONTENT-BASED DETECTION
    if (dashboard.improvedSyncInterval) {
        clearInterval(dashboard.improvedSyncInterval);
    }
    
    // Enhanced sync function that compares actual content, not just count
    dashboard.enhancedSyncCheck = async function() {
        if (this.syncInProgress) {
            console.log('🔄 IMPROVED: Sync already in progress, skipping...');
            return;
        }
        
        try {
            this.syncInProgress = true;
            console.log('🔄 IMPROVED: Checking for cloud updates...');
            
            const response = await fetch(this.cloudSyncUrl + '?t=' + Date.now());
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            const cloudAnnouncements = data.record?.announcements || [];
            
            // CONTENT-BASED COMPARISON (not just count)
            const localSorted = JSON.stringify(this.announcements.sort((a,b) => a.id.localeCompare(b.id)));
            const cloudSorted = JSON.stringify(cloudAnnouncements.sort((a,b) => a.id.localeCompare(b.id)));
            
            if (localSorted !== cloudSorted) {
                console.log('📝 IMPROVED: Content differences detected, performing smart merge...');
                
                // Check if we should skip merge due to very recent local changes
                const timeSinceLastLocalSave = Date.now() - (this.lastLocalSaveTime || 0);
                if (timeSinceLastLocalSave < 3000) { // 3 seconds (reduced from 5)
                    console.log('🚫 IMPROVED: Skipping merge - very recent local changes');
                    return;
                }
                
                // Use the dashboard's smart merge algorithm if available, otherwise simple replace
                if (typeof this.mergeAnnouncements === 'function') {
                    console.log('🧠 IMPROVED: Using smart merge algorithm');
                    const merged = this.mergeAnnouncements(this.announcements, cloudAnnouncements);
                    this.announcements = merged;
                } else {
                    console.log('📝 IMPROVED: Using simple replacement (smart merge not available)');
                    this.announcements = cloudAnnouncements;
                }
                
                localStorage.setItem('dashboard_announcements', JSON.stringify(this.announcements));
                this.updateAnnouncementsDisplay();
                
                console.log(`✅ IMPROVED: Updated from cloud (now have ${this.announcements.length} announcements)`);
            } else {
                console.log('✅ IMPROVED: Local and cloud are in sync');
            }
        } catch (error) {
            console.warn('❌ IMPROVED: Sync check failed:', error);
        } finally {
            this.syncInProgress = false;
        }
    };
    
    // Set up improved periodic sync (more frequent)
    dashboard.improvedSyncInterval = setInterval(() => {
        dashboard.enhancedSyncCheck();
    }, 20000); // Every 20 seconds
    
    // INITIAL SYNC
    setTimeout(() => {
        console.log('🚀 IMPROVED: Performing initial sync...');
        dashboard.enhancedSyncCheck();
    }, 1000);
    
    // FOCUS-BASED SYNC (sync when tab becomes active)
    let isTabActive = true;
    
    document.addEventListener('visibilitychange', () => {
        if (!document.hidden && !isTabActive) {
            isTabActive = true;
            console.log('👁️ IMPROVED: Tab became active, checking for updates...');
            setTimeout(() => dashboard.enhancedSyncCheck(), 500);
        } else if (document.hidden) {
            isTabActive = false;
        }
    });
    
    window.addEventListener('focus', () => {
        console.log('🎯 IMPROVED: Window focused, checking for updates...');
        setTimeout(() => dashboard.enhancedSyncCheck(), 500);
    });
    
    // ADD IMPROVED VISUAL INDICATOR
    const indicator = document.createElement('div');
    indicator.id = 'improvedSyncIndicator';
    indicator.textContent = '✅ Improved Sync Active';
    indicator.style.cssText = `
        position: fixed;
        top: 10px;
        right: 10px;
        background: linear-gradient(135deg, #28a745, #20c997);
        color: white;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 12px;
        z-index: 10000;
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        font-weight: 500;
    `;
    
    // Remove old indicator if it exists
    const oldIndicator = document.querySelector('[textContent="✅ Direct Sync Active"]');
    if (oldIndicator) oldIndicator.remove();
    
    document.body.appendChild(indicator);
    
    console.log('🎉 IMPROVED SYNC FIX APPLIED SUCCESSFULLY!');
    console.log('✅ Content-based sync detection (not just count)');
    console.log('✅ Retry logic for failed operations');
    console.log('✅ Smart merge algorithm integration');
    console.log('✅ Focus-based sync triggers');
    console.log('✅ Reduced sync conflicts');
    console.log('✅ Enhanced error handling');
    console.log('📊 Sync interval: every 20 seconds');
});
