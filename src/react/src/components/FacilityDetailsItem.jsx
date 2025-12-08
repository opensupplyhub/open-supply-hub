import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';

import FacilityDetailsDetail from './FacilityDetailsDetail';
import TitledDrawer from './TitledDrawer';
import ShowOnly from './ShowOnly';

const detailsStyles = theme =>
    Object.freeze({
        item: {
            paddingTop: theme.spacing.unit * 3,
        },
        label: {
            fontSize: '14px',
            textTransform: 'uppercase',
            fontWeight: 900,
        },
        button: {
            textTransform: 'none',
            fontWeight: 500,
            fontSize: '14px',
            padding: 0,
            lineHeight: '17px',
            textDecorationLine: 'underline',
        },
        itemWrapper: {
            paddingBottom: theme.spacing.unit * 3,
        },
    });

const FacilityDetailsItem = ({
    additionalContent,
    label,
    primary,
    lat,
    lng,
    locationLabeled,
    secondary,
    sourceBy,
    unit,
    jsonSchema,
    classes,
    embed,
    isVerified,
    isFromClaim,
    additionalContentText = 'entry',
    additionalContentTextPlural = 'entries',
    partnerConfigFields,
}) => {
    const [isOpen, setIsOpen] = useState(false);
    const hasAdditionalContent = !embed && !!additionalContent?.length;
    const additionalContentCount = additionalContent?.length;

    return (
        <div className={classes.item}>
            <div>
                <Typography className={classes.label}>{label}</Typography>
            </div>
            <FacilityDetailsDetail
                primary={primary}
                lat={lat}
                lng={lng}
                locationLabeled={locationLabeled}
                secondary={!embed ? secondary : null}
                sourceBy={!embed ? sourceBy : null}
                unit={!embed ? unit : null}
                jsonSchema={!embed ? jsonSchema : null}
                isVerified={isVerified}
                isFromClaim={isFromClaim}
                partnerConfigFields={partnerConfigFields}
            />
            <ShowOnly when={hasAdditionalContent}>
                <Button
                    color="primary"
                    className={classes.button}
                    onClick={() => {
                        if (!hasAdditionalContent) return;
                        setIsOpen(!isOpen);
                    }}
                >
                    {additionalContentCount} more{' '}
                    {additionalContentCount === 1
                        ? additionalContentText
                        : additionalContentTextPlural}
                </Button>
            </ShowOnly>
            <TitledDrawer
                open={isOpen}
                anchor="right"
                onClose={() => setIsOpen(false)}
                title={label}
                locationLabeled={locationLabeled}
                subtitle={`${
                    additionalContentCount + 1
                } ${additionalContentTextPlural}`}
            >
                <div className={classes.drawer}>
                    <div className={classes.itemWrapper}>
                        <FacilityDetailsDetail
                            primary={primary || `${lat}, ${lng}` || null}
                            secondary={!embed ? secondary : null}
                            sourceBy={!embed ? sourceBy : null}
                            unit={!embed ? unit : null}
                            jsonSchema={!embed ? jsonSchema : null}
                            isVerified={isVerified}
                            isFromClaim={isFromClaim}
                            partnerConfigFields={partnerConfigFields}
                        />
                    </div>
                    {isOpen &&
                        additionalContent.map(item => (
                            <div className={classes.itemWrapper} key={item.key}>
                                <FacilityDetailsDetail
                                    {...item}
                                    partnerConfigFields={partnerConfigFields}
                                />
                            </div>
                        ))}
                </div>
            </TitledDrawer>
        </div>
    );
};

FacilityDetailsItem.propTypes = {
    additionalContent: PropTypes.arrayOf(
        PropTypes.shape({
            key: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
        }),
    ),
    label: PropTypes.string,
    primary: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.node,
        PropTypes.object,
    ]),
    lat: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
    lng: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
    locationLabeled: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
    secondary: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
    sourceBy: PropTypes.string,
    unit: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
    jsonSchema: PropTypes.object,
    classes: PropTypes.object.isRequired,
    embed: PropTypes.bool,
    isVerified: PropTypes.bool,
    isFromClaim: PropTypes.bool,
    additionalContentText: PropTypes.string,
    additionalContentTextPlural: PropTypes.string,
    partnerConfigFields: PropTypes.shape({
        baseUrl: PropTypes.string,
        displayText: PropTypes.string,
    }),
};

FacilityDetailsItem.defaultProps = {
    additionalContent: [],
    label: '',
    primary: null,
    lat: null,
    lng: null,
    locationLabeled: null,
    secondary: null,
    sourceBy: null,
    unit: null,
    jsonSchema: null,
    embed: false,
    isVerified: false,
    isFromClaim: false,
    additionalContentText: 'entry',
    additionalContentTextPlural: 'entries',
    partnerConfigFields: null,
};

export default withStyles(detailsStyles)(FacilityDetailsItem);
