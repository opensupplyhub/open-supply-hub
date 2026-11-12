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
