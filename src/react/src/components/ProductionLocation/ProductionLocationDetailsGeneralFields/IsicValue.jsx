import React from 'react';
import { arrayOf, bool, string } from 'prop-types';
import Chip from '@material-ui/core/Chip';

import COLOURS from '../../../util/COLOURS';

export const MAPPED_FROM_OS_HUB = 'Mapped from OS Hub';

const mappedBadgeStyle = {
    background: COLOURS.MAPPED_CHIP_BG,
    color: COLOURS.MAPPED_CHIP_TEXT,
    border: `1px dashed ${COLOURS.MAPPED_CHIP_BORDER}`,
    borderRadius: 4,
    fontWeight: 600,
    marginLeft: 8,
};

const IsicValue = ({ titles, mapped, showPath }) => (
    <span data-testid="isic-value">
        <span data-testid="isic-value-text">
            {showPath
                ? titles
                      .filter((title, i) => title !== titles[i - 1])
                      .join(' › ')
                : titles[titles.length - 1]}
        </span>
        {mapped && (
            <Chip
                component="span"
                label={MAPPED_FROM_OS_HUB}
                size="small"
                style={mappedBadgeStyle}
                data-testid="isic-mapped-badge"
            />
        )}
    </span>
);

IsicValue.propTypes = {
    titles: arrayOf(string).isRequired,
    mapped: bool,
    showPath: bool,
};

IsicValue.defaultProps = { mapped: false, showPath: false };

export default IsicValue;
