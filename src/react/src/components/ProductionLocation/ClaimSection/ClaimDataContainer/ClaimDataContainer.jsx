import React from 'react';
import { connect } from 'react-redux';
import { object, bool, string, number, arrayOf, shape, func } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import Switch from '@material-ui/core/Switch';
import Collapse from '@material-ui/core/Collapse';
import InfoOutlined from '@material-ui/icons/InfoOutlined';

import DataPoint from '../../DataPoint/DataPoint';
import { STATUS_CLAIMED } from '../../DataPoint/constants';
import IconComponent from '../../../Shared/IconComponent/IconComponent';
import LearnMoreLink from '../../Shared/LearnMoreLink/LearnMoreLink';
import BadgeClaimed from '../../../BadgeClaimed';
import {
    getClaimDisplayData,
    getIsClaimed,
} from '../../../../selectors/claimDataSelectors';
import { toggleSectionOpen } from '../../../../actions/sectionNavigation';
import {
    useScrollToSection,
    transitionDurationMs,
} from '../../PartnerSection/PartnerSectionItem/useScrollToSection';

import claimDataContainerStyles from './styles';

const SECTION_ID = 'operational-details';

const ClaimDataContainer = ({
    classes,
    className,
    isClaimed,
    hasDisplayableFields,
    displayableFields,
    contributorName,
    contributorUserId,
    claimedAt,
    isOpen,
    scrollTargetId,
    dispatch,
}) => {
    const containerRef = useScrollToSection(
        scrollTargetId,
        SECTION_ID,
        dispatch,
    );

    const handleToggle = () => dispatch(toggleSectionOpen(SECTION_ID));

    const handleKeyDown = event => {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            handleToggle();
        }
    };

    if (!isClaimed || !hasDisplayableFields) {
        return null;
    }

    return (
        <div
            id={SECTION_ID}
            ref={containerRef}
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
            <Collapse in={isOpen} timeout={transitionDurationMs}>
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
    isClaimed: bool.isRequired,
    hasDisplayableFields: bool,
    displayableFields: arrayOf(
        shape({
            key: string.isRequired,
            label: string.isRequired,
            getValue: func.isRequired,
        }),
    ).isRequired,
    contributorName: string,
    contributorUserId: number,
    claimedAt: string,
    isOpen: bool.isRequired,
    scrollTargetId: string,
    dispatch: func.isRequired,
};

ClaimDataContainer.defaultProps = {
    className: '',
    contributorName: null,
    contributorUserId: null,
    claimedAt: null,
    scrollTargetId: null,
    hasDisplayableFields: false,
};

const mapStateToProps = state => ({
    isClaimed: getIsClaimed(state),
    ...getClaimDisplayData(state),
    isOpen: !!state.sectionNavigation.openSectionIds[SECTION_ID],
    scrollTargetId: state.sectionNavigation.scrollTargetId,
});

export default connect(mapStateToProps)(
    withStyles(claimDataContainerStyles)(ClaimDataContainer),
);
