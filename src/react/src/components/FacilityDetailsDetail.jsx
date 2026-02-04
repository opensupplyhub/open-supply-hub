import React from 'react';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import Tooltip from '@material-ui/core/Tooltip';

import ShowOnly from './ShowOnly';
import BadgeVerified from './BadgeVerified';
import FeatureFlag from './FeatureFlag';
import PartnerFieldSchemaValue from './PartnerFields/PartnerFieldSchemaValue/PartnerFieldSchemaValue';

import { CLAIM_A_FACILITY } from '../util/constants';

const detailsStyles = theme =>
    Object.freeze({
        root: {
            display: 'flex',
            alignItems: 'center',
        },
        badgeWrapper: {
            paddingRight: theme.spacing.unit,
            paddingTop: theme.spacing.unit,
        },
        primaryText: {
            overflowWrap: 'anywhere',
            fontWeight: 500,
            fontSize: '18px',
            lineHeight: '21px',
            paddingTop: theme.spacing.unit,
        },
        secondaryText: {
            overflowWrap: 'anywhere',
            fontWeight: 500,
            fontSize: '14px',
            lineHeight: '17px',
            paddingTop: theme.spacing.unit,
        },
        sourceText: {
            overflowWrap: 'anywhere',
            fontWeight: 500,
            fontSize: '16px',
            lineHeight: '19px',
            paddingTop: theme.spacing.unit,
        },
        unitText: {
            display: 'inline-block',
            marginLeft: theme.spacing.unit,
            fontWeight: 400,
            fontSize: '18px',
            lineHeight: '21px',
            verticalAlign: 'baseline',
        },
    });

const CLAIM_EXPLANATORY_TEXT =
    'Please note: The OS Hub team has only verified that the person claiming a ' +
    'facility profile is connected to that facility. The OS Hub team has not ' +
    'verified any additional details added to a facility profile, e.g. ' +
    'certifications, production capabilities etc. Users interested in those ' +
    'details will need to carry out their own due diligence checks.';

const FacilityDetailsDetail = ({
    primary,
    locationLabeled,
    secondary,
    sourceBy,
    unit,
    jsonSchema,
    isVerified,
    isFromClaim,
    classes,
    partnerConfigFields,
}) => (
    <div className={classes.root} data-testid="facility-details-detail">
        <ShowOnly when={isVerified || isFromClaim}>
            <div className={classes.badgeWrapper}>
                <ShowOnly when={isVerified && !isFromClaim}>
                    <BadgeVerified />
                </ShowOnly>
                <FeatureFlag flag={CLAIM_A_FACILITY}>
                    <ShowOnly when={isFromClaim}>
                        <Tooltip title={CLAIM_EXPLANATORY_TEXT}>
                            <BadgeVerified />
                        </Tooltip>
                    </ShowOnly>
                </FeatureFlag>
            </div>
        </ShowOnly>
        <div>
            <Typography className={classes.primaryText} component="div">
                {jsonSchema ? (
                    <PartnerFieldSchemaValue
                        value={primary}
                        jsonSchema={jsonSchema}
                        partnerConfigFields={partnerConfigFields}
                    />
                ) : (
                    primary || locationLabeled
                )}
                {unit ? <span className={classes.unitText}>{unit}</span> : null}
            </Typography>
            {sourceBy ? (
                <Typography
                    className={classes.sourceText}
                    component="div"
                    dangerouslySetInnerHTML={{ __html: sourceBy }}
                />
            ) : null}
            {secondary ? (
                <Typography className={classes.secondaryText}>
                    {secondary}
                </Typography>
            ) : null}
        </div>
    </div>
);

FacilityDetailsDetail.propTypes = {
    primary: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.node,
        PropTypes.object,
    ]),
    locationLabeled: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
    secondary: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
    sourceBy: PropTypes.string,
    unit: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
    jsonSchema: PropTypes.object,
    isVerified: PropTypes.bool,
    isFromClaim: PropTypes.bool,
    partnerConfigFields: PropTypes.shape({
        baseUrl: PropTypes.string,
        displayText: PropTypes.string,
    }),
    classes: PropTypes.shape({
        root: PropTypes.string,
        badgeWrapper: PropTypes.string,
        primaryText: PropTypes.string,
        secondaryText: PropTypes.string,
        sourceText: PropTypes.string,
        unitText: PropTypes.string,
    }).isRequired,
};

FacilityDetailsDetail.defaultProps = {
    primary: null,
    locationLabeled: null,
    secondary: null,
    sourceBy: null,
    unit: null,
    jsonSchema: null,
    isVerified: false,
    isFromClaim: false,
    partnerConfigFields: null,
};

export default withStyles(detailsStyles)(FacilityDetailsDetail);
