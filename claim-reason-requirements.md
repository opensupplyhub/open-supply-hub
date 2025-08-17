# Requirements for Claim Reason Feature - Open Supply Hub

## Overview
Add functionality to track why organizations are claiming their production locations, with a focus on identifying which brands/companies are requesting these claims for potential service upselling opportunities.

## Django Model Changes

### 1. New Model: `ClaimsReason`
Create a new Django model with:
- `text` (CharField, max_length=100): The reason/company name
- `is_active` (BooleanField, default=True): Whether to show in dropdown
- `created_at` (DateTimeField, auto_now_add=True)
- `updated_at` (DateTimeField, auto_now=True)

Model should have:
- Alphabetical ordering by `text` field
- String representation showing the text
- Django admin registration

### 2. Update `ClaimsRequest` Model
Add new field:
- `claim_reason` (CharField, max_length=100, blank=True, null=True)

## Django Admin Interface

### ClaimsReason Admin
- List display: `text`, `is_active`, `created_at`
- List filter: `is_active`
- Search fields: `text`
- Ability to bulk activate/deactivate
- Inline editing for `is_active` checkbox

### ClaimsRequest Admin
- Add `claim_reason` to the Claims Dashboard/approval page
- Display as a column with hover tooltip for overflow text
- Position near Claim ID and Facility columns

## Frontend Form Changes

### Claim Form UI
On the page where proof of ownership/management and facility existence is collected:

#### 1. Add new section
- Question: "What made you decide to claim?"

#### 2. Dropdown component
- Populate with all `ClaimsReason` objects where `is_active=True`
- Sort alphabetically
- Include "Other" as the last option
- Default to no selection (placeholder: "Select a reason")

#### 3. Free text field
- Only visible when "Other" is selected
- Max length: 100 characters
- Placeholder: "Please specify"
- Character counter showing remaining characters

#### 4. JavaScript behavior
```javascript
// On page load: Show only dropdown
// If user selects "Other": 
//   - Show free text field
//   - Make it required if they want to proceed with "Other"
// If user selects any other dropdown option:
//   - Hide free text field
//   - Clear any text that was entered
```

#### 5. Form submission
- If dropdown selection (not "Other"): Save dropdown text to `claim_reason`
- If "Other" + free text: Save free text to `claim_reason`
- If nothing selected: Save as null (field is optional)

## API/Backend Logic

### View/Serializer Updates
- Include `claim_reason` in ClaimsRequest serializer
- No validation required on the content
- Ensure field remains optional in API

### Data Storage Logic
- Single `claim_reason` field stores either:
  - The selected dropdown option text, OR
  - The free text entry (when "Other" is selected)
- No need to track which type was used (dropdown vs free text)

## Claims Dashboard Updates

### Add "Claim Reason" Column
- **Location**: Claims approval/moderation page
- **Position**: Near Claim ID and Facility columns  
- **Display**: Show `claim_reason` field value
- **Overflow handling**: Truncate at ~30 chars with hover tooltip showing full text
- **Empty state**: Show "-" or empty cell for claims without reason

## Migration Plan

### 1. Migration file to:
- Create `ClaimsReason` model
- Add `claim_reason` field to `ClaimsRequest`
- Existing claims will have null/blank values (acceptable)

### 2. No data backfill needed
- Existing claims remain without reason

## Testing Considerations

- Verify "Other" option shows/hides free text appropriately
- Test character limit enforcement
- Ensure dropdown updates when admin adds/removes ClaimsReason objects
- Verify tooltip displays full text on hover in dashboard
- Test that form submits successfully with and without claim reason

## Future Considerations (Not in Initial Scope)

- Analytics on which reasons are most common
- Auto-promotion of frequent free text entries
- API endpoint for reporting on claim reasons
- Translation support
- Integration with CRM for sales outreach

## Success Criteria

1. Moderators can see why claims are being made
2. Admin users can manage dropdown options via Django admin
3. System captures both standardized (dropdown) and custom (free text) reasons
4. Sales team can identify claims driven by major brands for upselling opportunities