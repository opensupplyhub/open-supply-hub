import React, { useMemo } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Collapse from '@material-ui/core/Collapse';
import InfoOutlined from '@material-ui/icons/InfoOutlined';
import Tab from '@material-ui/icons/Tab';
import IconComponent from '../../../Shared/IconComponent/IconComponent.jsx';
import ExpandToggleChevron from '../../../Shared/ExpandToggleChevron/ExpandToggleChevron.jsx';
import { getIconURL } from '../../Sidebar/NavBar/utils.js';
import { toggleSectionOpen } from '../../../../actions/sectionNavigation.js';
import parentSectionItemStyles from './styles.js';
import PartnerFieldItem from './PartnerFieldItem.jsx';
import {
    useScrollToSection,
    transitionDurationMs,
} from './useScrollToSection.jsx';

const emptyCKEditor5Field = '<p>&nbsp;</p>';

const PartnerSectionItem = ({
    classes,
    group,
    facilityData,
    isOpen,
    scrollTargetId,
    dispatch,
}) => {
    const containerRef = useScrollToSection(
        scrollTargetId,
        group.uuid,
        dispatch,
    );

    const columns = useMemo(() => {
        if (!group.partnerFields) return { left: [], right: [] };
        const mid = Math.ceil(group.partnerFields.length / 2);
        return {
            left: group.partnerFields.slice(0, mid),
            right: group.partnerFields.slice(mid),
        };
    }, [group]);

    const handleToggle = () => dispatch(toggleSectionOpen(group.uuid));

    const handleKeyDown = event => {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            handleToggle();
        }
    };

    const hasPartnerFields =
        columns.left.length > 0 || columns.right.length > 0;

    if (!hasPartnerFields) return null;

    return (
        <Grid
            item
            xs={12}
            key={group.uuid}
            id={group.uuid}
            className={classes.partnerSectionItem}
        >
            <div className={classes.container} ref={containerRef}>
                <div
                    className={`${classes.header}${
                        isOpen ? ` ${classes.headerOpen}` : ''
                    }`}
                    role="button"
                    tabIndex={0}
                    aria-expanded={isOpen}
                    onClick={handleToggle}
                    onKeyDown={handleKeyDown}
                >
                    <div className={classes.headerLeft}>
                        {group.icon_file ? (
                            <img
                                src={getIconURL(group.icon_file)}
                                width={20}
                                height={20}
                                alt={group.name}
                                className={classes.iconImage}
                            />
                        ) : (
                            <Tab
                                className={classes.iconImage}
                                style={{ height: 20, width: 20 }}
                            />
                        )}
                        <Typography
                            variant="title"
                            className={classes.title}
                            component="h3"
                        >
                            {group.name}
                        </Typography>
                        <div
                            onClick={event => event.stopPropagation()}
                            onKeyDown={event => event.stopPropagation()}
                            role="presentation"
                        >
                            {group.helper_text &&
                                group.helper_text !== emptyCKEditor5Field && (
                                    <IconComponent
                                        title={
                                            <span
                                                // eslint-disable-next-line react/no-danger
                                                dangerouslySetInnerHTML={{
                                                    __html: group.helper_text,
                                                }}
                                            />
                                        }
                                        icon={InfoOutlined}
                                        className={classes.infoIcon}
                                    />
                                )}
                        </div>
                    </div>
                    <div className={classes.headerRight}>
                        <span className={classes.toggleLabel}>
                            {isOpen ? 'Close' : 'Open'}
                        </span>
                        <ExpandToggleChevron
                            isExpanded={isOpen}
                            className={classes.chevron}
                            expandLessTestId="partner-section-expand-less"
                            expandMoreTestId="partner-section-expand-more"
                        />
                    </div>
                </div>
                <Collapse in={isOpen} timeout={transitionDurationMs}>
                    <div className={classes.contentArea}>
                        {hasPartnerFields && (
                            <Grid container spacing={8} alignItems="flex-start">
                                <Grid item xs={12} sm={6}>
                                    {columns.left.map(field => (
                                        <div
                                            className={classes.fieldItem}
                                            key={field.fieldName}
                                        >
                                            <PartnerFieldItem
                                                field={field}
                                                facilityData={facilityData}
                                                partnerGroupName={group.name}
                                            />
                                        </div>
                                    ))}
                                </Grid>
                                <Grid item xs={12} sm={6}>
                                    {columns.right.map(field => (
                                        <div
                                            className={classes.fieldItem}
                                            key={field.fieldName}
                                        >
                                            <PartnerFieldItem
                                                field={field}
                                                facilityData={facilityData}
                                                partnerGroupName={group.name}
                                            />
                                        </div>
                                    ))}
                                </Grid>
                            </Grid>
                        )}
                        {group.description &&
                            group.description !== emptyCKEditor5Field && (
                                <div className={classes.disclaimer}>
                                    <Typography
                                        component="div"
                                        className={classes.disclaimerText}
                                    >
                                        <span
                                            // eslint-disable-next-line react/no-danger
                                            dangerouslySetInnerHTML={{
                                                __html: group.description,
                                            }}
                                        />
                                    </Typography>
                                </div>
                            )}
                    </div>
                </Collapse>
            </div>
        </Grid>
    );
};

const partnerConfigFieldsPropType = PropTypes.oneOfType([
    PropTypes.shape({
        baseUrl: PropTypes.string,
        displayText: PropTypes.string,
    }),
    PropTypes.oneOf([null]),
]);

const partnerFieldForGroupPropType = PropTypes.shape({
    fieldName: PropTypes.string.isRequired,
    formatValue: PropTypes.func,
    label: PropTypes.string.isRequired,
    partnerConfigFields: partnerConfigFieldsPropType,
});

PartnerSectionItem.propTypes = {
    classes: PropTypes.object.isRequired,
    group: PropTypes.shape({
        uuid: PropTypes.string.isRequired,
        name: PropTypes.string.isRequired,
        icon_file: PropTypes.string,
        helper_text: PropTypes.string,
        description: PropTypes.string,
        partnerFields: PropTypes.arrayOf(partnerFieldForGroupPropType),
    }).isRequired,
    facilityData: PropTypes.object,
    isOpen: PropTypes.bool.isRequired,
    scrollTargetId: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.oneOf([null]),
    ]),
    dispatch: PropTypes.func.isRequired,
};

PartnerSectionItem.defaultProps = {
    facilityData: null,
    scrollTargetId: null,
};

const mapStateToProps = (state, ownProps) => ({
    facilityData: state.facilities.singleFacility.data,
    scrollTargetId: state.sectionNavigation.scrollTargetId,
    isOpen: !!state.sectionNavigation.openSectionIds[ownProps.group.uuid],
});

export default connect(mapStateToProps)(
    withStyles(parentSectionItemStyles)(PartnerSectionItem),
);
