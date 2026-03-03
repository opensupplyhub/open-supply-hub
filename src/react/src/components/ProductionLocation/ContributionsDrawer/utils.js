import React from 'react';

/**
 * Return the default "Why is this data source displayed first?" info text (JSX).
 * @param {object} classes - withStyles classes (must include supportLink)
 * @returns {React.ReactNode}
 */
export function getInfoPromotedText(classes) {
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
