// SYNC TEST AUTOMATION - Phase 4 Testing Helper
// This script provides automated testing functions to verify announcement sync
// Load this in console to access testing utilities

console.log('🧪 SYNC TEST AUTOMATION: Loading test utilities...');

// Wait for dashboard and debug tools
function waitForTestEnvironment() {
    return new Promise((resolve) => {
        const check = () => {
            if (window.dashboard && window.syncDebug) {
                resolve(true);
            } else {
                setTimeout(check, 500);
            }
        };
        check();
    });
}

waitForTestEnvironment().then(() => {
    console.log('🧪 TEST AUTOMATION: Environment ready');
    
    // Test utilities
    window.testUtils = {
        
        // Create a test announcement with unique identifier
        createTestAnnouncement: function(deviceName = 'Unknown', testName = 'General') {
            const now = new Date();
            const endTime = new Date(now.getTime() + 2 * 60 * 60 * 1000); // +2 hours
            
            const announcement = {
                id: `test_${testName}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
                text: `TEST: ${testName} - Created on ${deviceName} at ${now.toLocaleTimeString()}`,
                startDate: now.toISOString().split('T')[0],
                startTime: now.toTimeString().split(' ')[0].slice(0, 5),
                endDate: endTime.toISOString().split('T')[0],
                endTime: endTime.toTimeString().split(' ')[0].slice(0, 5),
                createdAt: now.toISOString(),
                lastModified: now.toISOString()
            };
            
            dashboard.announcements.push(announcement);
            console.log(`✅ Created test announcement: ${announcement.text}`);
            return announcement;
        },
        
        // Save and sync test announcement
        saveAndSync: async function() {
            try {
                await dashboard.saveAnnouncements();
                console.log('✅ Save completed');
                return true;
            } catch (error) {
                console.error('❌ Save failed:', error);
                return false;
            }
        },
        
        // Run basic functionality test
        runBasicTest: async function(deviceName = 'TestDevice') {
            console.log(`\n🧪 RUNNING BASIC TEST on ${deviceName}...`);
            
            const beforeCount = dashboard.announcements.length;
            console.log(`📊 Starting announcements: ${beforeCount}`);
            
            // Create test announcement
            const testAnn = this.createTestAnnouncement(deviceName, 'BasicTest');
            
            // Save and sync
            const saveSuccess = await this.saveAndSync();
            
            if (saveSuccess) {
                console.log(`✅ BASIC TEST COMPLETE on ${deviceName}`);
                console.log(`📊 Final announcements: ${dashboard.announcements.length}`);
                return testAnn;
            } else {
                console.error(`❌ BASIC TEST FAILED on ${deviceName}`);
                return null;
            }
        },
        
        // Check for announcements from other devices
        checkForSyncedAnnouncements: function(searchText = 'TEST:') {
            const testAnnouncements = dashboard.announcements.filter(ann => 
                ann.text.includes(searchText)
            );
            
            console.log(`📊 Found ${testAnnouncements.length} test announcements:`);
            testAnnouncements.forEach(ann => {
                console.log(`  - ${ann.text} (ID: ${ann.id.substr(0, 20)}...)`);
            });
            
            return testAnnouncements;
        },
        
        // Clean up test announcements
        cleanupTestAnnouncements: async function() {
            const beforeCount = dashboard.announcements.length;
            dashboard.announcements = dashboard.announcements.filter(ann => 
                !ann.id.startsWith('test_')
            );
            const afterCount = dashboard.announcements.length;
            const removedCount = beforeCount - afterCount;
            
            if (removedCount > 0) {
                await this.saveAndSync();
                console.log(`🧹 Cleaned up ${removedCount} test announcements`);
            } else {
                console.log('🧹 No test announcements to clean up');
            }
            
            return removedCount;
        },
        
        // Monitor sync for specific duration
        monitorSync: function(durationMinutes = 2) {
            console.log(`👀 MONITORING SYNC for ${durationMinutes} minutes...`);
            
            let checks = 0;
            const maxChecks = durationMinutes * 4; // Check every 15 seconds
            const startCount = dashboard.announcements.length;
            
            const monitor = setInterval(() => {
                checks++;
                const currentCount = dashboard.announcements.length;
                const timeSinceLastSync = dashboard.lastSyncTime ? 
                    Math.round((Date.now() - dashboard.lastSyncTime) / 1000) : 'Never';
                
                console.log(`👀 Check ${checks}/${maxChecks}: ${currentCount} announcements, last sync ${timeSinceLastSync}s ago`);
                
                if (currentCount !== startCount) {
                    console.log(`📊 SYNC DETECTED: Count changed from ${startCount} to ${currentCount}`);
                }
                
                if (checks >= maxChecks) {
                    clearInterval(monitor);
                    console.log(`👀 MONITORING COMPLETE after ${durationMinutes} minutes`);
                }
            }, 15000); // Every 15 seconds
            
            return monitor;
        },
        
        // Full cross-device test sequence
        runCrossDeviceTest: async function(deviceName) {
            console.log(`\n🌐 RUNNING CROSS-DEVICE TEST on ${deviceName}...`);
            
            // Step 1: Check current state
            syncDebug.status();
            
            // Step 2: Create test announcement
            const testAnn = await this.runBasicTest(deviceName);
            
            if (testAnn) {
                // Step 3: Start monitoring for sync on other devices
                console.log(`📡 Test announcement created: ${testAnn.text}`);
                console.log(`🔍 Watch other devices for this announcement to appear`);
                console.log(`⏰ Expected sync time: 60-90 seconds`);
                
                // Step 4: Monitor this device for changes from others
                this.monitorSync(3); // Monitor for 3 minutes
                
                return testAnn;
            }
            
            return null;
        },
        
        // Quick system health check
        healthCheck: function() {
            console.log('\n💊 SYSTEM HEALTH CHECK...');
            
            // Check configuration
            const config = {
                cloudSyncEnabled: dashboard.cloudSyncEnabled,
                cloudSyncUrl: dashboard.cloudSyncUrl,
                syncInProgress: dashboard.syncInProgress,
                announcementCount: dashboard.announcements.length,
                lastSyncTime: dashboard.lastSyncTime ? new Date(dashboard.lastSyncTime).toLocaleString() : 'Never',
                lastSaveTime: dashboard.lastLocalSaveTime ? new Date(dashboard.lastLocalSaveTime).toLocaleString() : 'Never'
            };
            
            console.table(config);
            
            // Check for errors
            const hasErrors = !dashboard.cloudSyncEnabled || !dashboard.cloudSyncUrl;
            
            if (hasErrors) {
                console.warn('⚠️ CONFIGURATION ISSUES DETECTED');
            } else {
                console.log('✅ SYSTEM HEALTH: GOOD');
            }
            
            return !hasErrors;
        }
    };
    
    console.log('\n🛠️ TEST AUTOMATION COMMANDS AVAILABLE:');
    console.log('  testUtils.healthCheck() - Quick system health check');
    console.log('  testUtils.runBasicTest("DeviceName") - Test basic functionality');
    console.log('  testUtils.runCrossDeviceTest("DeviceName") - Full cross-device test');
    console.log('  testUtils.checkForSyncedAnnouncements() - Look for test announcements');
    console.log('  testUtils.monitorSync(minutes) - Monitor sync activity');
    console.log('  testUtils.cleanupTestAnnouncements() - Remove test data');
    console.log('');
    
    // Auto-run health check
    setTimeout(() => {
        testUtils.healthCheck();
    }, 1000);
    
}).catch(error => {
    console.error('❌ TEST AUTOMATION: Failed to initialize', error);
});