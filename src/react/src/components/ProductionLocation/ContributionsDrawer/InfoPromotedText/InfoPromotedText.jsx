import React from 'react';
import { object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';

import infoPromotedTextStyles from './styles';

const InfoPromotedText = ({ classes }) => (
    <>
        OS Hub automatically prioritizes data in this order: (1) claimed
        locations where owners/managers submitted data, (2) most frequently
        submitted values. The OS Hub team also actively moderates to promote
        quality data. To request reordering, email{' '}
        <a
            href="mailto:support@opensupplyhub.org"
            target="_blank"
            rel="noopener noreferrer"
            className={classes.supportLink}
        >
            Support
        </a>{' '}
        with the OS ID, preferred data entry, and justification.
    </>
);

InfoPromotedText.propTypes = {
    classes: object.isRequired,
};

export default withStyles(infoPromotedTextStyles)(InfoPromotedText);
