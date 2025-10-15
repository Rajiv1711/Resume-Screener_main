# Session Management UI Guide

## Overview

The Resume Screener now includes a complete session management UI that allows users to:
- Create named upload sessions
- Switch between sessions
- Rename sessions
- Delete old sessions
- View session details (date, file count)

## UI Components

### SessionManager Component

Located at: `frontend/src/components/SessionManager.js`

This component provides the complete session management interface with:
- **Session List**: Shows all user sessions with names, dates, and file counts
- **Active Session Indicator**: Highlights the currently active session
- **Action Buttons**: Rename and delete for each session
- **Create Session Modal**: Dialog to create new sessions with custom names

## Features

### 1. **Create New Session**

Click the "New Session" button to open a modal where you can:
- Enter a custom name for your session (e.g., "ML Engineer Applications", "Backend Developer Roles")
- Click "Create" to start a new session
- The new session automatically becomes active

**API Call:**
```javascript
POST /api/sessions/create
Body: { "name": "ML Engineer Applications" }
```

### 2. **View All Sessions**

The session list shows:
- **Session Name**: Custom name or auto-generated
- **Created Date**: When the session was created
- **File Count**: Number of files uploaded to this session
- **Active Badge**: Shows which session is currently active

### 3. **Switch Sessions**

Click on any session to switch to it. The active session will:
- Be highlighted with a cyan border
- Show an "Active" badge
- Be used for all new uploads

**API Call:**
```javascript
POST /api/sessions/{session_id}/set-active
```

### 4. **Rename Session**

Click the pencil icon on any session to:
- Open the rename modal
- Enter a new name
- Save the changes

**API Call:**
```javascript
PUT /api/sessions/{session_id}/name
Body: { "name": "New Session Name" }
```

### 5. **Delete Session**

Click the trash icon to delete a session:
- Shows confirmation dialog
- Deletes all files in the session
- Shows count of deleted files
- If deleting active session, automatically switches to another

**API Call:**
```javascript
DELETE /api/sessions/{session_id}
```

## Integration

### UploadPage

The SessionManager is integrated into the UploadPage:

```jsx
<div className="row">
  {/* Session Manager Sidebar */}
  <div className="col-lg-4 mb-4">
    <SessionManager 
      onSessionChange={(sessionId) => {
        console.log('Active session changed to:', sessionId);
      }}
      pushToast={pushToast}
    />
  </div>

  {/* Upload Area */}
  <div className="col-lg-8">
    <UploadResume ... />
  </div>
</div>
```

### Dashboard Integration (Optional)

You can also add SessionManager to the Dashboard for easy session switching:

```jsx
import SessionManager from '../components/SessionManager';

// In your Dashboard component
<div className="row">
  <div className="col-lg-3">
    <SessionManager 
      onSessionChange={handleSessionChange}
      pushToast={pushToast}
    />
  </div>
  <div className="col-lg-9">
    {/* Existing dashboard content */}
  </div>
</div>
```

## User Experience

### Typical Workflow

1. **User visits Upload page**
   - Sees session manager on the left
   - Either has an existing session or creates a new one

2. **Create named session**
   - Click "New Session"
   - Enter name: "Senior Developer Screening - Jan 2025"
   - Session is created and becomes active

3. **Upload resumes**
   - All uploads go to the active session
   - Can see file count increase in session list

4. **Rank resumes**
   - Go to Dashboard
   - Resumes from active session are ranked
   - Results saved to that session

5. **Switch sessions**
   - Return to Upload page
   - Click different session to switch
   - Upload more resumes to new session

6. **Manage sessions**
   - Rename sessions for better organization
   - Delete old sessions to clean up storage

## Styling

The SessionManager uses your existing design system:

```css
--bg-tertiary: Session item background
--border-primary: Session item border
--accent-primary: Active session highlight (cyan)
--text-primary: Session name text
--text-secondary: Date and file count text
--accent-danger: Delete button color
```

Active session highlighting:
- Background: `rgba(79, 209, 197, 0.1)` (cyan with transparency)
- Border: `2px solid var(--accent-primary)`
- Badge: Cyan background with white text

## Responsive Design

The SessionManager is fully responsive:

- **Desktop (lg)**: Sidebar layout (col-lg-4)
- **Tablet**: Stacks above upload area
- **Mobile**: Full width with scrollable session list

## Animations

Uses Framer Motion for smooth animations:
- Session items fade in when loaded
- Session items slide out when deleted
- Modals scale up when opened
- Smooth transitions on hover

## Error Handling

All operations include error handling:
- Failed API calls show error toasts
- Confirmation dialogs for destructive actions
- Loading states during operations
- Graceful fallbacks for missing data

## Testing

### Manual Testing Checklist

- [ ] Create a new session with custom name
- [ ] Create a session with empty name (should require name)
- [ ] Switch between sessions
- [ ] Upload files to different sessions
- [ ] Rename a session
- [ ] Delete a session (verify files are deleted)
- [ ] Delete active session (verify switch to another)
- [ ] View session history with multiple sessions
- [ ] Test responsive behavior on mobile/tablet
- [ ] Test with no sessions (empty state)

### Example Test Scenario

```javascript
// 1. Create sessions
await createSession("ML Engineer Roles");
await createSession("Backend Developer Roles");

// 2. Upload to first session
await switchSession("session_20250115_103045");
await uploadResume("resume1.pdf");

// 3. Switch and upload to second
await switchSession("session_20250115_143020");
await uploadResume("resume2.pdf");

// 4. Verify isolation
const files1 = await listSessionFiles("session_20250115_103045");
// Should only show resume1.pdf

const files2 = await listSessionFiles("session_20250115_143020");
// Should only show resume2.pdf
```

## Future Enhancements

Possible additions:
- Session search/filter
- Bulk session operations
- Session sharing
- Session export
- Session templates
- Automatic session naming suggestions
- Session tags/categories

## Troubleshooting

### Session doesn't switch
- Check browser console for API errors
- Verify user_id is set in localStorage
- Check backend logs for session endpoint errors

### Files appear in wrong session
- Verify active session before upload
- Check that upload API uses session-based storage
- Confirm `upload_file_session()` is being called

### Can't delete session
- Check if session has files (they should be deleted)
- Verify user owns the session
- Check blob storage permissions

### Session names don't persist
- Verify metadata is being saved to blob storage
- Check `.metadata.json` files in session folders
- Confirm `_save_session_metadata()` is working
