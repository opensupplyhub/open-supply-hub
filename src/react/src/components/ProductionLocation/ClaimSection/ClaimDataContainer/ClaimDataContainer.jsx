import React, { useState } from 'react';
import { object, bool, shape, oneOfType, string } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import Switch from '@material-ui/core/Switch';
import InfoOutlined from '@material-ui/icons/InfoOutlined';
import filter from 'lodash/filter';
import get from 'lodash/get';
import isEmpty from 'lodash/isEmpty';
import isString from 'lodash/isString';

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
    const [isOpen, setIsOpen] = useState(true);

    if (!isClaimed || !claimInfo) {
        return null;
    }

    const { facility, contact, office } = claimInfo;

    const contributorName = isString(claimInfo.contributor)
        ? claimInfo.contributor
        : get(claimInfo, 'contributor.name', null);

    const claimedAt =
        get(claimInfo, 'approved_at') || get(claimInfo, 'created_at') || null;

    const fieldsConfig = getLocationFieldsConfig(
        facility || {},
        contact || null,
        office || null,
    );

    const displayableFields = filter(fieldsConfig, field =>
        hasDisplayableValue(field.getValue()),
    );

    if (isEmpty(displayableFields)) {
        return null;
    }

    return (
        <div
            id="operational-details"
            className={`${classes.container} ${className || ''}`}
        >
            <div className={classes.titleRow}>
                <BadgeClaimed className={classes.titleIcon} />
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
                    data-testid="claim-data-info-tooltip"
                />
                <div className={classes.switchWrap}>
                    <Typography
                        component="span"
                        className={classes.switchLabel}
                    >
                        <b>{isOpen ? 'Close' : 'Open'}</b>
                    </Typography>
                    <Switch
                        checked={isOpen}
                        onChange={e => setIsOpen(e.target.checked)}
                        color="primary"
                        size="small"
                        className={classes.switch}
                        inputProps={{
                            'aria-label':
                                'Show operational details submitted by management',
                        }}
                    />
                </div>
            </div>
            {isOpen && (
                <div className={classes.dataPointsList}>
                    {displayableFields.map(field => (
                        <React.Fragment key={field.key}>
                            <DataPoint
                                label={field.label}
                                value={field.getValue()}
                                statusLabel={STATUS_CLAIMED}
                                contributorName={contributorName}
                                date={claimedAt}
                            />
                        </React.Fragment>
                    ))}
                </div>
            )}
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
