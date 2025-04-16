import React, { useState } from 'react';
import { withStyles } from '@material-ui/core/styles';

import FacilityDetailsContributorsDrawer from './FacilityDetailsContributorsDrawer';
import FacilityDetailsShowContributorsButton from './FacilityDetailsShowContributorsButton';

import { splitContributorsIntoPublicAndNonPublic } from '../util/util';

const detailsStyles = theme =>
    Object.freeze({
        root: {
            color: '#191919',
            display: 'flex',
            justifyContent: 'center',
            borderTop: '2px solid #F9F7F7',
            paddingTop: theme.spacing.unit * 3,
        },
        contentContainer: {
            width: '100%',
            maxWidth: '1072px',
            paddingLeft: theme.spacing.unit * 3,
        },
    });

const FacilityDetailsContributors = ({ classes, contributors }) => {
    const [isOpen, setIsOpen] = useState(false);

    const visibleContributors = contributors.filter(
        c => !!c.contributor_name || !!c.name,
    );

    if (!visibleContributors.length) return null;

    const splittedContributors = splitContributorsIntoPublicAndNonPublic(
        visibleContributors,
    );

    return (
        <div className={classes.root}>
            <div className={classes.contentContainer}>
                <FacilityDetailsShowContributorsButton
                    publicContributorsNum={
                        splittedContributors.publicContributors.length
                    }
                    onOpen={() => setIsOpen(true)}
                />
            </div>
            <FacilityDetailsContributorsDrawer
                open={isOpen}
                onClose={() => setIsOpen(false)}
                splittedContributors={splittedContributors}
            />
        </div>
    );
};
export default withStyles(detailsStyles)(FacilityDetailsContributors);
