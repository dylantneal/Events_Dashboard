// ✅ ORIGINAL ANNOUNCEMENT SYNC SYSTEM BACKUP
// This is the WORKING original system from index.html before any fix scripts
// Created during Phase 1 cleanup - DO NOT MODIFY

// This system includes:
// - Smart conflict resolution using lastModified timestamps
// - Content-based sync detection (not count-based)
// - 5-second protection against merge during local changes
// - Proper error handling and fallbacks
// - Configurable sync intervals (60s default)

const ORIGINAL_ANNOUNCEMENT_FUNCTIONS = {

    // ==================== ANNOUNCEMENTS LOADING ====================
    
    async loadAnnouncements() {
        try {
            console.log('🔄 LOADING ANNOUNCEMENTS...');
            console.log('  Cloud sync enabled:', this.cloudSyncEnabled);
            console.log('  Cloud URL:', this.cloudSyncUrl);
            
            // Try cloud sync first if enabled
            if (this.cloudSyncEnabled && this.cloudSyncUrl) {
                console.log('🌐 Attempting to load announcements from cloud...');
                try {
                    const cloudData = await this.loadFromCloud();
                    if (cloudData && Array.isArray(cloudData)) {
                        this.announcements = cloudData;
                        // Also save to localStorage as backup
                        localStorage.setItem('dashboard_announcements', JSON.stringify(this.announcements));
                        console.log('✅ LOADED FROM CLOUD:', this.announcements.length, 'items');
                        
                        // Immediately check which ones are active
                        const now = new Date();
                        const activeCount = this.announcements.filter(ann => {
                            const startDate = new Date(ann.startDate + 'T' + ann.startTime);
                            const endDate = new Date(ann.endDate + 'T' + ann.endTime);
                            return now >= startDate && now <= endDate;
                        }).length;
                        console.log('📊 ACTIVE ANNOUNCEMENTS RIGHT NOW:', activeCount);
                        
                        return;
                    } else {
                        console.warn('⚠️ Cloud returned invalid data format:', cloudData);
                    }
                } catch (cloudError) {
                    console.error('❌ Cloud sync failed:', cloudError.message);
                    console.error('   Full error:', cloudError);
                }
            } else {
                console.log('⚠️ Cloud sync not enabled or URL missing');
            }
            
            // Fallback to localStorage
            console.log('📱 Falling back to localStorage...');
            const stored = localStorage.getItem('dashboard_announcements');
            this.announcements = stored ? JSON.parse(stored) : [];
            console.log('📱 Loaded from localStorage:', this.announcements.length, 'items');
            
            // If we have no announcements and cloud sync is enabled, try one more time
            if (this.announcements.length === 0 && this.cloudSyncEnabled && this.cloudSyncUrl) {
                console.log('🔄 No local data, retrying cloud sync...');
                setTimeout(async () => {
                    try {
                        const retryData = await this.loadFromCloud();
                        if (retryData && Array.isArray(retryData) && retryData.length > 0) {
                            console.log('✅ RETRY SUCCESS: Got', retryData.length, 'announcements');
                            this.announcements = retryData;
                            localStorage.setItem('dashboard_announcements', JSON.stringify(this.announcements));
                            this.updateAnnouncementsDisplay();
                        }
                    } catch (retryError) {
                        console.error('❌ Retry also failed:', retryError.message);
                    }
                }, 2000);
            }
            
            // Sync status info
            if (this.cloudSyncEnabled) {
                console.log('✅ Cloud sync is enabled - announcements will sync across devices');
            } else if (window.DASHBOARD_CONFIG?.isProduction) {
                console.log('📄 Running on GitHub Pages - announcements are stored locally per device');
                console.log('💡 Use Ctrl+E to export and Ctrl+I to import announcements between devices');
                console.log('☁️ Enable cloud sync in config.js for automatic multi-device sync');
            }
        } catch (error) {
            console.error('💥 Error loading announcements:', error);
            this.announcements = [];
        }
    },

    // ==================== ANNOUNCEMENTS SAVING ====================

    async saveAnnouncements() {
        try {
            // Track when we make local changes
            this.lastLocalSaveTime = Date.now();
            
            // Always save to localStorage first (immediate backup)
            localStorage.setItem('dashboard_announcements', JSON.stringify(this.announcements));
            console.log('Saved announcements to localStorage:', this.announcements.length, 'items');
            
            // Also sync to cloud if enabled
            if (this.cloudSyncEnabled && this.cloudSyncUrl && !this.syncInProgress) {
                this.syncInProgress = true;
                try {
                    await this.saveToCloud(this.announcements);
                    console.log('✓ Synced announcements to cloud');
                    this.lastSyncTime = Date.now();
                } catch (cloudError) {
                    console.warn('Cloud sync failed during save:', cloudError.message);
                } finally {
                    this.syncInProgress = false;
                }
            }
        } catch (error) {
            console.error('Error saving announcements:', error);
        }
    },

    // ==================== CLOUD SYNC FUNCTIONALITY ====================

    async loadFromCloud() {
        if (!this.cloudSyncUrl) {
            throw new Error('Cloud sync URL not configured');
        }

        console.log('🌐 LOADING FROM CLOUD:', this.cloudSyncUrl);
        
        const response = await fetch(this.cloudSyncUrl, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                ...(this.cloudSyncKey && { 'X-Master-Key': this.cloudSyncKey })
            }
        });

        console.log('📡 Cloud response status:', response.status, response.statusText);
        
        if (!response.ok) {
            throw new Error(`Cloud fetch failed: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        console.log('📦 Raw cloud data structure:', Object.keys(data));
        console.log('📦 Full cloud data:', JSON.stringify(data, null, 2));
        
        // Handle different cloud storage formats
        if (data.record && data.record.announcements && Array.isArray(data.record.announcements)) {
            console.log('✅ Using JSONBin format with wrapper, found', data.record.announcements.length, 'announcements');
            return data.record.announcements; // JSONBin format with wrapper
        } else if (data.record && Array.isArray(data.record)) {
            console.log('✅ Using JSONBin format direct array, found', data.record.length, 'announcements');
            return data.record; // JSONBin format direct array
        } else if (Array.isArray(data)) {
            console.log('✅ Using direct array format, found', data.length, 'announcements');
            return data; // Direct array format
        } else if (data.announcements && Array.isArray(data.announcements)) {
            console.log('✅ Using wrapped format, found', data.announcements.length, 'announcements');
            return data.announcements; // Wrapped format
        }
        
        console.error('❌ Invalid cloud data format. Data structure:', data);
        throw new Error('Invalid cloud data format');
    },

    async saveToCloud(announcements) {
        if (!this.cloudSyncUrl) {
            throw new Error('Cloud sync URL not configured');
        }

        const payload = { announcements: announcements };
        console.log('Saving to cloud:', announcements.length, 'announcements');
        
        // Remove /latest for PUT requests to JSONBin
        const saveUrl = this.cloudSyncUrl.replace('/latest', '');
        console.log('💾 SAVING TO CLOUD:');
        console.log('  Original URL:', this.cloudSyncUrl);
        console.log('  Save URL:', saveUrl);
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
            console.error('Cloud save failed:', response.status, response.statusText, errorText);
            throw new Error(`Cloud save failed: ${response.status} ${response.statusText} - ${errorText}`);
        }

        const result = await response.json();
        console.log('✓ Cloud save successful:', result);
        return result;
    },

    async syncAnnouncementsFromCloud() {
        if (!this.cloudSyncEnabled || this.syncInProgress) {
            return;
        }

        try {
            this.syncInProgress = true;
            console.log('Checking for cloud updates...');
            
            const cloudData = await this.loadFromCloud();
            if (cloudData && Array.isArray(cloudData)) {
                // Check if we should skip merge due to recent local changes
                const timeSinceLastLocalSave = Date.now() - (this.lastLocalSaveTime || 0);
                if (timeSinceLastLocalSave < 5000) { // 5 seconds
                    console.log('🚫 Skipping cloud merge - recent local changes detected');
                    this.lastSyncTime = Date.now();
                    return;
                }
                
                // Smart merge instead of overwrite
                const mergedAnnouncements = this.mergeAnnouncements(this.announcements, cloudData);
                const localDataStr = JSON.stringify(this.announcements.sort((a,b) => a.id.localeCompare(b.id)));
                const mergedDataStr = JSON.stringify(mergedAnnouncements.sort((a,b) => a.id.localeCompare(b.id)));
                
                if (localDataStr !== mergedDataStr) {
                    console.log('📝 Applying cloud changes to local data');
                    this.announcements = mergedAnnouncements;
                    localStorage.setItem('dashboard_announcements', JSON.stringify(this.announcements));
                    this.updateAnnouncementsDisplay();
                } else {
                    console.log('Announcements are up to date');
                }
                
                this.lastSyncTime = Date.now();
            }
        } catch (error) {
            console.warn('Background cloud sync failed:', error.message);
        } finally {
            this.syncInProgress = false;
        }
    },

    // Smart merge function that combines local and cloud announcements with proper deletion handling
    mergeAnnouncements(localAnnouncements, cloudAnnouncements) {
        // Create a map of all announcements by ID, tracking last modified time
        const announcementMap = new Map();
        
        // Add local announcements with modification tracking
        localAnnouncements.forEach(ann => {
            // Ensure lastModified exists (for backward compatibility)
            if (!ann.lastModified) {
                ann.lastModified = ann.createdAt || new Date().toISOString();
            }
            announcementMap.set(ann.id, ann);
        });
        
        // Add/update with cloud announcements, but respect lastModified timestamps
        cloudAnnouncements.forEach(ann => {
            if (ann.id && ann.text) { // Basic validation
                // Ensure lastModified exists (for backward compatibility)
                if (!ann.lastModified) {
                    ann.lastModified = ann.createdAt || new Date().toISOString();
                }
                
                const existingLocal = announcementMap.get(ann.id);
                if (!existingLocal) {
                    // New announcement from cloud, add it
                    announcementMap.set(ann.id, ann);
                } else {
                    // Announcement exists both locally and in cloud, use the most recent
                    const localModified = new Date(existingLocal.lastModified);
                    const cloudModified = new Date(ann.lastModified);
                    
                    if (cloudModified > localModified) {
                        // Cloud version is newer, use it
                        announcementMap.set(ann.id, ann);
                    }
                    // Otherwise keep local version (it's newer or same age)
                }
            }
        });
        
        // Convert back to array and filter out invalid/expired announcements
        const now = new Date();
        const mergedAnnouncements = Array.from(announcementMap.values()).filter(ann => {
            // Remove announcements that are more than 24 hours past their end time (cleanup)
            const endDate = new Date(ann.endDate + 'T' + ann.endTime);
            const hoursSinceEnd = (now - endDate) / (1000 * 60 * 60);
            return hoursSinceEnd < 24; // Keep announcements that ended less than 24 hours ago
        });
        
        console.log(`📊 MERGE SUMMARY:`);
        console.log(`  Local: ${localAnnouncements.length} announcements`);
        console.log(`  Cloud: ${cloudAnnouncements.length} announcements`);
        console.log(`  Final: ${mergedAnnouncements.length} announcements`);
        console.log('  Strategy: Preferring most recently modified versions');
        
        // Debug: Show which announcements are in each set
        const localIds = new Set(localAnnouncements.map(a => a.id));
        const cloudIds = new Set(cloudAnnouncements.map(a => a.id));
        const finalIds = new Set(mergedAnnouncements.map(a => a.id));
        
        const onlyLocal = [...localIds].filter(id => !cloudIds.has(id));
        const onlyCloud = [...cloudIds].filter(id => !localIds.has(id));
        const bothSets = [...localIds].filter(id => cloudIds.has(id));
        
        if (onlyLocal.length > 0) console.log(`  🏠 Local only: ${onlyLocal.length} announcements`);
        if (onlyCloud.length > 0) console.log(`  ☁️ Cloud only: ${onlyCloud.length} announcements`);
        if (bothSets.length > 0) console.log(`  🔄 In both: ${bothSets.length} announcements`);
        
        return mergedAnnouncements;
    },

    startCloudSync() {
        if (!this.cloudSyncEnabled) {
            return;
        }

        console.log('Starting automatic cloud sync...');
        
        // Use configurable sync interval (default: 1 minute)
        const syncInterval = window.DASHBOARD_CONFIG?.cloudSync?.syncInterval || 60000;
        setInterval(() => {
            this.syncAnnouncementsFromCloud();
        }, syncInterval);
        
        // Initial sync after a short delay
        setTimeout(() => {
            this.syncAnnouncementsFromCloud();
        }, 2000);
    }
};

// Export for reference
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ORIGINAL_ANNOUNCEMENT_FUNCTIONS;
}

console.log('✅ Original announcement system backup loaded for reference');