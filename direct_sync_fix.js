// DIRECT SYNC FIX - Run this in your browser console on marquisdashboard.com
// This fixes the CRUD sync issue immediately without waiting for deployment

console.log('🔧 DIRECT SYNC FIX: Starting...');

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
    console.log('✅ Dashboard found, applying direct sync fix...');
    
    // FORCE ENABLE CLOUD SYNC
    dashboard.cloudSyncEnabled = true;
    dashboard.cloudSyncUrl = 'https://api.jsonbin.io/v3/b/686350a78a456b7966b930b1/latest';
    
    // OVERRIDE CREATE/UPDATE FUNCTION
    const originalSubmit = dashboard.handleAnnouncementSubmit;
    dashboard.handleAnnouncementSubmit = async function() {
        console.log('📝 DIRECT FIX: Creating/updating announcement...');
        
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

        // IMMEDIATE CLOUD SYNC
        try {
            console.log('☁️ DIRECT FIX: Syncing to cloud...');
            const response = await fetch('https://api.jsonbin.io/v3/b/686350a78a456b7966b930b1', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ announcements: this.announcements })
            });
            
            if (response.ok) {
                console.log('✅ DIRECT FIX: Cloud sync successful!');
                localStorage.setItem('dashboard_announcements', JSON.stringify(this.announcements));
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
        } catch (error) {
            console.error('❌ DIRECT FIX: Cloud sync failed:', error);
            alert('Failed to sync to cloud. Saved locally only.');
            localStorage.setItem('dashboard_announcements', JSON.stringify(this.announcements));
        }

        this.updateAnnouncementsDisplay();
        this.closeAnnouncementModal();
    };
    
    // OVERRIDE DELETE FUNCTION
    const originalDelete = dashboard.deleteAnnouncement;
    dashboard.deleteAnnouncement = async function(id) {
        if (!confirm('Delete this announcement?')) return;
        
        console.log('🗑️ DIRECT FIX: Deleting announcement...');
        this.announcements = this.announcements.filter(a => a.id !== id);
        
        // IMMEDIATE CLOUD SYNC
        try {
            const response = await fetch('https://api.jsonbin.io/v3/b/686350a78a456b7966b930b1', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ announcements: this.announcements })
            });
            
            if (response.ok) {
                console.log('✅ DIRECT FIX: Delete synced to cloud!');
                localStorage.setItem('dashboard_announcements', JSON.stringify(this.announcements));
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
        } catch (error) {
            console.error('❌ DIRECT FIX: Delete sync failed:', error);
            localStorage.setItem('dashboard_announcements', JSON.stringify(this.announcements));
        }
        
        this.updateAnnouncementsDisplay();
    };
    
    // ENHANCED PERIODIC SYNC
    if (dashboard.cloudSyncInterval) {
        clearInterval(dashboard.cloudSyncInterval);
    }
    
    dashboard.cloudSyncInterval = setInterval(async () => {
        if (dashboard.syncInProgress) return;
        
        try {
            dashboard.syncInProgress = true;
            console.log('🔄 DIRECT FIX: Checking for updates...');
            
            const response = await fetch('https://api.jsonbin.io/v3/b/686350a78a456b7966b930b1/latest?t=' + Date.now());
            const data = await response.json();
            const cloudAnnouncements = data.record.announcements || [];
            
            // Simple merge: if cloud has different count, update local
            if (cloudAnnouncements.length !== dashboard.announcements.length) {
                console.log('📝 DIRECT FIX: Updating from cloud...');
                dashboard.announcements = cloudAnnouncements;
                localStorage.setItem('dashboard_announcements', JSON.stringify(dashboard.announcements));
                dashboard.updateAnnouncementsDisplay();
            }
        } catch (error) {
            console.warn('❌ DIRECT FIX: Sync check failed:', error);
        } finally {
            dashboard.syncInProgress = false;
        }
    }, 30000); // Every 30 seconds
    
    // INITIAL SYNC
    setTimeout(() => {
        console.log('🚀 DIRECT FIX: Performing initial sync...');
        dashboard.cloudSyncInterval();
    }, 2000);
    
    // ADD VISUAL INDICATOR
    const indicator = document.createElement('div');
    indicator.textContent = '✅ Direct Sync Active';
    indicator.style.cssText = `
        position: fixed;
        top: 10px;
        right: 10px;
        background: #28a745;
        color: white;
        padding: 5px 10px;
        border-radius: 3px;
        font-size: 12px;
        z-index: 10000;
        font-family: Arial, sans-serif;
    `;
    document.body.appendChild(indicator);
    
    console.log('🎉 DIRECT SYNC FIX APPLIED SUCCESSFULLY!');
    console.log('✅ Create, Update, Delete will now sync immediately');
    console.log('✅ Automatic sync every 30 seconds');
    console.log('✅ Visual indicator added');
});
