import React from 'react';
import { object } from 'prop-types';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';

import { CLAIM_LIVE_CHECK_FIELD_LABELS, makeFixBannerTitle } from './constants';
import { fixBannerStyles } from './styles';
import { focusFixField } from './utils';

// The banner at the top of the pending claim edit page while the
// claim's latest check did not pass: one link per flagged field.
const ClaimLiveCheckFixBanner = ({ classes, fixesByField }) => {
    const fields = Object.keys(fixesByField);
    if (fields.length === 0) {
        return null;
    }
    const fixCount = fields.reduce(
        (count, field) => count + fixesByField[field].length,
        0,
    );
    return (
        <div className={classes.banner} role="status">
            <Typography component="h2" className={classes.bannerTitle}>
                {makeFixBannerTitle(fixCount)}
            </Typography>
            <ul className={classes.bannerLinks}>
                {fields.map(field => (
                    <li key={field}>
                        <Button
                            className={classes.bannerLink}
                            onClick={() =>
                                focusFixField(fixesByField[field][0])
                            }
                            disableRipple
                        >
                            {CLAIM_LIVE_CHECK_FIELD_LABELS[field]}
                        </Button>
                    </li>
                ))}
            </ul>
        </div>
    );
};

ClaimLiveCheckFixBanner.propTypes = {
    classes: object.isRequired,
    fixesByField: object.isRequired,
};

export default withStyles(fixBannerStyles)(ClaimLiveCheckFixBanner);
