import React, { useEffect } from 'react';
import { arrayOf, bool, func, node, string } from 'prop-types';
import { connect } from 'react-redux';
import CircularProgress from '@material-ui/core/CircularProgress';
import Typography from '@material-ui/core/Typography';
import Paper from '@material-ui/core/Paper';
import { Link, Route } from 'react-router-dom';

import DashboardClaimDetailsControls from './DashboardClaimDetailsControls';
import DashboardClaimsDetailsNote from './DashboardClaimsDetailsNote';
import DashboardClaimsDetailsAddNote from './DashboardClaimsDetailsAddNote';
import DashboardClaimsDetailsAttachments from './DashboardClaimsDetailsAttachments';

import {
    fetchSingleFacilityClaim,
    clearSingleFacilityClaim,
} from '../actions/claimFacilityDashboard';

import { facilityClaimPropType } from '../util/propTypes';
import { DATE_FORMATS } from '../util/constants';
import {
    makeProfileRouteLink,
    makeFacilityDetailLink,
    addProtocolToWebsiteURLIfMissing,
    formatDate,
} from '../util/util';

const dashboardClaimsDetailsStyles = Object.freeze({
    containerStyles: Object.freeze({
        width: '100%',
        display: 'flex',
        flexWrap: 'wrap',
    }),
    infoSectionStyles: Object.freeze({
        width: '40%',
        padding: '3%',
    }),
    dateStyles: Object.freeze({
        padding: '10px',
    }),
    notesHeaderStyles: Object.freeze({
        margin: '50px 0 0',
    }),
});

const defaultInfoSectionValueStyle = Object.freeze({
    padding: '10px 0',
    fontSize: '16px',
    whiteSpace: 'pre-line',
});

const InfoSection = ({ label, value }) => (
    <div style={dashboardClaimsDetailsStyles.infoSectionStyles}>
        <Typography variant="title">{label}</Typography>
        <Typography variant="body1" style={defaultInfoSectionValueStyle}>
            {value}
        </Typography>
    </div>
);

InfoSection.defaultProps = {
    value: '',
};

InfoSection.propTypes = {
    label: string.isRequired,
    value: node,
};

const createLink = (url, text) => (
    <Link to={url} href={url}>
        {text}
    </Link>
);

const createExternalLink = url => (
    <a
        href={addProtocolToWebsiteURLIfMissing(url)}
        target="_blank"
        rel="noopener noreferrer"
    >
        {url}
    </a>
);

function DashboardClaimsDetails({
    getFacilityClaim,
    clearFacilityClaim,
    data,
    fetching,
    error,
}) {
    useEffect(() => {
        getFacilityClaim();
        return clearFacilityClaim;
    }, [getFacilityClaim, clearFacilityClaim]);

    if (fetching) {
        return <CircularProgress />;
    }

    if (error) {
        return (
            <Typography>
                An error prevented fetching that facility claim.
            </Typography>
        );
    }

    if (!data) {
        return null;
    }

    return (
        <>
            <DashboardClaimDetailsControls data={data} />

            <div style={dashboardClaimsDetailsStyles.dateStyles}>
                <Typography variant="body2">
                    Created on{' '}
                    {formatDate(data.created_at, DATE_FORMATS.LONG_WITH_TIME)} /
                    Last updated on{' '}
                    {formatDate(data.updated_at, DATE_FORMATS.LONG_WITH_TIME)}
                </Typography>
            </div>

            <Paper style={dashboardClaimsDetailsStyles.containerStyles}>
                <InfoSection
                    label="Location Name"
                    value={createLink(
                        makeFacilityDetailLink(data.facility.id),
                        data.facility.properties.name,
                    )}
                />
                <InfoSection
                    label="Claimant Account"
                    value={createLink(
                        makeProfileRouteLink(data.contributor.id),
                        data.contributor.name,
                    )}
                />
                <InfoSection
                    label="Contact Person"
                    value={data.contact_person}
                />
                <InfoSection label="Claimant Title" value={data.job_title} />
                <InfoSection
                    label="Claim Reason"
                    value={data.claim_reason || 'Not specified'}
                />
                <InfoSection label="Account Email" value={data.email} />
                <InfoSection
                    label="Claimant's Website"
                    value={data.website && createExternalLink(data.website)}
                />
                <InfoSection
                    label="Production Location's Website"
                    value={
                        data.facility_website &&
                        createExternalLink(data.facility_website)
                    }
                />
                <InfoSection
                    label="Production Location's LinkedIn"
                    value={
                        data.linkedin_profile &&
                        createExternalLink(data.linkedin_profile)
                    }
                />
                <InfoSection
                    label="Sector(s)"
                    value={data.sector && data.sector.join(', ')}
                />
                <InfoSection
                    label="Number of Workers"
                    value={data.facility_workers_count}
                />
                <InfoSection
                    label="Local Language Name"
                    value={data.facility_name_native_language}
                />
            </Paper>

            <div style={dashboardClaimsDetailsStyles.notesHeaderStyles}>
                <Typography variant="title">
                    Facility Claim Review Notes
                </Typography>
            </div>

            <DashboardClaimsDetailsAttachments attachments={data.attachments} />

            {data.notes.map(note => (
                <DashboardClaimsDetailsNote key={note.id} note={note} />
            ))}

            <Route component={DashboardClaimsDetailsAddNote} />
        </>
    );
}

DashboardClaimsDetails.defaultProps = {
    data: null,
    error: null,
};

DashboardClaimsDetails.propTypes = {
    getFacilityClaim: func.isRequired,
    clearFacilityClaim: func.isRequired,
    data: facilityClaimPropType,
    fetching: bool.isRequired,
    error: arrayOf(string),
};

function mapStateToProps({
    claimFacilityDashboard: {
        detail: { data, fetching, error },
    },
}) {
    return {
        data,
        fetching,
        error,
    };
}

function mapDispatchToProps(
    dispatch,
    {
        match: {
            params: { claimID },
        },
    },
) {
    return {
        getFacilityClaim: () => dispatch(fetchSingleFacilityClaim(claimID)),
        clearFacilityClaim: () => dispatch(clearSingleFacilityClaim()),
    };
}

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(DashboardClaimsDetails);
