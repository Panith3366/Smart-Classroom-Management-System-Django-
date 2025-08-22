# Editable Attendance Counts Feature - User Guide

## Overview
The attendance system now supports **editable Present, Late, and Absent counts** similar to the existing Total Sessions functionality. This allows system administrators and teachers to:

- Edit individual attendance counts by clicking on them
- Perform bulk updates for attendance counts across multiple students
- Override actual attendance records with custom values
- Maintain audit trails of who made changes and when

## Features

### 1. **Inline Editing for Attendance Counts**
- Click on any student's Present, Late, or Absent count in the attendance list
- The number becomes editable with visual feedback (hover effects and edit icon)
- Enter the new value and press Enter to save
- Press Escape to cancel editing
- Only non-negative integers are allowed

### 2. **Visual Indicators**
- Editable fields show hover effects with edit icons
- Custom counts display "(X actual)" when they differ from actual records
- Color-coded counts: Present (green), Late (yellow), Absent (red)
- Real-time attendance percentage recalculation

### 3. **Bulk Update Functionality**
- New "Bulk Update Attendance" dropdown in Quick Actions panel
- Separate options for Present, Late, and Absent counts
- Apply the same count to all visible students in current filter
- Confirmation and progress feedback

### 4. **Permission Control**
- Only system administrators and teachers can edit attendance counts
- Students can view but not modify attendance data
- All changes are logged with user information

## How to Use

### For Administrators and Teachers:

#### Individual Student Count Editing:
1. **Navigate to Attendance List**
   - Go to Attendance → Attendance List
   - Filter by classroom if needed

2. **Edit Present/Late/Absent Counts**
   - Click on any Present, Late, or Absent number for a student
   - Enter the new count (must be ≥ 0)
   - Press Enter to save or Escape to cancel

3. **View Results**
   - Attendance percentages update automatically
   - Custom counts show "(X actual)" when different from real records
   - Total sessions may also update automatically

#### Bulk Update All Students:
1. **Use Quick Actions Panel**
   - Click "Bulk Update Attendance" dropdown
   - Select "Present Count", "Late Count", or "Absent Count"

2. **Set Values**
   - Enter the count for all visible students
   - Click "Update All" to apply

3. **Confirmation**
   - Success/error messages show update results
   - Page refreshes to show updated data

### Admin Panel Management:
- Go to Admin → Attendance → Student Custom Attendance Records
- View, edit, or delete custom attendance records
- Track who created/updated each record
- See total custom sessions calculated from counts

## Technical Details

### Database Structure
- New model: `StudentCustomAttendance`
- Stores custom counts per student/classroom/subject combination
- Tracks creation and modification history
- Unique constraint prevents duplicate records

### API Endpoints
- POST `/attendance/update-attendance-count/`
  - Parameters: `student_id`, `count_type` (present/late/absent), `count_value`
  - Returns updated counts and percentage

- POST `/attendance/bulk-update-attendance-counts/`
  - Parameters: `count_type`, `count_value`, `student_ids[]`
  - Returns bulk update results

### Data Priority
1. **Custom Attendance Records** (if they exist) - highest priority
2. **Actual Attendance Records** - fallback if no custom records
3. **Automatic Initialization** - custom records are created with actual values when first edited

## Benefits

1. **Flexible Management**: Handle special cases, corrections, and adjustments
2. **Bulk Operations**: Efficiently manage entire classrooms
3. **Audit Trail**: Track who made changes and when
4. **User-Friendly**: Intuitive inline editing with visual feedback
5. **Data Integrity**: Maintains both actual and custom records
6. **Permission Control**: Only authorized users can make changes

## Example Scenarios

### Scenario 1: Correcting Student Records
- Student was present but marked absent due to technical issue
- Click on their Absent count, change from 1 to 0
- Click on their Present count, increase by 1
- Attendance percentage updates automatically

### Scenario 2: Adjusting for Transfer Students
- Student transferred mid-semester with attendance from previous school
- Set their Present count to include previous attendance
- Adjust other counts as needed
- System maintains both actual and custom records

### Scenario 3: Bulk Corrections
- Entire class was marked absent due to system error
- Use "Bulk Update Attendance" → "Absent Count"
- Set all students' absent count to 0
- Then bulk update present count to correct value

## Validation Rules

1. **Non-negative Numbers**: All counts must be ≥ 0
2. **Integer Values**: Only whole numbers are accepted
3. **Permission Checks**: Only admin/teacher roles can edit
4. **Data Consistency**: System maintains both actual and custom records

## Troubleshooting

### "Permission denied" Error
- Only administrators and teachers can edit attendance counts
- Students and other roles cannot modify attendance data

### Changes Not Saving
- Check network connection
- Ensure you're logged in with proper permissions
- Try refreshing the page and attempting again

### Visual Issues
- Custom counts show "(X actual)" to indicate override
- Hover effects indicate editable fields
- Progress circles update automatically with new percentages

## Migration and Compatibility

- New feature is backward compatible
- Existing attendance data remains unchanged
- Custom records are created only when explicitly edited
- Original attendance records are preserved for audit purposes

## Security Considerations

- All changes logged with user information
- Custom records track creation and modification timestamps
- Original attendance data is never deleted or modified
- Permission-based access control enforced at all levels

The system now provides complete flexibility for attendance management while maintaining data integrity and audit trails!