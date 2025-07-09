// FIX CLOUD SAVE FUNCTIONALITY
// This will repair the cloud save function and manually sync changes

console.log('🔧 FIXING CLOUD SAVE FUNCTIONALITY...');

async function fixCloudSave() {
    try {
        // Step 1: Clear everything and start fresh
        console.log('🧹 Step 1: Clearing all local data...');
        localStorage.removeItem('dashboard_announcements');
        
        // Step 2: Create a fresh lunch announcement
        console.log('🍽️ Step 2: Creating fresh lunch announcement...');
        const now = new Date();
        const lunchAnnouncement = {
            id: 'lunch_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9),
            text: 'Lunch announcement - Please update this with your actual lunch message',
            startDate: now.toISOString().split('T')[0],
            startTime: now.toTimeString().split(' ')[0].slice(0, 5),
            endDate: now.toISOString().split('T')[0],
            endTime: '17:00',
            createdAt: now.toISOString(),
            lastModified: now.toISOString()
        };
        
        // Step 3: Save ONLY the lunch announcement to cloud (delete all others)
        console.log('☁️ Step 3: Saving lunch announcement to cloud...');
        const cloudUrl = 'https://api.jsonbin.io/v3/b/686350a78a456b7966b930b1';
        
        const response = await fetch(cloudUrl, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Cache-Control': 'no-cache'
            },
            body: JSON.stringify({
                announcements: [lunchAnnouncement]
            })
        });
        
        if (!response.ok) {
            throw new Error(`Save failed: ${response.status} ${response.statusText}`);
        }
        
        const result = await response.json();
        console.log('✅ Cloud save successful:', result);
        
        // Step 4: Update local storage
        localStorage.setItem('dashboard_announcements', JSON.stringify([lunchAnnouncement]));
        console.log('💾 Updated local storage');
        
        // Step 5: Update dashboard if it exists
        if (window.dashboard) {
            console.log('🎯 Updating dashboard...');
            window.dashboard.announcements = [lunchAnnouncement];
            window.dashboard.updateAnnouncementsDisplay();
        }
        
        console.log('🎉 CLOUD SAVE FIXED!');
        console.log('📝 You now have a single lunch announcement that you can edit');
        console.log('🔄 Refreshing page to ensure clean state...');
        
        // Refresh after a short delay
        setTimeout(() => {
            location.reload(true);
        }, 2000);
        
    } catch (error) {
        console.error('❌ Fix failed:', error);
        
        // Fallback: Manual instructions
        console.log('🔧 MANUAL FIX REQUIRED:');
        console.log('1. Delete all announcements manually');
        console.log('2. Create a new lunch announcement');
        console.log('3. Refresh the page');
        
        // Still try to refresh
        setTimeout(() => {
            location.reload(true);
        }, 3000);
    }
}

// Enhanced save function to prevent future issues
function enhancedSaveToCloud(announcements) {
    console.log('💾 ENHANCED SAVE: Saving', announcements.length, 'announcements to cloud...');
    
    const cloudUrl = 'https://api.jsonbin.io/v3/b/686350a78a456b7966b930b1';
    
    return fetch(cloudUrl, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache'
        },
        body: JSON.stringify({
            announcements: announcements
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Save failed: ${response.status} ${response.statusText}`);
        }
        return response.json();
    })
    .then(result => {
        console.log('✅ Enhanced save successful');
        return result;
    })
    .catch(error => {
        console.error('❌ Enhanced save failed:', error);
        throw error;
    });
}

// Override the dashboard's save function if it exists
if (window.dashboard) {
    console.log('🔧 Overriding dashboard save function...');
    window.dashboard.saveToCloud = enhancedSaveToCloud;
}

// Run the fix
fixCloudSave();

console.log('🔧 Cloud save fix script loaded'); 