import React from 'react';

export default function getInfoPromotedText(classes) {
    return (
        <>
            OS Hub automatically prioritizes data in this order: (1) claimed
            locations where owners/managers submitted data, (2) most frequently
            submitted values. The OS Hub team also actively moderates to promote
            quality data. To request reordering, email Support with the OS ID,
            preferred data entry, and justification.{' '}
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
}
