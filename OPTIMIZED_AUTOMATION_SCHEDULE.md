# Optimized Automation Schedule

## Overview
This document describes the new optimized GitHub Actions scheduling system that resolves midnight UTC congestion issues and workflow conflicts.

## Schedule Changes Made

### Previous Issues
- **Midnight UTC Problem**: Both daily workflows scheduled at `0 0 * * *` (midnight UTC)
- **High Congestion**: Midnight UTC is peak time for GitHub Actions globally
- **Delays**: Consistent 1-2 hour delays due to GitHub's scheduling queue
- **Duplicated Work**: Two daily workflows doing overlapping tasks

### New Optimized Schedule

| Workflow | Previous Schedule | New Schedule | Local Time (CDT) | Rationale |
|----------|-------------------|--------------|------------------|-----------|
| **Daily Enhanced** | `0 0 * * *` | `15 3 * * *` | 10:15 PM | Off-peak UTC time, comprehensive daily update |
| **Weekly** | `0 0 * * 1` | `30 3 * * 1` | 10:30 PM Sun | Staggered 15 min after daily |
| **Monthly** | `0 6 1 * *` | `45 3 1 * *` | 10:45 PM previous day | Staggered 30 min after daily |

### Improvements Made

#### 1. **Eliminated Duplicate Workflows**
- ❌ Removed: `daily-update.yml` (basic daily workflow)
- ✅ Kept: `daily-update-enhanced.yml` (comprehensive workflow that updates all charts)

#### 2. **Off-Peak Scheduling**
- **3:15 AM UTC**: Much less GitHub Actions traffic
- **Staggered timing**: Prevents resource conflicts between workflows
- **Predictable execution**: Should run within 5-10 minutes of scheduled time

#### 3. **Enhanced Reliability**
- **Retry logic**: Auto-retry failed git pushes
- **Dependency caching**: Faster execution with pip cache
- **Timeout protection**: Prevents hanging workflows
- **File verification**: Confirms files were generated

#### 4. **Better Error Handling**
- **Push retries**: Automatic retry if git push fails
- **Execution logging**: Detailed completion timestamps
- **File verification**: Checks that expected files exist

## Expected Behavior

### Daily Updates (10:15 PM CDT)
- **What happens**: Updates all charts with today markers
- **Files updated**: Daily, weekly, monthly charts + calendar
- **Commit message**: `🎯 Auto-update: Daily refresh with Today markers - [Date]`
- **Expected completion**: Within 10 minutes (by 10:25 PM CDT)

### Weekly Updates (10:30 PM CDT Sundays)
- **What happens**: Generates "Happening This Week" chart
- **Commit message**: `🤖 Auto-update: Weekly dashboard - [Date Range]`
- **Expected completion**: Within 10 minutes (by 10:40 PM CDT)

### Monthly Updates (10:45 PM CDT, last day of month)
- **What happens**: 4-month rolling window + calendar generation
- **Commit message**: `🤖 Auto-update: Monthly dashboard - [Month Year] 4-month rolling window + calendar`
- **Expected completion**: Within 15 minutes (by 11:00 PM CDT)

## Monitoring

### Check Automation Status
```bash
./check_automation_status.sh
```

### Manual Triggers
If automation fails, you can manually trigger workflows:
1. Go to: https://github.com/dylantneal/Encore_Dashboard/actions
2. Select the workflow you want to run
3. Click "Run workflow" button

### Expected Timeline
- **10:15 PM CDT**: Daily automation starts
- **10:25 PM CDT**: Daily automation completes
- **10:30 PM CDT** (Sundays): Weekly automation starts
- **10:45 PM CDT** (1st of month): Monthly automation starts
- **11:00 PM CDT**: All automation should be complete

## Troubleshooting

### If workflows don't run
1. Check GitHub Actions page for errors
2. Verify repository permissions
3. Run manual trigger as backup
4. Use `./emergency_manual_update.sh` for immediate updates

### Expected behavior changes
- **More reliable timing**: Should run within 10 minutes of schedule
- **Better visibility**: Enhanced logging and verification
- **No more duplicates**: Only one daily workflow now
- **Faster execution**: Dependency caching reduces setup time

## Benefits

✅ **Eliminated midnight UTC congestion**
✅ **Removed duplicate workflows**  
✅ **Staggered scheduling prevents conflicts**
✅ **Added reliability improvements**
✅ **Better error handling and retries**
✅ **Faster execution with caching**
✅ **Predictable timing you can count on**

Your automation should now run reliably every evening around 10:15-11:00 PM CDT, giving you fresh data every morning!