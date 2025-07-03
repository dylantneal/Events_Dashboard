# Slide Timing Configuration Guide

## Overview

The Encore Dashboard displays slides in a continuous loop. By default, each slide displays for 60 seconds, but you can now customize the duration for each slide individually.

## How Slides Work

1. **Slide Sources**: 
   - PNG images in the `slides/` directory
   - Dynamic announcements board
   
2. **Slide Manifest**: The `slides.json` file automatically lists all PNG files

3. **Display Order**: Slides are shown in the order listed in `slides.json`, plus the announcements slide

## Configuring Slide Durations

### Method 1: Same Duration for All Slides

Edit your `config.js` file and set the `slideInterval` value:

```javascript
window.DASHBOARD_CONFIG = {
    slideInterval: 90000, // 90 seconds for all slides
    // ... other settings
};
```

### Method 2: Different Duration for Each Slide

Use the `slideDurations` object to set individual slide timings:

```javascript
window.DASHBOARD_CONFIG = {
    // Default duration for slides not specified below
    slideInterval: 60000, // 60 seconds default
    
    // Individual slide durations
    slideDurations: {
        // Monthly calendars - longer viewing time
        'calendar_2025_07.png': 120000,  // 2 minutes
        'calendar_2025_08.png': 120000,  // 2 minutes
        
        // Gantt charts - standard viewing time
        'gantt_2025_07.png': 60000,     // 1 minute
        'gantt_2025_08.png': 60000,     // 1 minute
        
        // Daily view - quick glance
        'gantt_daily_2025_07_02.png': 30000,  // 30 seconds
        
        // Weekly view - medium duration
        'gantt_weekly_2025_06_30.png': 45000, // 45 seconds
        
        // Announcements - give people time to read
        'announcements': 90000  // 1.5 minutes
    },
    // ... other settings
};
```

## Duration Reference

| Seconds | Milliseconds | Use Case |
|---------|--------------|----------|
| 15 | 15000 | Quick status updates |
| 30 | 30000 | Daily schedules, brief info |
| 45 | 45000 | Weekly overviews |
| 60 | 60000 | Standard slides (default) |
| 90 | 90000 | Detailed charts, announcements |
| 120 | 120000 | Complex calendars, detailed info |
| 180 | 180000 | Very detailed content |

## Best Practices

1. **Calendar Views**: 90-120 seconds (people need time to scan dates)
2. **Gantt Charts**: 60-90 seconds (depending on complexity)
3. **Daily Views**: 30-45 seconds (less information to absorb)
4. **Announcements**: 60-120 seconds (depending on typical message length)

## Testing Your Configuration

1. Open `test_slide_timing.html` in a browser to test short durations
2. Watch the console for timing logs
3. The progress bar at the bottom shows remaining time for each slide

## Troubleshooting

- **Slides not changing duration**: Make sure you're editing `config.js`, not `config.example.js`
- **All slides same duration**: Check that slide filenames in `slideDurations` match exactly
- **Progress bar wrong**: Clear browser cache and reload

## Configuring Slide Order

You can customize the order in which slides appear using the `slideOrder` configuration:

```javascript
window.DASHBOARD_CONFIG = {
    // ... other settings
    
    // Slide order configuration
    // Lower numbers appear first (after announcements)
    slideOrder: {
        'daily': 1,    // Happening Today - shows first
        'weekly': 2,   // Happening This Week - shows second
        'current': 3,  // This Month - shows third
        'next': 4,     // Next Month - shows fourth
        'third': 5,    // Third Month - shows fifth
        'calendar': 6  // Calendar - shows last
    }
};
```

The system automatically:
- Keeps announcements as the first slide
- Identifies monthly Gantt charts as current, next, or third month
- Orders slides according to your configuration
- Falls back to alphabetical order for unrecognized slides

## Technical Details

The implementation uses:
- `setTimeout` instead of `setInterval` for per-slide flexibility
- Dynamic progress bar animation based on slide duration
- Console logging for debugging (`Setting timer for slide X: Y seconds`)
- Smart slide categorization based on filename patterns

## Example: Mixed Duration Setup

```javascript
// Short rotation for status dashboard
slideDurations: {
    'status_overview.png': 15000,      // 15 sec
    'today_schedule.png': 20000,       // 20 sec
    'alerts.png': 10000,               // 10 sec
    'announcements': 30000             // 30 sec
}

// Long rotation for detailed planning
slideDurations: {
    'monthly_calendar.png': 180000,    // 3 min
    'project_gantt.png': 120000,       // 2 min
    'resource_allocation.png': 150000, // 2.5 min
    'announcements': 120000            // 2 min
}
``` 