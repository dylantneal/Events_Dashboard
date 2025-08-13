// ENHANCED SYNC LOGGING - Phase 3 Configuration Verification
// This script adds detailed logging to track sync operations without modifying core functionality
// Safe to use - only adds console logging, no function overrides

console.log('📊 ENHANCED SYNC LOGGING: Initializing...');

// Wait for dashboard to be ready
function waitForDashboard() {
    return new Promise((resolve) => {
        const check = () => {
            if (window.dashboard && window.dashboard.cloudSyncEnabled !== undefined) {
                resolve(window.dashboard);
            } else {
                setTimeout(check, 100);
            }
        };
        check();
    });
}

waitForDashboard().then(dashboard => {
    console.log('📊 ENHANCED LOGGING: Dashboard ready, adding sync monitoring...');
    
    // LOG CONFIGURATION STATUS
    function logConfigStatus() {
        console.log('\n=== 🔧 SYNC CONFIGURATION STATUS ===');
        console.log('✅ Cloud Sync Enabled:', dashboard.cloudSyncEnabled);
        console.log('🌐 Cloud URL:', dashboard.cloudSyncUrl);
        console.log('🔑 API Key Present:', !!dashboard.cloudSyncKey);
        console.log('⏰ Last Sync Time:', dashboard.lastSyncTime ? new Date(dashboard.lastSyncTime).toLocaleString() : 'Never');
        console.log('⚡ Sync In Progress:', dashboard.syncInProgress);
        console.log('📱 Local Announcements:', dashboard.announcements?.length || 0);
        
        if (dashboard.cloudSyncUrl) {
            const hasLatest = dashboard.cloudSyncUrl.includes('/latest');
            console.log('🔗 URL Format:', hasLatest ? '✅ Correct (with /latest)' : '⚠️ Missing /latest');
            
            // Show what URLs will be used
            const readUrl = dashboard.cloudSyncUrl;
            const writeUrl = dashboard.cloudSyncUrl.replace('/latest', '');
            console.log('📖 Read URL:', readUrl);
            console.log('💾 Write URL:', writeUrl);
        }
        console.log('=====================================\n');
    }
    
    // LOG SYNC EVENTS
    function logSyncEvent(operation, details) {
        const timestamp = new Date().toLocaleString();
        console.log(`🔄 [${timestamp}] SYNC EVENT: ${operation}`);
        if (details) {
            console.log('  Details:', details);
        }
    }
    
    // MONITOR SYNC OPERATIONS (without overriding)
    function startSyncMonitoring() {
        // Log config status immediately
        logConfigStatus();
        
        // Monitor sync timing
        let lastAnnouncementCount = dashboard.announcements?.length || 0;
        let lastSyncCheck = Date.now();
        
        setInterval(() => {
            const currentCount = dashboard.announcements?.length || 0;
            const now = Date.now();
            
            // Log if announcements count changed
            if (currentCount !== lastAnnouncementCount) {
                logSyncEvent('ANNOUNCEMENT COUNT CHANGED', {
                    from: lastAnnouncementCount,
                    to: currentCount,
                    difference: currentCount - lastAnnouncementCount
                });
                lastAnnouncementCount = currentCount;
            }
            
            // Log sync timing info every 30 seconds
            if (now - lastSyncCheck >= 30000) {
                const timeSinceLastSync = dashboard.lastSyncTime ? 
                    Math.round((now - dashboard.lastSyncTime) / 1000) : 'Never';
                const timeSinceLastSave = dashboard.lastLocalSaveTime ? 
                    Math.round((now - dashboard.lastLocalSaveTime) / 1000) : 'Never';
                
                console.log(`⏰ SYNC TIMING UPDATE:`);
                console.log(`  Time since last cloud sync: ${timeSinceLastSync}s`);
                console.log(`  Time since last local save: ${timeSinceLastSave}s`);
                console.log(`  Sync in progress: ${dashboard.syncInProgress}`);
                console.log(`  Current announcements: ${currentCount}`);
                
                lastSyncCheck = now;
            }
        }, 5000); // Check every 5 seconds
        
        console.log('📊 ENHANCED LOGGING: Monitoring started (every 5s checks, 30s reports)');
    }
    
    // MANUAL SYNC COMMANDS FOR TESTING
    window.syncDebug = {
        status: () => logConfigStatus(),
        
        test: async () => {
            console.log('🧪 MANUAL SYNC TEST: Starting...');
            try {
                await dashboard.syncAnnouncementsFromCloud();
                console.log('✅ MANUAL SYNC TEST: Completed successfully');
            } catch (error) {
                console.error('❌ MANUAL SYNC TEST: Failed', error);
            }
        },
        
        save: async () => {
            console.log('💾 MANUAL SAVE TEST: Starting...');
            try {
                await dashboard.saveAnnouncements();
                console.log('✅ MANUAL SAVE TEST: Completed successfully');
            } catch (error) {
                console.error('❌ MANUAL SAVE TEST: Failed', error);
            }
        },
        
        checkCloud: async () => {
            console.log('☁️ CLOUD CHECK: Fetching directly from cloud...');
            try {
                const cloudData = await dashboard.loadFromCloud();
                console.log('✅ CLOUD CHECK: Success');
                console.log('  Cloud announcements:', cloudData?.length || 0);
                console.log('  Cloud data:', cloudData);
            } catch (error) {
                console.error('❌ CLOUD CHECK: Failed', error);
            }
        }
    };
    
    // Start monitoring
    startSyncMonitoring();
    
    // Show available commands
    console.log('\n🛠️ MANUAL TESTING COMMANDS AVAILABLE:');
    console.log('  syncDebug.status() - Show current configuration');
    console.log('  syncDebug.test() - Test cloud sync manually');
    console.log('  syncDebug.save() - Test save to cloud manually');
    console.log('  syncDebug.checkCloud() - Check cloud storage directly');
    console.log('');
    
}).catch(error => {
    console.error('❌ ENHANCED LOGGING: Failed to initialize', error);
});