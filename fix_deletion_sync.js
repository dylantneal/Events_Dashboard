// FIX CLOUD SYNC DELETION ISSUE
// This script fixes the problem where deletions don't sync to the cloud

console.log('🔧 FIXING CLOUD SYNC DELETION ISSUE...');

function fixDeletionSync() {
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
        console.log('🎯 Dashboard ready, fixing deletion sync...');
        
        // Override the deleteAnnouncement function to ensure cloud sync
        const originalDeleteAnnouncement = dashboard.deleteAnnouncement.bind(dashboard);
        dashboard.deleteAnnouncement = async function(announcementId) {
            if (confirm('Are you sure you want to delete this announcement?')) {
                console.log(`🗑️ ENHANCED DELETE: Deleting announcement ${announcementId}`);
                console.log(`   Before deletion: ${this.announcements.length} announcements`);
                
                // Remove from local array
                this.announcements = this.announcements.filter(a => a.id !== announcementId);
                console.log(`   After deletion: ${this.announcements.length} announcements`);
                
                // IMMEDIATE cloud sync with enhanced error handling
                if (this.cloudSyncEnabled && this.cloudSyncUrl) {
                    try {
                        console.log('☁️ ENHANCED DELETE: Syncing deletion to cloud...');
                        
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
                            throw new Error(`Cloud sync failed: ${response.status} ${response.statusText}`);
                        }
                        
                        const result = await response.json();
                        console.log('✅ ENHANCED DELETE: Cloud sync successful!');
                        console.log('📊 Cloud now has', this.announcements.length, 'announcements');
                        
                        // Update localStorage
                        localStorage.setItem('dashboard_announcements', JSON.stringify(this.announcements));
                        
                    } catch (error) {
                        console.error('❌ ENHANCED DELETE: Cloud sync failed:', error);
                        
                        // Show user error and ask if they want to retry
                        const retry = confirm(`Cloud sync failed: ${error.message}\n\nWould you like to retry?`);
                        if (retry) {
                            // Retry the deletion
                            setTimeout(() => {
                                this.deleteAnnouncement(announcementId);
                            }, 1000);
                            return;
                        }
                    }
                } else {
                    console.warn('⚠️ Cloud sync not enabled, deletion only local');
                    localStorage.setItem('dashboard_announcements', JSON.stringify(this.announcements));
                }
                
                // Update display
                this.updateAnnouncementsDisplay();
                console.log(`✅ ENHANCED DELETE: Deletion complete`);
            }
        };
        
        // Override the saveAnnouncements function to ensure proper cloud sync
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
        
        // Add a manual sync button to the dashboard
        const addManualSyncButton = () => {
            const existingButton = document.getElementById('manualSyncButton');
            if (existingButton) return;
            
            const button = document.createElement('button');
            button.id = 'manualSyncButton';
            button.textContent = '🔄 Force Sync';
            button.style.cssText = `
                position: fixed;
                top: 20px;
                left: 20px;
                z-index: 9999;
                background: #007bff;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 14px;
            `;
            
            button.onclick = async () => {
                console.log('🔄 Manual sync triggered...');
                button.textContent = '⏳ Syncing...';
                button.disabled = true;
                
                try {
                    await dashboard.saveAnnouncements();
                    button.textContent = '✅ Synced!';
                    setTimeout(() => {
                        button.textContent = '🔄 Force Sync';
                        button.disabled = false;
                    }, 2000);
                } catch (error) {
                    button.textContent = '❌ Failed';
                    setTimeout(() => {
                        button.textContent = '🔄 Force Sync';
                        button.disabled = false;
                    }, 2000);
                }
            };
            
            document.body.appendChild(button);
        };
        
        // Add the manual sync button after a short delay
        setTimeout(addManualSyncButton, 2000);
        
        console.log('✅ DELETION SYNC FIX APPLIED!');
        console.log('🎯 Deletions will now sync to cloud immediately');
        console.log('🔄 Manual sync button added to top-left corner');
    });
}

// Apply the fix
fixDeletionSync();

console.log('🔧 Deletion sync fix script loaded'); 