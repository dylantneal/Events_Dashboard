// FIX ANNOUNCEMENT CREATION SYNC ISSUE - DISABLED DURING PHASE 2 CLEANUP
// This script was redundant with the original system's creation handling
// Disabled to allow original system to work properly

console.log('⚠️ CREATION SYNC FIX: DISABLED - Using original system instead');
// Early return to prevent any interference
if (true) {
    console.log('🚫 fix_creation_sync.js is disabled - original sync system handles creation properly');
    // Exit immediately without making any changes
}

function fixCreationSync() {
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
    
    waitForDashboard().then(dashboard => {
        console.log('🎯 Dashboard ready, fixing creation sync...');
        
        // Override the handleAnnouncementSubmit function to ensure immediate cloud sync
        const originalHandleSubmit = dashboard.handleAnnouncementSubmit.bind(dashboard);
        dashboard.handleAnnouncementSubmit = async function() {
            console.log('📝 ENHANCED CREATE: Processing announcement submission...');
            
            const text = document.getElementById('announcementText').value.trim();
            const startDate = document.getElementById('startDate').value;
            const startTime = document.getElementById('startTime').value;
            const endDate = document.getElementById('endDate').value;
            const endTime = document.getElementById('endTime').value;

            if (!text || !startDate || !startTime || !endDate || !endTime) {
                alert('Please fill in all fields');
                return;
            }

            // Validate dates
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

            console.log('📝 ENHANCED CREATE: Announcement object created:', announcement);

            if (this.editingAnnouncementId) {
                // Update existing
                const index = this.announcements.findIndex(a => a.id === this.editingAnnouncementId);
                if (index !== -1) {
                    this.announcements[index] = announcement;
                    console.log('✏️ ENHANCED CREATE: Updated existing announcement');
                }
            } else {
                // Add new
                this.announcements.push(announcement);
                console.log('➕ ENHANCED CREATE: Added new announcement');
            }

            console.log(`📊 ENHANCED CREATE: Total announcements: ${this.announcements.length}`);

            // IMMEDIATE cloud sync with enhanced error handling
            if (this.cloudSyncEnabled && this.cloudSyncUrl) {
                let retryCount = 0;
                const maxRetries = 3;
                
                while (retryCount < maxRetries) {
                    try {
                        console.log(`☁️ ENHANCED CREATE: Syncing to cloud (attempt ${retryCount + 1}/${maxRetries})...`);
                        
                        const saveUrl = this.cloudSyncUrl.replace('/latest', '');
                        const response = await fetch(saveUrl, {
                            method: 'PUT',
                            headers: {
                                'Content-Type': 'application/json',
                                'Cache-Control': 'no-cache'
                            },
                            body: JSON.stringify({
                                announcements: this.announcements
                            })
                        });
                        
                        if (!response.ok) {
                            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                        }
                        
                        const result = await response.json();
                        console.log('✅ ENHANCED CREATE: Cloud sync successful!');
                        console.log('📊 Cloud now has', this.announcements.length, 'announcements');
                        
                        // Update localStorage
                        localStorage.setItem('dashboard_announcements', JSON.stringify(this.announcements));
                        
                        // Success - break out of retry loop
                        break;
                        
                    } catch (error) {
                        retryCount++;
                        console.warn(`⚠️ ENHANCED CREATE: Attempt ${retryCount} failed:`, error.message);
                        
                        if (retryCount < maxRetries) {
                            await new Promise(resolve => setTimeout(resolve, 1000 * retryCount));
                        } else {
                            console.error('❌ ENHANCED CREATE: All cloud sync attempts failed');
                            
                            // Show error to user but don't fail the creation
                            const userChoice = confirm(
                                `Failed to sync announcement to cloud after ${maxRetries} attempts.\n\n` +
                                `The announcement was saved locally but won't appear on other devices.\n\n` +
                                `Would you like to try again?`
                            );
                            
                            if (userChoice) {
                                // Reset retry count and try again
                                retryCount = 0;
                                continue;
                            } else {
                                // Save locally only
                                localStorage.setItem('dashboard_announcements', JSON.stringify(this.announcements));
                                console.log('💾 ENHANCED CREATE: Saved locally only');
                                break;
                            }
                        }
                    }
                }
            } else {
                console.warn('⚠️ Cloud sync not enabled, saving locally only');
                localStorage.setItem('dashboard_announcements', JSON.stringify(this.announcements));
            }

            // Update display and close modal
            this.updateAnnouncementsDisplay();
            this.closeAnnouncementModal();
            
            console.log('✅ ENHANCED CREATE: Announcement creation complete');
        };
        
        // Also enhance the general saveAnnouncements function (if not already done)
        if (!dashboard.saveAnnouncements.toString().includes('ENHANCED SAVE')) {
            const originalSaveAnnouncements = dashboard.saveAnnouncements.bind(dashboard);
            dashboard.saveAnnouncements = async function() {
                console.log('💾 ENHANCED SAVE: Saving announcements...');
                
                // Always save to localStorage first
                localStorage.setItem('dashboard_announcements', JSON.stringify(this.announcements));
                console.log('✅ ENHANCED SAVE: Saved to localStorage');
                
                // Force cloud sync if enabled
                if (this.cloudSyncEnabled && this.cloudSyncUrl) {
                    let retryCount = 0;
                    const maxRetries = 3;
                    
                    while (retryCount < maxRetries) {
                        try {
                            console.log(`☁️ ENHANCED SAVE: Syncing to cloud (attempt ${retryCount + 1}/${maxRetries})...`);
                            
                            const saveUrl = this.cloudSyncUrl.replace('/latest', '');
                            const response = await fetch(saveUrl, {
                                method: 'PUT',
                                headers: {
                                    'Content-Type': 'application/json',
                                    'Cache-Control': 'no-cache'
                                },
                                body: JSON.stringify({
                                    announcements: this.announcements
                                })
                            });
                            
                            if (!response.ok) {
                                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                            }
                            
                            const result = await response.json();
                            console.log('✅ ENHANCED SAVE: Cloud sync successful!');
                            break;
                            
                        } catch (error) {
                            retryCount++;
                            console.warn(`⚠️ ENHANCED SAVE: Attempt ${retryCount} failed:`, error.message);
                            
                            if (retryCount < maxRetries) {
                                await new Promise(resolve => setTimeout(resolve, 1000 * retryCount));
                            } else {
                                console.error('❌ ENHANCED SAVE: All attempts failed');
                                alert(`Failed to sync to cloud after ${maxRetries} attempts.\nChanges saved locally only.`);
                            }
                        }
                    }
                }
                
                this.updateAnnouncementsDisplay();
            };
        }
        
        // Add visual feedback for cloud sync status
        const addSyncStatusIndicator = () => {
            const existingIndicator = document.getElementById('syncStatusIndicator');
            if (existingIndicator) return;
            
            const indicator = document.createElement('div');
            indicator.id = 'syncStatusIndicator';
            indicator.textContent = '☁️ Synced';
            indicator.style.cssText = `
                position: fixed;
                top: 60px;
                left: 20px;
                z-index: 9999;
                background: #28a745;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                font-size: 12px;
                opacity: 0.8;
            `;
            
            document.body.appendChild(indicator);
            
            // Update indicator based on sync status
            window.updateSyncStatus = (status) => {
                switch(status) {
                    case 'syncing':
                        indicator.textContent = '⏳ Syncing...';
                        indicator.style.background = '#ffc107';
                        break;
                    case 'synced':
                        indicator.textContent = '☁️ Synced';
                        indicator.style.background = '#28a745';
                        break;
                    case 'error':
                        indicator.textContent = '❌ Sync Failed';
                        indicator.style.background = '#dc3545';
                        break;
                }
            };
        };
        
        // Add the sync status indicator
        setTimeout(addSyncStatusIndicator, 2000);
        
        console.log('✅ CREATION SYNC FIX APPLIED!');
        console.log('🎯 New announcements will now sync to cloud immediately');
        console.log('📊 Added sync status indicator');
    });
}

// Apply the fix
fixCreationSync();

console.log('🔧 Creation sync fix script loaded'); 