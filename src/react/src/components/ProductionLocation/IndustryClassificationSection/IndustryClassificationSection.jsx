import React, { useMemo } from 'react';
import { connect } from 'react-redux';
import { bool, func, object, string } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import Collapse from '@material-ui/core/Collapse';
import InfoOutlined from '@material-ui/icons/InfoOutlined';

import DataPoint from '../DataPoint/DataPoint';
import ContributionsDrawer from '../ContributionsDrawer/ContributionsDrawer';
import IconComponent from '../../Shared/IconComponent/IconComponent';
import ExpandToggleChevron from '../../Shared/ExpandToggleChevron/ExpandToggleChevron';
import getSelectedDrawerField from '../utils';
import useDrawerState from '../hooks';
import { INDUSTRY_CLASSIFICATION_SECTION } from '../constants.jsx';
import { toggleSectionOpen } from '../../../actions/sectionNavigation';
import {
    useScrollToSection,
    transitionDurationMs,
} from '../PartnerSection/PartnerSectionItem/useScrollToSection';
import { ENABLE_ISIC_TAXONOMY } from '../../../util/constants';
import getIndustryClassificationFields from './utils';
import claimDataContainerStyles from '../ClaimSection/ClaimDataContainer/styles';

const SECTION_ID = 'industry-classification';

/*
Industry Classification (OSDEV-3622), after Operational Details and opening
and closing the same way. Shown while the ISIC switch is on and the
location has ISIC data.
*/
const IndustryClassificationSection = ({
    classes,
    className,
    data,
    isicEnabled,
    isOpen,
    scrollTargetId,
    dispatch,
}) => {
    const containerRef = useScrollToSection(
        scrollTargetId,
        SECTION_ID,
        dispatch,
    );
    const [
        openDrawerFieldKey,
        isDrawerOpen,
        openDrawer,
        closeDrawer,
    ] = useDrawerState(null);
    const fields = useMemo(() => getIndustryClassificationFields(data), [data]);
    const selectedDrawerField = getSelectedDrawerField(
        fields,
        openDrawerFieldKey,
    );

    if (!isicEnabled || !fields.length) {
        return null;
    }

    const handleToggle = () => dispatch(toggleSectionOpen(SECTION_ID));
    const handleKeyDown = event => {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            handleToggle();
        }
    };

    return (
        <div
            id={SECTION_ID}
            ref={containerRef}
            className={`${classes.container} ${className}`}
            data-testid="industry-classification-section"
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
                    <Typography
                        variant="title"
                        className={classes.title}
                        component="h3"
                    >
                        {INDUSTRY_CLASSIFICATION_SECTION.label}
                    </Typography>
                    <div
                        onClick={event => event.stopPropagation()}
                        onKeyDown={event => event.stopPropagation()}
                        role="presentation"
                    >
                        <IconComponent
                            title={INDUSTRY_CLASSIFICATION_SECTION.description}
                            icon={InfoOutlined}
                            className={classes.infoIcon}
                        />
                    </div>
                </div>
                <div className={classes.headerRight}>
                    <Typography className={classes.toggleLabel}>
                        {isOpen ? 'Close' : 'Open'}
                    </Typography>
                    <ExpandToggleChevron
                        isExpanded={isOpen}
                        className={classes.chevron}
                        expandLessTestId="industry-classification-expand-less"
                        expandMoreTestId="industry-classification-expand-more"
                    />
                </div>
            </div>
            <Collapse in={isOpen} timeout={transitionDurationMs}>
                <div className={classes.dataPointsList}>
                    {fields.map(field => (
                        <DataPoint
                            key={field.key}
                            label={field.label}
                            value={field.value}
                            tooltipText={field.tooltipText}
                            statusLabel={field.statusLabel}
                            contributorName={field.contributorName}
                            userId={field.userId}
                            date={field.date}
                            drawerData={field.drawerData}
                            onOpenDrawer={() => openDrawer(field.key)}
                            multiline
                        />
                    ))}
                </div>
            </Collapse>
            <ContributionsDrawer
                open={isDrawerOpen}
                onClose={closeDrawer}
                fieldName={selectedDrawerField?.label}
                promotedContribution={
                    selectedDrawerField?.drawerData?.promotedContribution
                }
                contributions={
                    selectedDrawerField?.drawerData?.contributions ?? []
                }
            />
        </div>
    );
};

IndustryClassificationSection.propTypes = {
    classes: object.isRequired,
    className: string,
    data: object,
    isicEnabled: bool.isRequired,
    isOpen: bool.isRequired,
    scrollTargetId: string,
    dispatch: func.isRequired,
};

IndustryClassificationSection.defaultProps = {
    className: '',
    data: null,
    scrollTargetId: null,
};

const mapStateToProps = ({
    featureFlags: { flags },
    sectionNavigation: { openSectionIds, scrollTargetId },
}) => ({
    isicEnabled: !!flags[ENABLE_ISIC_TAXONOMY],
    isOpen: !!openSectionIds[SECTION_ID],
    scrollTargetId,
});

export default connect(mapStateToProps)(
    withStyles(claimDataContainerStyles)(IndustryClassificationSection),
);
