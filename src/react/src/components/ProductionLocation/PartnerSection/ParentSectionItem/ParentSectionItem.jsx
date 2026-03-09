import React, { useMemo, useEffect, useRef } from 'react';
import { connect } from 'react-redux';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Switch from '@material-ui/core/Switch';
import Collapse from '@material-ui/core/Collapse';
import InfoOutlined from '@material-ui/icons/InfoOutlined';
import IconComponent from '../../../Shared/IconComponent/IconComponent';
import { renderPartnerField } from '../../../PartnerFields/PartnerFieldsSection/utils.jsx';
import getIconURL from '../../Sidebar/NavBar/utils';
import {
    clearScrollTargetSection,
    toggleSectionOpen,
} from '../../../../actions/partnerFieldGroups';

import parentSectionItemStyles from './styles';

const ParentSectionItem = ({
    classes,
    group,
    partnerFields,
    facilityData,
    isOpen,
    scrollTargetId,
    dispatch,
}) => {
    const containerRef = useRef(null);

    useEffect(() => {
        if (scrollTargetId === group.uuid) {
            dispatch(clearScrollTargetSection());
            containerRef.current?.scrollIntoView({
                behavior: 'smooth',
                block: 'start',
            });
        }
    }, [scrollTargetId, group.uuid, dispatch]);

    const renderedFields = useMemo(() => {
        if (!isOpen || !partnerFields) return [];
        return partnerFields
            .map(field => renderPartnerField({ ...field, data: facilityData }))
            .filter(Boolean);
    }, [isOpen, partnerFields, facilityData]);

    const handleToggle = () => dispatch(toggleSectionOpen(group.uuid));

    const handleKeyDown = event => {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            handleToggle();
        }
    };

    return (
        <div className={classes.container} ref={containerRef}>
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
                    {group.icon_file && (
                        <img
                            src={getIconURL(group.icon_file)}
                            width={20}
                            height={20}
                            alt={group.name}
                            className={classes.iconImage}
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
                    />
                </div>
            </div>
            <Collapse in={isOpen}>
                <div className={classes.contentArea}>
                    {renderedFields.length > 0 && (
                        <Grid container>{renderedFields}</Grid>
                    )}
                    {group.description && (
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
    );
};

const mapStateToProps = (state, ownProps) => ({
    facilityData: state.facilities.singleFacility.data,
    scrollTargetId: state.partnerFieldGroups.scrollTargetId,
    isOpen: !!state.partnerFieldGroups.openSectionIds[ownProps.group.uuid],
});

export default connect(mapStateToProps)(
    withStyles(parentSectionItemStyles)(ParentSectionItem),
);
