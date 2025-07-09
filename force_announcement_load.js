// FORCE ANNOUNCEMENT LOAD SCRIPT
// This script bypasses any initialization issues and forces announcement loading

console.log('🚀 FORCE LOADING ANNOUNCEMENTS...');

// Wait for page to be ready
function forceLoadAnnouncements() {
    console.log('🔧 Starting force load process...');
    
    // Direct cloud fetch
    const cloudUrl = 'https://api.jsonbin.io/v3/b/686350a78a456b7966b930b1/latest';
    
    fetch(cloudUrl)
        .then(response => {
            console.log('📡 Direct cloud response:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('📦 Direct cloud data:', data);
            
            if (data.record && data.record.announcements) {
                const announcements = data.record.announcements;
                console.log('✅ Found', announcements.length, 'announcements in cloud');
                
                // Save to localStorage
                localStorage.setItem('dashboard_announcements', JSON.stringify(announcements));
                console.log('💾 Saved to localStorage');
                
                // Check which are active
                const now = new Date();
                const activeAnnouncements = announcements.filter(ann => {
                    const startDate = new Date(ann.startDate + 'T' + ann.startTime);
                    const endDate = new Date(ann.endDate + 'T' + ann.endTime);
                    return now >= startDate && now <= endDate;
                });
                
                console.log('📊 Active announcements:', activeAnnouncements.length);
                activeAnnouncements.forEach(ann => {
                    console.log('  ✅', ann.text);
                });
                
                // Try to update the display if dashboard exists
                if (window.dashboard) {
                    console.log('🎯 Updating dashboard display...');
                    window.dashboard.announcements = announcements;
                    window.dashboard.updateAnnouncementsDisplay();
                } else {
                    console.log('⚠️ Dashboard not ready yet, will retry...');
                    setTimeout(forceLoadAnnouncements, 2000);
                }
                
                // Force page refresh to ensure display updates
                setTimeout(() => {
                    console.log('🔄 Forcing page refresh to update display...');
                    location.reload();
                }, 3000);
                
            } else {
                console.error('❌ Invalid cloud data structure');
            }
        })
        .catch(error => {
            console.error('❌ Force load failed:', error);
        });
}

// Run immediately and also after page load
forceLoadAnnouncements();

// Also run when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', forceLoadAnnouncements);
} else {
    setTimeout(forceLoadAnnouncements, 1000);
}

console.log('🎯 Force load script initialized'); 