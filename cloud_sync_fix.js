// COMPREHENSIVE CLOUD SYNC FIX
// This script fixes the announcement sync issues by:
// 1. Reducing the local save protection window
// 2. Adding more frequent sync checks
// 3. Improving the merge logic
// 4. Adding better error handling

console.log('🔧 APPLYING COMPREHENSIVE CLOUD SYNC FIX...');

// Wait for dashboard to be ready
function waitForDashboard() {
    return new Promise((resolve) => {
        const checkInterval = setInterval(() => {
            if (window.dashboard && window.dashboard.cloudSyncEnabled) {
                clearInterval(checkInterval);
                resolve(window.dashboard);
            }
        }, 100);
    });
}

// Apply the fix
waitForDashboard().then(dashboard => {
    console.log('✅ Dashboard ready, applying cloud sync fixes...');
    
    // 1. REDUCE LOCAL SAVE PROTECTION WINDOW
    // Override the sync function to reduce the protection window from 5 seconds to 1 second
    const originalSyncFromCloud = dashboard.syncAnnouncementsFromCloud.bind(dashboard);
    dashboard.syncAnnouncementsFromCloud = async function() {
        if (!this.cloudSyncEnabled || this.syncInProgress) {
            return;
        }

        try {
            this.syncInProgress = true;
            console.log('🔄 ENHANCED: Checking for cloud updates...');
            
            const cloudData = await this.loadFromCloud();
            if (cloudData && Array.isArray(cloudData)) {
                // REDUCED protection window from 5000ms to 1000ms
                const timeSinceLastLocalSave = Date.now() - (this.lastLocalSaveTime || 0);
                if (timeSinceLastLocalSave < 1000) { // Changed from 5000 to 1000
                    console.log('🚫 ENHANCED: Skipping cloud merge - recent local changes detected (1s window)');
                    this.lastSyncTime = Date.now();
                    return;
                }
                
                // Enhanced merge with better logging
                const mergedAnnouncements = this.mergeAnnouncements(this.announcements, cloudData);
                const localDataStr = JSON.stringify(this.announcements.sort((a,b) => a.id.localeCompare(b.id)));
                const mergedDataStr = JSON.stringify(mergedAnnouncements.sort((a,b) => a.id.localeCompare(b.id)));
                
                if (localDataStr !== mergedDataStr) {
                    console.log('📝 ENHANCED: Applying cloud changes to local data');
                    console.log(`   Before: ${this.announcements.length} announcements`);
                    console.log(`   After: ${mergedAnnouncements.length} announcements`);
                    
                    this.announcements = mergedAnnouncements;
                    localStorage.setItem('dashboard_announcements', JSON.stringify(this.announcements));
                    this.updateAnnouncementsDisplay();
                    
                    // Force immediate display update
                    if (this.currentSlideIndex === this.announcementsSlideIndex) {
                        console.log('📺 ENHANCED: Updating announcement display immediately');
                        this.updateAnnouncementsDisplay();
                    }
                } else {
                    console.log('✅ ENHANCED: Announcements are up to date');
                }
                
                this.lastSyncTime = Date.now();
            }
        } catch (error) {
            console.warn('❌ ENHANCED: Background cloud sync failed:', error.message);
        } finally {
            this.syncInProgress = false;
        }
    };
    
    // 2. ENHANCED SAVE FUNCTION WITH IMMEDIATE CLOUD SYNC
    const originalSaveAnnouncements = dashboard.saveAnnouncements.bind(dashboard);
    dashboard.saveAnnouncements = async function() {
        console.log('💾 ENHANCED: Saving announcements with immediate cloud sync...');
        
        // Mark local save time
        this.lastLocalSaveTime = Date.now();
        
        // Save to localStorage immediately
        localStorage.setItem('dashboard_announcements', JSON.stringify(this.announcements));
        console.log('✅ ENHANCED: Saved to localStorage:', this.announcements.length, 'items');
        
        // IMMEDIATE cloud sync with retry logic
        if (this.cloudSyncEnabled && this.cloudSyncUrl) {
            let retryCount = 0;
            const maxRetries = 3;
            
            while (retryCount < maxRetries) {
                try {
                    console.log(`🔄 ENHANCED: Attempting cloud sync (attempt ${retryCount + 1}/${maxRetries})...`);
                    await this.saveToCloud(this.announcements);
                    console.log('✅ ENHANCED: Immediate cloud sync successful');
                    this.lastSyncTime = Date.now();
                    break;
                } catch (cloudError) {
                    retryCount++;
                    if (retryCount < maxRetries) {
                        console.warn(`⚠️ ENHANCED: Cloud sync attempt ${retryCount} failed, retrying...`);
                        await new Promise(resolve => setTimeout(resolve, 1000 * retryCount)); // Exponential backoff
                    } else {
                        console.error('❌ ENHANCED: All cloud sync attempts failed:', cloudError.message);
                    }
                }
            }
        }
        
        // Update display
        this.updateAnnouncementsDisplay();
    };
    
    // 3. MORE FREQUENT SYNC CHECKS
    // Clear any existing sync interval
    if (dashboard.cloudSyncInterval) {
        clearInterval(dashboard.cloudSyncInterval);
    }
    
    // Set up more frequent sync (every 5 seconds instead of 15)
    dashboard.cloudSyncInterval = setInterval(() => {
        console.log('⏰ ENHANCED: Periodic cloud sync check...');
        dashboard.syncAnnouncementsFromCloud();
    }, 5000); // Every 5 seconds
    
    // 4. ENHANCED ANNOUNCEMENT DISPLAY UPDATES
    // Clear any existing announcement update interval
    if (dashboard.announcementUpdateInterval) {
        clearInterval(dashboard.announcementUpdateInterval);
    }
    
    // More frequent display updates
    dashboard.announcementUpdateInterval = setInterval(() => {
        if (dashboard.currentSlideIndex === dashboard.announcementsSlideIndex) {
            console.log('📺 ENHANCED: Periodic announcement display update...');
            dashboard.updateAnnouncementsDisplay();
        }
    }, 3000); // Every 3 seconds when on announcement slide
    
    // 5. ENHANCED MERGE FUNCTION
    const originalMergeAnnouncements = dashboard.mergeAnnouncements.bind(dashboard);
    dashboard.mergeAnnouncements = function(localAnnouncements, cloudAnnouncements) {
        console.log('🔄 ENHANCED MERGE: Starting smart merge...');
        console.log(`   Local: ${localAnnouncements.length} announcements`);
        console.log(`   Cloud: ${cloudAnnouncements.length} announcements`);
        
        // Create a map of all announcements by ID
        const announcementMap = new Map();
        
        // Add local announcements
        localAnnouncements.forEach(ann => {
            if (!ann.lastModified) {
                ann.lastModified = ann.createdAt || new Date().toISOString();
            }
            announcementMap.set(ann.id, ann);
        });
        
        // Process cloud announcements
        cloudAnnouncements.forEach(ann => {
            if (ann.id && ann.text) {
                if (!ann.lastModified) {
                    ann.lastModified = ann.createdAt || new Date().toISOString();
                }
                
                const existingLocal = announcementMap.get(ann.id);
                if (!existingLocal) {
                    // New from cloud
                    console.log(`   📥 ENHANCED: Adding from cloud: ${ann.text.substring(0, 30)}...`);
                    announcementMap.set(ann.id, ann);
                } else {
                    // Exists in both - compare timestamps
                    const localTime = new Date(existingLocal.lastModified).getTime();
                    const cloudTime = new Date(ann.lastModified).getTime();
                    
                    if (cloudTime > localTime) {
                        console.log(`   🔄 ENHANCED: Updating from cloud: ${ann.text.substring(0, 30)}...`);
                        announcementMap.set(ann.id, ann);
                    } else {
                        console.log(`   ⏭️ ENHANCED: Keeping local version: ${existingLocal.text.substring(0, 30)}...`);
                    }
                }
            }
        });
        
        // Filter out expired announcements (cleanup)
        const now = new Date();
        const mergedAnnouncements = Array.from(announcementMap.values()).filter(ann => {
            const endDate = new Date(ann.endDate + 'T' + ann.endTime);
            const hoursSinceEnd = (now - endDate) / (1000 * 60 * 60);
            const shouldKeep = hoursSinceEnd < 24;
            
            if (!shouldKeep) {
                console.log(`   🧹 ENHANCED: Removing expired: ${ann.text.substring(0, 30)}...`);
            }
            
            return shouldKeep;
        });
        
        console.log(`   ✅ ENHANCED: Merge complete - ${mergedAnnouncements.length} final announcements`);
        return mergedAnnouncements;
    };
    
    // 6. IMMEDIATE INITIAL SYNC
    console.log('🚀 ENHANCED: Performing immediate initial sync...');
    setTimeout(() => {
        dashboard.syncAnnouncementsFromCloud();
    }, 500); // Immediate sync after 0.5 seconds
    
    // 7. ENHANCED ERROR HANDLING FOR CLOUD OPERATIONS
    const originalSaveToCloud = dashboard.saveToCloud.bind(dashboard);
    dashboard.saveToCloud = async function(announcements) {
        if (!this.cloudSyncUrl) {
            throw new Error('Cloud sync URL not configured');
        }

        const payload = { announcements: announcements };
        console.log('💾 ENHANCED: Saving to cloud:', announcements.length, 'announcements');
        
        const saveUrl = this.cloudSyncUrl.replace('/latest', '');
        console.log('🔗 ENHANCED: Save URL:', saveUrl);
        
        const response = await fetch(saveUrl, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                ...(this.cloudSyncKey && { 'X-Master-Key': this.cloudSyncKey })
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ ENHANCED: Cloud save failed:', response.status, response.statusText, errorText);
            throw new Error(`Cloud save failed: ${response.status} ${response.statusText} - ${errorText}`);
        }

        const result = await response.json();
        console.log('✅ ENHANCED: Cloud save successful:', result);
        return result;
    };
    
    console.log('🎉 ENHANCED CLOUD SYNC FIX APPLIED SUCCESSFULLY!');
    console.log('   • Reduced local save protection to 1 second');
    console.log('   • Increased sync frequency to every 5 seconds');
    console.log('   • Enhanced merge logic with better logging');
    console.log('   • Added retry logic for cloud saves');
    console.log('   • Improved error handling');
    console.log('   • More frequent display updates');
    
    // Test the fix
    console.log('🧪 ENHANCED: Testing sync after 2 seconds...');
    setTimeout(() => {
        dashboard.syncAnnouncementsFromCloud();
    }, 2000);
}); 