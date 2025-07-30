// Simple test to verify announcement system
console.log('🧪 Testing Announcement System...\n');

// Test 1: Cloud Access
async function testCloudAccess() {
    try {
        const response = await fetch('https://api.jsonbin.io/v3/b/686350a78a456b7966b930b1/latest');
        const data = await response.json();
        
        if (data.record && data.record.announcements) {
            console.log('✅ Cloud access: SUCCESS');
            console.log(`   Found ${data.record.announcements.length} announcements`);
            return true;
        }
        return false;
    } catch (error) {
        console.log('❌ Cloud access: FAILED -', error.message);
        return false;
    }
}

// Test 2: Dashboard Access
async function testDashboard() {
    try {
        const response = await fetch('https://www.marquisdashboard.com');
        const html = await response.text();
        
        const hasSync = html.includes('syncAnnouncementsFromCloud');
        const hasConfig = html.includes('cloudSync');
        const noEnhanced = !html.includes('startEnhancedAnnouncementSync');
        
        if (hasSync && hasConfig && noEnhanced) {
            console.log('✅ Dashboard: SUCCESS');
            console.log('   Has sync function, cloud config, no enhanced sync');
            return true;
        } else {
            console.log('❌ Dashboard: FAILED');
            console.log(`   Sync: ${hasSync}, Config: ${hasConfig}, No Enhanced: ${noEnhanced}`);
            return false;
        }
    } catch (error) {
        console.log('❌ Dashboard: FAILED -', error.message);
        return false;
    }
}

// Test 3: Announcement Active Check
function testAnnouncementTiming() {
    const now = new Date();
    const start = new Date('2025-07-30T10:00');
    const end = new Date('2025-07-30T17:00');
    const isActive = now >= start && now <= end;
    
    console.log('✅ Timing check: SUCCESS');
    console.log(`   Current time: ${now.toLocaleTimeString()}`);
    console.log(`   Announcement should be: ${isActive ? 'ACTIVE' : 'INACTIVE'}`);
    
    return isActive;
}

// Run all tests
async function runTests() {
    console.log('🚀 Running comprehensive tests...\n');
    
    const cloud = await testCloudAccess();
    const dashboard = await testDashboard();
    const timing = testAnnouncementTiming();
    
    console.log('\n📊 Test Results:');
    console.log(`   Cloud Access: ${cloud ? '✅ PASS' : '❌ FAIL'}`);
    console.log(`   Dashboard: ${dashboard ? '✅ PASS' : '❌ FAIL'}`);
    console.log(`   Timing: ${timing ? '✅ ACTIVE' : '⚠️ INACTIVE'}`);
    
    const overall = cloud && dashboard;
    console.log(`\n🎯 Overall: ${overall ? '✅ SYSTEM WORKING' : '❌ SYSTEM BROKEN'}`);
    
    if (overall && timing) {
        console.log('\n🎉 ALL SYSTEMS GO! Announcements should sync across browsers.');
    } else if (overall && !timing) {
        console.log('\n⏰ System working but no active announcements right now.');
    } else {
        console.log('\n🔧 System needs attention - check failed components.');
    }
}

// Run the tests
runTests();