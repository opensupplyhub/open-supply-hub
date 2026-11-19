import React from 'react';
import { arrayOf, object, oneOf } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';

import InputErrorText from '../Contribute/InputErrorText';
import { CLAIM_LIVE_CHECK_FIXES } from './constants';
import { fieldFixesStyles } from './styles';

/*
 * The preset lines of the live check fixes that are about one field of
 * the pending claim edit page, shown in red directly under that field
 * (OSDEV-3805). Renders nothing when the field has no fix.
 */
const ClaimLiveCheckFieldFixes = ({ classes, fixes }) => {
    if (!fixes || fixes.length === 0) {
        return null;
    }
    return (
        <div
            className={classes.fieldFixes}
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
    classes: object.isRequired,
    fixes: arrayOf(oneOf(Object.keys(CLAIM_LIVE_CHECK_FIXES))),
};

export default withStyles(fieldFixesStyles)(ClaimLiveCheckFieldFixes);
