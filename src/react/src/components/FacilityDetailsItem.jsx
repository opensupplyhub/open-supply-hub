/* eslint no-unused-vars: 0 */
import React, { useState } from 'react';
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
    urlReference,
}) => {
    const [isOpen, setIsOpen] = useState(false);
    const hasAdditionalContent = !embed && !!additionalContent?.length;
    const additionalContentCount = additionalContent?.length;

    console.log(
        `Additional content for ${label}: ${JSON.stringify(additionalContent)}`,
    );

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
                urlReference={urlReference}
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
                            urlReference={urlReference}
                            primary={primary || `${lat}, ${lng}` || null}
                            secondary={!embed ? secondary : null}
                            sourceBy={!embed ? sourceBy : null}
                            unit={!embed ? unit : null}
                            jsonSchema={!embed ? jsonSchema : null}
                            isVerified={isVerified}
                            isFromClaim={isFromClaim}
                        />
                    </div>
                    {isOpen &&
                        additionalContent.map(item => {
                            console.log('item: ', item);
                            return (
                                <div
                                    className={classes.itemWrapper}
                                    key={item.key}
                                >
                                    <FacilityDetailsDetail {...item} />
                                </div>
                            );
                        })}
                </div>
            </TitledDrawer>
        </div>
    );
};

export default withStyles(detailsStyles)(FacilityDetailsItem);
