import React from 'react';
import { Link } from 'react-router-dom';
import { v4 as uuidv4 } from 'uuid';
import Typography from '@material-ui/core/Typography';

import { facilityDetailsPropType } from '../util/propTypes';

import { makeFacilityDetailLink, makeProfileRouteLink } from '../util/util';

const claimedFacilitiesDetailsSidebarStyles = Object.freeze({
    wrapperStyles: Object.freeze({
        marginLeft: '20px',
    }),
    containerStyles: Object.freeze({}),
    sectionStyles: Object.freeze({
        margin: '0 0 5px 0',
    }),
    bodyTextStyles: Object.freeze({
        margin: '10px 0',
    }),
});

export default function ClaimedFacilitiesDetailsSidebar({ facilityDetails }) {
    return (
        <div style={claimedFacilitiesDetailsSidebarStyles.wrapperStyles} s>
            <div style={claimedFacilitiesDetailsSidebarStyles.sectionStyles}>
                <Typography variant="title">
                    Contributed Facility Name
                </Typography>
                <Typography
                    variant="body1"
                    style={claimedFacilitiesDetailsSidebarStyles.bodyTextStyles}
                >
                    {facilityDetails.properties.name}
                </Typography>
            </div>
            <div style={claimedFacilitiesDetailsSidebarStyles.sectionStyles}>
                <Typography variant="title">OS ID</Typography>
                <Typography
                    variant="body1"
                    style={claimedFacilitiesDetailsSidebarStyles.bodyTextStyles}
                >
                    <Link
                        to={makeFacilityDetailLink(facilityDetails.id)}
                        href={makeFacilityDetailLink(facilityDetails.id)}
                    >
                        {facilityDetails.id}
                    </Link>
                </Typography>
            </div>
            <div style={claimedFacilitiesDetailsSidebarStyles.sectionStyles}>
                <Typography variant="title">Organizations</Typography>
                <ul
                    style={claimedFacilitiesDetailsSidebarStyles.bodyTextStyles}
                >
                    {facilityDetails.properties.contributors.map(
                        ({ id, name }) => {
                            const uniqueKey = uuidv4();
                            return (
                                <li key={uniqueKey}>
                                    <Link
                                        to={makeProfileRouteLink(id)}
                                        href={makeProfileRouteLink(id)}
                                        key={uniqueKey}
                                    >
                                        {name}
                                    </Link>
                                </li>
                            );
                        },
                    )}
                </ul>
            </div>
        </div>
    );
}

ClaimedFacilitiesDetailsSidebar.propTypes = {
    facilityDetails: facilityDetailsPropType.isRequired,
};
