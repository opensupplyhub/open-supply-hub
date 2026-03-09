import React, { useState, useMemo } from 'react';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Switch from '@material-ui/core/Switch';
import Collapse from '@material-ui/core/Collapse';
import InfoOutlined from '@material-ui/icons/InfoOutlined';
import IconComponent from '../../../Shared/IconComponent/IconComponent';
import { renderPartnerField } from '../../../PartnerFields/PartnerFieldsSection/utils.jsx';
import getIconURL from '../../Sidebar/NavBar/utils';

import parentSectionItemStyles from './styles';

const ParentSectionItem = ({ classes, group, partnerFields, facilityData }) => {
    const [isOpen, setIsOpen] = useState(false);
    const renderedFields = useMemo(() => {
        if (!isOpen || !partnerFields) return [];
        return partnerFields
            .map(field => renderPartnerField({ ...field, data: facilityData }))
            .filter(Boolean);
    }, [isOpen, partnerFields, facilityData]);

    return (
        <div className={classes.container}>
            <div
                className={classes.header}
                role="button"
                tabIndex={0}
                onClick={() => setIsOpen(prev => !prev)}
                onKeyDown={e => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        setIsOpen(prev => !prev);
                    }
                }}
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
                        onClick={e => e.stopPropagation()}
                        onKeyDown={e => e.stopPropagation()}
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
                        onChange={() => setIsOpen(prev => !prev)}
                        onClick={e => e.stopPropagation()}
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
                                <span className={classes.disclaimerLabel}>
                                    Disclaimer:
                                </span>{' '}
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

export default withStyles(parentSectionItemStyles)(ParentSectionItem);
