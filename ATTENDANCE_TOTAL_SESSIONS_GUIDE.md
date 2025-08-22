# Dynamic Total Sessions Feature - User Guide

## Overview
The attendance system now supports **dynamic total sessions** that can be edited by administrators and teachers. This allows you to set custom total session counts for students, which is useful for:

- Setting expected total sessions for a semester/term
- Adjusting for students who joined mid-term
- Accounting for planned sessions that haven't occurred yet
- Correcting attendance percentages based on actual class schedules

## Features

### 1. **Inline Editing**
- Click on any student's "Total Sessions" number in the attendance list
- The number becomes editable
- Enter the new value and press Enter to save
- Press Escape to cancel editing

### 2. **Bulk Update**
- Use the "Bulk Update Sessions" button to set the same total sessions for all visible students
- Useful for setting semester totals for entire classes

### 3. **Smart Validation**
- Total sessions cannot be less than actual attendance records
- Only positive numbers are allowed
- Real-time attendance percentage recalculation

### 4. **Visual Indicators**
- Shows "(X actual)" when custom total differs from actual records
- Hover effects indicate editable fields
- Success/error messages for all operations

## How to Use

### For Administrators and Teachers:

1. **Navigate to Attendance List**
   - Go to Attendance → Attendance List
   - Filter by classroom if needed

2. **Edit Individual Student Sessions**
   - Click on the total sessions number for any student
   - Enter the new total (must be ≥ actual attendance records)
   - Press Enter to save or Escape to cancel

3. **Bulk Update All Students**
   - Click "Bulk Update Sessions" button
   - Enter the total sessions for all visible students
   - Click "Update All" to apply

4. **View Results**
   - Attendance percentages update automatically
   - Custom totals are saved per student/classroom combination

### Admin Panel Management:
- Go to Admin → Attendance → Student Total Sessions
- View, edit, or delete custom session totals
- Track who created/updated each record

## Technical Details

### Database Structure
- New model: `StudentTotalSessions`
- Stores custom totals per student/classroom/subject combination
- Tracks creation and modification history

### Automatic Profile Creation
- Student profiles are automatically created for new student users
- Existing students without profiles are fixed automatically
- Management command available: `python manage.py fix_student_profiles`

### API Endpoint
- POST `/attendance/update-total-sessions/`
- JSON payload: `{"student_id": 123, "total_sessions": 50}`
- Returns updated percentage and success status

## Troubleshooting

### "Student profile not found" Error
This error has been fixed by:
1. Automatic profile creation for new users
2. Management command to fix existing users
3. Graceful handling in attendance views

### Permission Issues
- Only administrators and teachers can edit total sessions
- Students can view but not modify attendance data

### Validation Errors
- "Total sessions cannot be less than actual records" - Increase the number
- "Must be a valid positive number" - Enter a number ≥ 0

## Benefits

1. **Accurate Percentages**: Set realistic totals based on planned sessions
2. **Flexible Management**: Handle mid-term enrollments and schedule changes
3. **Bulk Operations**: Efficiently manage entire classrooms
4. **Audit Trail**: Track who made changes and when
5. **User-Friendly**: Intuitive inline editing with visual feedback

## Example Scenarios

### Scenario 1: New Semester Setup
- Set total sessions to 60 for all students in a classroom
- As sessions occur, attendance percentage accurately reflects progress

### Scenario 2: Mid-term Student
- Student joins after 10 sessions have occurred
- Set their total to 50 (remaining sessions)
- Their percentage calculates correctly from their start date

### Scenario 3: Schedule Changes
- Originally planned 50 sessions, now planning 45
- Bulk update all students to 45 total sessions
- Percentages adjust automatically

The system is now ready for production use with full dynamic total sessions support!