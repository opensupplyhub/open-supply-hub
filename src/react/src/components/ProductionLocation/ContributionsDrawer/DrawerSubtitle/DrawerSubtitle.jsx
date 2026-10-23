import React from 'react';
import { object, string, number } from 'prop-types';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';

import drawerSubtitleStyles from './styles';

const DrawerSubtitle = ({
    classes,
    fieldName,
    contributorCount,
    mappedCount,
}) => {
    if (fieldName == null || fieldName === '') {
        return null;
    }
    const count = contributorCount;
    const orgText = `${
        count === 1 ? '1 organization has' : `${count} organizations have`
    } contributed data`;
    const mappedText = `${mappedCount} ${
        mappedCount === 1 ? 'value was' : 'values were'
    } mapped from OS Hub data`;
    // Mapped values have no organization behind them (OSDEV-3622).
    const sourcesText = [
        (count > 0 || mappedCount === 0) && orgText,
        mappedCount > 0 && mappedText,
    ]
        .filter(Boolean)
        .join(' and ');
    return (
        <Typography
            className={classes.subtitle}
            component="p"
            data-testid="contributions-drawer-subtitle"
        >
            {/* Values only mapped are mapped "to" a scheme. */}
            {sourcesText} {count === 0 && mappedCount > 0 ? 'to' : 'for'}{' '}
            <span className={classes.fieldName}>{fieldName}</span>
        </Typography>
    );
};

DrawerSubtitle.propTypes = {
    classes: object.isRequired,
    fieldName: string,
    contributorCount: number.isRequired,
    mappedCount: number,
};

DrawerSubtitle.defaultProps = {
    fieldName: null,
    mappedCount: 0,
};

export default withStyles(drawerSubtitleStyles)(DrawerSubtitle);
