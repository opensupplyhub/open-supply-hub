import React, { useState } from 'react';
import { object, bool, shape, oneOfType, string, number } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import Switch from '@material-ui/core/Switch';
import Collapse from '@material-ui/core/Collapse';
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
import sortClaimFields from './utils';

const ClaimDataContainer = ({ classes, className, claimInfo, isClaimed }) => {
    const [isOpen, setIsOpen] = useState(false);

    const handleToggle = () => setIsOpen(prev => !prev);

    const handleKeyDown = event => {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            handleToggle();
        }
    };

    if (!isClaimed || !claimInfo) {
        return null;
    }

    const { facility, contact, office } = claimInfo;

    const contributorName = isString(claimInfo.contributor)
        ? claimInfo.contributor
        : get(claimInfo, 'contributor.name', null);

    const contributorUserId = get(claimInfo, 'user_id', null);

    const claimedAt =
        get(claimInfo, 'approved_at') || get(claimInfo, 'created_at') || null;

    const fieldsConfig = getLocationFieldsConfig(
        facility || {},
        contact || null,
        office || null,
    );

    const displayableFields = sortClaimFields(
        filter(fieldsConfig, field => hasDisplayableValue(field.getValue())),
    );

    if (isEmpty(displayableFields)) {
        return null;
    }

    return (
        <div
            id="operational-details"
            className={`${classes.container} ${className || ''}`}
        >
            <div
                className={`${classes.header}${
                    isOpen ? ` ${classes.headerOpen}` : ''
                }`}
                role="button"
                tabIndex={0}
                onClick={handleToggle}
                onKeyDown={handleKeyDown}
            >
                <div className={classes.headerLeft}>
                    <BadgeClaimed className={classes.titleIcon} />
                    <Typography
                        variant="title"
                        className={classes.title}
                        component="h3"
                    >
                        Operational Details Submitted by Management
                    </Typography>
                    <div
                        onClick={event => event.stopPropagation()}
                        onKeyDown={event => event.stopPropagation()}
                        role="presentation"
                    >
                        <IconComponent
                            title={
                                <>
                                    Data provided by the production location
                                    management through the claim process.
                                    <LearnMoreLink href="https://info.opensupplyhub.org/resources/claim-a-facility" />
                                </>
                            }
                            icon={InfoOutlined}
                            className={classes.infoIcon}
                            data-testid="claim-data-info-tooltip"
                        />
                    </div>
                </div>
                <div className={classes.headerRight}>
                    <Typography className={classes.toggleLabel}>
                        {isOpen ? 'Close' : 'Open'}
                    </Typography>
                    <Switch
                        color="primary"
                        checked={isOpen}
                        onChange={handleToggle}
                        onClick={event => event.stopPropagation()}
                        className={classes.switchWrapper}
                        inputProps={{
                            'aria-label':
                                'Show operational details submitted by management',
                        }}
                    />
                </div>
            </div>
            <Collapse in={isOpen}>
                <div className={classes.dataPointsList}>
                    {displayableFields.map(field => (
                        <React.Fragment key={field.key}>
                            <DataPoint
                                label={field.label}
                                value={field.getValue()}
                                tooltipText={field.tooltipText}
                                statusLabel={STATUS_CLAIMED}
                                contributorName={contributorName}
                                userId={contributorUserId}
                                date={claimedAt}
                            />
                        </React.Fragment>
                    ))}
                </div>
            </Collapse>
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
        user_id: number,
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
