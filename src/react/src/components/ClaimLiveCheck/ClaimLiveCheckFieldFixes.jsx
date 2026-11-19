import React from 'react';
import { arrayOf, oneOf } from 'prop-types';

import InputErrorText from '../Contribute/InputErrorText';
import { CLAIM_LIVE_CHECK_FIXES } from './constants';

// The preset lines of the live check fixes about one field of the
// pending claim edit page, shown in red directly under that field.
const ClaimLiveCheckFieldFixes = ({ fixes }) => {
    if (!fixes) {
        return null;
    }
    return (
        <div
            style={{ display: 'grid', gap: 4, marginTop: 8 }}
            data-testid="live-check-field-fixes"
        >
            {fixes.map(fix => (
                <InputErrorText
                    key={fix}
                    text={CLAIM_LIVE_CHECK_FIXES[fix].text}
                />
            ))}
        </div>
    );
};

ClaimLiveCheckFieldFixes.defaultProps = {
    fixes: null,
};

ClaimLiveCheckFieldFixes.propTypes = {
    fixes: arrayOf(oneOf(Object.keys(CLAIM_LIVE_CHECK_FIXES))),
};

export default ClaimLiveCheckFieldFixes;
