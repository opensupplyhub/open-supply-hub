import React, { useMemo } from 'react';
import { arrayOf, bool, func, object, oneOfType, string } from 'prop-types';
import InputLabel from '@material-ui/core/InputLabel';
import { withStyles } from '@material-ui/core/styles';

import IsicValuePicker from './IsicValuePicker';
import { isicOptions } from './utils';
import { inputSectionStyles } from '../../../util/styles';

// The ISIC field of the claimed-location editor, laid out like its other
// InputSections, from the claim's stored ISIC 4 / ISIC 5 values.
function IsicInputSection({ isic4, isic5, onChange, disabled, classes }) {
    const value = useMemo(
        () => ({ 4: isicOptions(isic4), 5: isicOptions(isic5) }),
        [isic4, isic5],
    );

    return (
        <div className={classes.inputSectionStyles}>
            <InputLabel className={classes.inputSectionLabelStyles}>
                Industry Classification (ISIC)
            </InputLabel>
            <IsicValuePicker
                value={value}
                onChange={onChange}
                disabled={disabled}
            />
        </div>
    );
}

IsicInputSection.defaultProps = {
    isic4: null,
    isic5: null,
    disabled: false,
};

IsicInputSection.propTypes = {
    isic4: oneOfType([arrayOf(object), string]),
    isic5: oneOfType([arrayOf(object), string]),
    onChange: func.isRequired,
    disabled: bool,
};

export default withStyles(inputSectionStyles)(IsicInputSection);
