import React from 'react';
import { object, bool, shape, oneOfType, string } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import Divider from '@material-ui/core/Divider';
import InfoOutlined from '@material-ui/icons/InfoOutlined';

import DataPoint from '../../DataPoint/DataPoint';
import { STATUS_CLAIMED } from '../../DataPoint/constants';
import IconComponent from '../../../Shared/IconComponent/IconComponent';
import LearnMoreLink from '../../Shared/LearnMoreLink/LearnMoreLink';
import BadgeClaimed from '../../../BadgeClaimed';
import {
    getLocationFieldsConfig,
    hasDisplayableValue,
} from '../../../FacilityDetailsClaimedInfo/utils';

import claimDataContainerStyles from './styles';

const ClaimDataContainer = ({ classes, className, claimInfo, isClaimed }) => {
    if (!isClaimed || !claimInfo) {
        return null;
    }

    const { facility, contact, office } = claimInfo;

    const contributorName =
        typeof claimInfo.contributor === 'string'
            ? claimInfo.contributor
            : claimInfo.contributor?.name ?? null;

    const claimedAt = claimInfo.approved_at ?? claimInfo.created_at ?? null;

    const fieldsConfig = getLocationFieldsConfig(
        facility || {},
        contact || null,
        office || null,
    );

    const displayableFields = fieldsConfig.filter(field =>
        hasDisplayableValue(field.getValue()),
    );

    if (displayableFields.length === 0) {
        return null;
    }

    return (
        <div className={`${classes.container} ${className || ''}`}>
            <div className={classes.titleRow}>
                <span className={classes.titleIcon}>
                    <BadgeClaimed fontSize="20px" />
                </span>
                <Typography
                    variant="title"
                    className={classes.sectionTitle}
                    component="h3"
                >
                    Operational Details Submitted by Management
                </Typography>
                <IconComponent
                    title={
                        <>
                            Data provided by the production location management
                            through the claim process.
                            <LearnMoreLink href="https://info.opensupplyhub.org/resources/claim-a-facility" />
                        </>
                    }
                    icon={InfoOutlined}
                    className={classes.infoButton}
                />
            </div>
            <div className={classes.dataPointsList}>
                {displayableFields.map((field, index) => (
                    <React.Fragment key={field.key}>
                        <DataPoint
                            label={field.label}
                            value={field.getValue()}
                            statusLabel={STATUS_CLAIMED}
                            contributorName={contributorName}
                            date={claimedAt}
                        />
                        {index < displayableFields.length - 1 && (
                            <Divider className={classes.divider} />
                        )}
                    </React.Fragment>
                ))}
            </div>
        </div>
    );
};

ClaimDataContainer.propTypes = {
    classes: object.isRequired,
    className: string,
    claimInfo: shape({
        facility: object,
        contact: object,
        office: object,
        contributor: oneOfType([string, shape({ name: string })]),
        approved_at: string,
        created_at: string,
    }),
    isClaimed: bool,
};

ClaimDataContainer.defaultProps = {
    className: '',
    claimInfo: null,
    isClaimed: false,
};

export default withStyles(claimDataContainerStyles)(ClaimDataContainer);
