// Rules for the names a Spotlight partner types in. They mirror the checks
// the server makes, so a partner sees the problem before they submit. The
// server still has the final say.
export const SPOTLIGHT_NAME_MAX_LENGTH = 50;

export const SPOTLIGHT_NAME_RULES =
    'Use only lowercase letters, numbers and underscores, start with a ' +
    'letter, and keep it to 50 characters or fewer (for example ' +
    '"certification_status"). It cannot be changed after you save.';

export const SPOTLIGHT_DISPLAY_NAME_RULES =
    'This is the name people see on OS Hub, for example "Certification ' +
    'Status". Keep it to 50 characters or fewer. You can change it later.';

const INTERNAL_NAME_PATTERN = /^[a-z][a-z0-9_]*$/;

// Returns an error message, or null when the internal name is fine.
export const validateSpotlightInternalName = name => {
    if (!name) return 'Enter an internal name.';
    if (name.length > SPOTLIGHT_NAME_MAX_LENGTH) {
        return 'The internal name must be 50 characters or fewer.';
    }
    if (!INTERNAL_NAME_PATTERN.test(name)) {
        return (
            'The internal name must use only lowercase letters, numbers ' +
            'and underscores, and start with a letter (for example ' +
            '"certification_status").'
        );
    }
    return null;
};

// Returns an error message, or null when the display name is fine.
export const validateSpotlightDisplayName = displayName => {
    const trimmed = (displayName || '').trim();
    if (!trimmed) return 'Enter a display name.';
    if (trimmed.length > SPOTLIGHT_NAME_MAX_LENGTH) {
        return 'The display name must be 50 characters or fewer.';
    }
    return null;
};

// Where a field is in its life, in plain words for the partner.
export const getSpotlightFieldStatus = field => {
    if (!field.approved) return 'Waiting for approval';
    return field.active ? 'Active' : 'Approved, inactive';
};

export const SPOTLIGHT_DEFAULT_FIELD_TYPE = 'text';

export const SPOTLIGHT_FIELD_TYPE_HELP =
    'What kind of value this field holds. It cannot be changed after you ' +
    'save.';

// Example values shown in the preview, so a partner can see how each type
// of field reads on a production location page.
const EXAMPLE_VALUES = {
    text: 'Example text',
    date: '2026-06-15',
    number: '42',
    yes_no: 'Yes',
    score: '4.5 / 5',
    url: 'https://example.org',
};

// Turns a type into the example value the preview shows for it.
export const getSpotlightExampleValue = fieldType => {
    const example = EXAMPLE_VALUES[fieldType] || EXAMPLE_VALUES.text;
    if (fieldType === 'date') {
        return new Date(example).toLocaleDateString('en-US', {
            month: 'long',
            day: 'numeric',
            year: 'numeric',
            timeZone: 'UTC',
        });
    }
    return example;
};

// Looks up the label for a type, such as "Yes/No" for yes_no.
export const getSpotlightFieldTypeLabel = (fieldTypes, value) => {
    const match = (fieldTypes || []).find(type => type.value === value);
    return match ? match.label : value;
};

// The lines of the preview: the partner's saved fields, then the field they
// are typing now (when it has a display name), each with an example value.
export const getSpotlightPreviewRows = (fields, draft) => {
    const rows = fields.map(field => ({
        key: field.name,
        label: field.display_name,
        value: getSpotlightExampleValue(field.field_type),
    }));
    const draftLabel = ((draft && draft.displayName) || '').trim();
    if (draftLabel) {
        rows.push({
            key: '__draft__',
            label: draftLabel,
            value: getSpotlightExampleValue(draft.fieldType),
            isDraft: true,
        });
    }
    return rows;
};
