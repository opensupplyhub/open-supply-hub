import React from 'react';
import { arrayOf, bool, string } from 'prop-types';
import Chip from '@material-ui/core/Chip';

import COLOURS from '../../../util/COLOURS';
import { STATUS_MAPPED } from '../DataPoint/constants';

const SCHEME = 'ISIC 4';

const chipStyle = (background, color, border = 'none') => ({
    background,
    color,
    border,
    borderRadius: 4,
    fontWeight: 600,
    marginLeft: 8,
});

const IsicValue = ({ titles, mapped, showPath }) => (
    <span data-testid="isic-value">
        <span data-testid="isic-value-text">
            {showPath
                ? titles
                      .filter((title, i) => title !== titles[i - 1])
                      .join(' › ')
                : titles[titles.length - 1]}
        </span>
        <Chip
            component="span"
            label={SCHEME}
            size="small"
            style={chipStyle(COLOURS.VERSION_TAG_BG, COLOURS.VERSION_TAG_TEXT)}
            data-testid="isic-scheme-tag"
        />
        {mapped && (
            <Chip
                component="span"
                label={STATUS_MAPPED}
                size="small"
                style={chipStyle(
                    COLOURS.MAPPED_CHIP_BG,
                    COLOURS.MAPPED_CHIP_TEXT,
                    `1px dashed ${COLOURS.MAPPED_CHIP_BORDER}`,
                )}
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
