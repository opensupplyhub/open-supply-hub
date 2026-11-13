import React from 'react';
import { object, string } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';

import betaChipStyles from './styles';

export const BETA_CHIP_TEXT = 'Beta';

/**
 * The pill that marks a provisional dataset (OSDEV-3778). Rendered
 * beside a title rather than inside it, so the title text itself,
 * and anything derived from it such as analytics event names, is
 * unchanged.
 */
const BetaChip = ({ classes, className }) => {
    const chipClassName = [classes.chip, className].filter(Boolean).join(' ');

    return <span className={chipClassName}>{BETA_CHIP_TEXT}</span>;
};

BetaChip.propTypes = {
    classes: object.isRequired,
    className: string,
};

BetaChip.defaultProps = {
    className: undefined,
};

export default withStyles(betaChipStyles)(BetaChip);
