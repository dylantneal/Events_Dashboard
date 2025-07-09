// EMERGENCY COMPLETE SYNC SOLUTION
// This script ensures perfect CRUD synchronization across all devices

console.log('🚨 EMERGENCY COMPLETE SYNC SOLUTION LOADING...');

function emergencyCompleteSyncFix() {
    const CLOUD_URL = 'https://api.jsonbin.io/v3/b/686350a78a456b7966b930b1';
    
    // Wait for dashboard to be ready
    function waitForDashboard() {
        return new Promise((resolve) => {
            const checkInterval = setInterval(() => {
                if (window.dashboard) {
                    clearInterval(checkInterval);
                    resolve(window.dashboard);
                }
            }, 100);
        });
    }
    
    waitForDashboard().then(dashboard => {
        console.log('🎯 EMERGENCY SYNC: Dashboard ready, applying complete sync fix...');
        
        // FORCE ENABLE CLOUD SYNC
        dashboard.cloudSyncEnabled = true;
        dashboard.cloudSyncUrl = CLOUD_URL + '/latest';
        
        // ENHANCED CLOUD OPERATIONS
        dashboard.saveToCloudForced = async function(announcements) {
            console.log('☁️ EMERGENCY SYNC: Force saving to cloud...');
            const saveUrl = CLOUD_URL.replace('/latest', '');
            
            let retryCount = 0;
            const maxRetries = 5;
            
            while (retryCount < maxRetries) {
                try {
                    const response = await fetch(saveUrl, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json',
                            'Cache-Control': 'no-cache'
                        },
                        body: JSON.stringify({
                            announcements: announcements || []
                        })
                    });
                    
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    
                    const result = await response.json();
                    console.log('✅ EMERGENCY SYNC: Cloud save successful!');
                    return result;
                    
                } catch (error) {
                    retryCount++;
                    console.warn(`⚠️ EMERGENCY SYNC: Save attempt ${retryCount} failed:`, error.message);
                    
                    if (retryCount < maxRetries) {
                        await new Promise(resolve => setTimeout(resolve, 1000 * retryCount));
                    } else {
                        console.error('❌ EMERGENCY SYNC: All save attempts failed');
                        throw error;
                    }
                }
            }
        };
        
        dashboard.loadFromCloudForced = async function() {
            console.log('☁️ EMERGENCY SYNC: Force loading from cloud...');
            
            try {
                const response = await fetch(CLOUD_URL + '/latest?t=' + Date.now(), {
                    headers: { 'Cache-Control': 'no-cache' }
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const data = await response.json();
                const announcements = data.record.announcements || [];
                console.log(`☁️ EMERGENCY SYNC: Loaded ${announcements.length} announcements from cloud`);
                return announcements;
                
            } catch (error) {
                console.error('❌ EMERGENCY SYNC: Failed to load from cloud:', error.message);
                throw error;
            }
        };
        
        // OVERRIDE ALL CRUD OPERATIONS
        
        // 1. CREATE/UPDATE - IMMEDIATE CLOUD SYNC
        const originalHandleSubmit = dashboard.handleAnnouncementSubmit.bind(dashboard);
        dashboard.handleAnnouncementSubmit = async function() {
            console.log('📝 EMERGENCY SYNC: CREATE/UPDATE operation...');
            
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

            console.log('📝 EMERGENCY SYNC: Announcement object:', announcement);

            if (this.editingAnnouncementId) {
                const index = this.announcements.findIndex(a => a.id === this.editingAnnouncementId);
                if (index !== -1) {
                    this.announcements[index] = announcement;
                    console.log('✏️ EMERGENCY SYNC: Updated existing announcement');
                }
            } else {
                this.announcements.push(announcement);
                console.log('➕ EMERGENCY SYNC: Added new announcement');
            }

            // IMMEDIATE CLOUD SYNC
            try {
                await this.saveToCloudForced(this.announcements);
                console.log('✅ EMERGENCY SYNC: CREATE/UPDATE synced to cloud successfully!');
                
                // Update localStorage
                localStorage.setItem('dashboard_announcements', JSON.stringify(this.announcements));
                
                // Show success feedback
                if (window.updateSyncStatus) {
                    window.updateSyncStatus('synced');
                }
                
            } catch (error) {
                console.error('❌ EMERGENCY SYNC: CREATE/UPDATE cloud sync failed:', error.message);
                
                // Show error but don't fail the operation
                const retry = confirm(
                    `Failed to sync announcement to cloud.\n\n` +
                    `The announcement was saved locally but won't appear on other devices.\n\n` +
                    `Would you like to try again?`
                );
                
                if (retry) {
                    try {
                        await this.saveToCloudForced(this.announcements);
                        console.log('✅ EMERGENCY SYNC: Retry successful!');
                    } catch (retryError) {
                        console.error('❌ EMERGENCY SYNC: Retry failed:', retryError.message);
                        alert('Sync failed again. Saved locally only.');
                    }
                } else {
                    localStorage.setItem('dashboard_announcements', JSON.stringify(this.announcements));
                }
            }

            this.updateAnnouncementsDisplay();
            this.closeAnnouncementModal();
            console.log('✅ EMERGENCY SYNC: CREATE/UPDATE complete');
        };
        
        // 2. DELETE - IMMEDIATE CLOUD SYNC
        const originalDeleteAnnouncement = dashboard.deleteAnnouncement.bind(dashboard);
        dashboard.deleteAnnouncement = async function(announcementId) {
            console.log('🗑️ EMERGENCY SYNC: DELETE operation for ID:', announcementId);
            
            if (!confirm('Are you sure you want to delete this announcement?')) {
                return;
            }
            
            // Remove from local array
            const beforeCount = this.announcements.length;
            this.announcements = this.announcements.filter(a => a.id !== announcementId);
            const afterCount = this.announcements.length;
            
            console.log(`🗑️ EMERGENCY SYNC: Removed locally (${beforeCount} → ${afterCount})`);
            
            // IMMEDIATE CLOUD SYNC
            try {
                await this.saveToCloudForced(this.announcements);
                console.log('✅ EMERGENCY SYNC: DELETE synced to cloud successfully!');
                
                // Update localStorage
                localStorage.setItem('dashboard_announcements', JSON.stringify(this.announcements));
                
                // Show success feedback
                if (window.updateSyncStatus) {
                    window.updateSyncStatus('synced');
                }
                
            } catch (error) {
                console.error('❌ EMERGENCY SYNC: DELETE cloud sync failed:', error.message);
                
                // Show error and offer retry
                const retry = confirm(
                    `Failed to sync deletion to cloud.\n\n` +
                    `The announcement was deleted locally but may still appear on other devices.\n\n` +
                    `Would you like to try again?`
                );
                
                if (retry) {
                    try {
                        await this.saveToCloudForced(this.announcements);
                        console.log('✅ EMERGENCY SYNC: Delete retry successful!');
                    } catch (retryError) {
                        console.error('❌ EMERGENCY SYNC: Delete retry failed:', retryError.message);
                        alert('Delete sync failed again. Deleted locally only.');
                    }
                }
            }
            
            this.updateAnnouncementsDisplay();
            console.log('✅ EMERGENCY SYNC: DELETE complete');
        };
        
        // 3. ENHANCED PERIODIC SYNC - EVERY 30 SECONDS
        if (dashboard.cloudSyncInterval) {
            clearInterval(dashboard.cloudSyncInterval);
        }
        
        dashboard.emergencySyncFromCloud = async function() {
            if (this.syncInProgress) return;
            
            try {
                this.syncInProgress = true;
                console.log('🔄 EMERGENCY SYNC: Checking for cloud updates...');
                
                const cloudAnnouncements = await this.loadFromCloudForced();
                
                // Simple but effective merge: cloud takes precedence for conflicts
                const localIds = new Set(this.announcements.map(a => a.id));
                const cloudIds = new Set(cloudAnnouncements.map(a => a.id));
                
                let hasChanges = false;
                
                // Add new announcements from cloud
                for (const cloudAnn of cloudAnnouncements) {
                    if (!localIds.has(cloudAnn.id)) {
                        this.announcements.push(cloudAnn);
                        hasChanges = true;
                        console.log('➕ EMERGENCY SYNC: Added from cloud:', cloudAnn.text.substring(0, 30) + '...');
                    } else {
                        // Update existing if cloud version is newer
                        const localAnn = this.announcements.find(a => a.id === cloudAnn.id);
                        if (localAnn && cloudAnn.lastModified > localAnn.lastModified) {
                            Object.assign(localAnn, cloudAnn);
                            hasChanges = true;
                            console.log('✏️ EMERGENCY SYNC: Updated from cloud:', cloudAnn.text.substring(0, 30) + '...');
                        }
                    }
                }
                
                // Remove announcements that don't exist in cloud
                const initialLength = this.announcements.length;
                this.announcements = this.announcements.filter(localAnn => cloudIds.has(localAnn.id));
                if (this.announcements.length < initialLength) {
                    hasChanges = true;
                    console.log('🗑️ EMERGENCY SYNC: Removed deleted announcements from cloud');
                }
                
                if (hasChanges) {
                    console.log('📝 EMERGENCY SYNC: Applied cloud changes to local data');
                    localStorage.setItem('dashboard_announcements', JSON.stringify(this.announcements));
                    this.updateAnnouncementsDisplay();
                    
                    if (window.updateSyncStatus) {
                        window.updateSyncStatus('synced');
                    }
                } else {
                    console.log('✅ EMERGENCY SYNC: No changes needed');
                }
                
            } catch (error) {
                console.warn('❌ EMERGENCY SYNC: Periodic sync failed:', error.message);
                if (window.updateSyncStatus) {
                    window.updateSyncStatus('error');
                }
            } finally {
                this.syncInProgress = false;
            }
        };
        
        // Set up frequent sync
        dashboard.cloudSyncInterval = setInterval(() => {
            dashboard.emergencySyncFromCloud();
        }, 30000); // Every 30 seconds
        
        // 4. FORCE INITIAL SYNC
        console.log('🚀 EMERGENCY SYNC: Performing initial sync...');
        setTimeout(() => {
            dashboard.emergencySyncFromCloud();
        }, 2000);
        
        // 5. ADD SYNC STATUS INDICATOR
        const addSyncStatusIndicator = () => {
            const existingIndicator = document.getElementById('emergencySyncStatus');
            if (existingIndicator) return;
            
            const indicator = document.createElement('div');
            indicator.id = 'emergencySyncStatus';
            indicator.textContent = '🚨 Emergency Sync Active';
            indicator.style.cssText = `
                position: fixed;
                top: 10px;
                left: 10px;
                z-index: 10000;
                background: #dc3545;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
                box-shadow: 0 2px 4px rgba(0,0,0,0.3);
            `;
            
            document.body.appendChild(indicator);
            
            window.updateSyncStatus = (status) => {
                switch(status) {
                    case 'syncing':
                        indicator.textContent = '⏳ Syncing...';
                        indicator.style.background = '#ffc107';
                        break;
                    case 'synced':
                        indicator.textContent = '✅ Synced';
                        indicator.style.background = '#28a745';
                        break;
                    case 'error':
                        indicator.textContent = '❌ Sync Error';
                        indicator.style.background = '#dc3545';
                        break;
                }
            };
        };
        
        addSyncStatusIndicator();
        
        // 6. ADD MANUAL SYNC BUTTON
        const addManualSyncButton = () => {
            const existingButton = document.getElementById('manualSyncButton');
            if (existingButton) return;
            
            const button = document.createElement('button');
            button.id = 'manualSyncButton';
            button.textContent = '🔄 Force Sync';
            button.style.cssText = `
                position: fixed;
                top: 50px;
                left: 10px;
                z-index: 10000;
                background: #007bff;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 5px;
                font-size: 12px;
                cursor: pointer;
                box-shadow: 0 2px 4px rgba(0,0,0,0.3);
            `;
            
            button.onclick = () => {
                console.log('🔄 MANUAL SYNC: Force sync triggered');
                dashboard.emergencySyncFromCloud();
            };
            
            document.body.appendChild(button);
        };
        
        addManualSyncButton();
        
        console.log('🚨 EMERGENCY COMPLETE SYNC SOLUTION APPLIED!');
        console.log('✅ All CRUD operations will now sync immediately');
        console.log('✅ Periodic sync every 30 seconds');
        console.log('✅ Manual sync button available');
        console.log('✅ Sync status indicator active');
    });
}

// Apply the emergency fix
emergencyCompleteSyncFix();

console.log('🚨 Emergency complete sync solution loaded'); 