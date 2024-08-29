import React, { useEffect } from 'react';
import { arrayOf, bool, func, node, string } from 'prop-types';
import { connect } from 'react-redux';
import CircularProgress from '@material-ui/core/CircularProgress';
import Typography from '@material-ui/core/Typography';
import Paper from '@material-ui/core/Paper';
import moment from 'moment';
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

import {
    makeProfileRouteLink,
    makeFacilityDetailLink,
    addProtocolToWebsiteURLIfMissing,
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
            {value || ''}
        </Typography>
    </div>
);
InfoSection.defaultProps = {
    value: null,
};

InfoSection.propTypes = {
    label: string.isRequired,
    value: node,
};

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
                    Created on {moment(data.created_at).format('LLL')} / Last
                    updated on {moment(data.updated_at).format('LLL')}
                </Typography>
            </div>
            <Paper style={dashboardClaimsDetailsStyles.containerStyles}>
                <InfoSection
                    label="Location Name"
                    value={
                        <Link
                            to={makeFacilityDetailLink(data.facility.id)}
                            href={makeFacilityDetailLink(data.facility.id)}
                        >
                            {data.facility.properties.name}
                        </Link>
                    }
                />
                <InfoSection
                    label="Claimant Account"
                    value={
                        <Link
                            to={makeProfileRouteLink(data.contributor.id)}
                            href={makeProfileRouteLink(data.contributor.id)}
                        >
                            {data.contributor.name}
                        </Link>
                    }
                />
                <InfoSection
                    label="Contact Person"
                    value={data.contact_person}
                />
                <InfoSection label="Claimant Title" value={data.job_title} />
                <InfoSection label="Account Email" value={data.email} />
                <InfoSection
                    label="Claimant's Website"
                    value={
                        data.website && (
                            <a
                                href={addProtocolToWebsiteURLIfMissing(
                                    data.website,
                                )}
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                {data.website}
                            </a>
                        )
                    }
                />
                <InfoSection
                    label="Production Location's Website"
                    value={
                        data.facility_website && (
                            <a
                                href={addProtocolToWebsiteURLIfMissing(
                                    data.facility_website,
                                )}
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                {data.facility_website}
                            </a>
                        )
                    }
                />

                <InfoSection
                    label="Production Location's LinkedIn"
                    value={
                        data.linkedin_profile && (
                            <a
                                href={addProtocolToWebsiteURLIfMissing(
                                    data.linkedin_profile,
                                )}
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                {data.linkedin_profile}
                            </a>
                        )
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
