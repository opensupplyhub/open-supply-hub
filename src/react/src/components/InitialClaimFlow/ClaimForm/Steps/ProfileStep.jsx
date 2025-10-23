import React, { useState, useEffect } from 'react';
import { func, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import TextField from '@material-ui/core/TextField';
import ExpansionPanel from '@material-ui/core/ExpansionPanel';
import ExpansionPanelSummary from '@material-ui/core/ExpansionPanelSummary';
import ExpansionPanelDetails from '@material-ui/core/ExpansionPanelDetails';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import Business from '@material-ui/icons/Business';
import Build from '@material-ui/icons/Build';
import Nature from '@material-ui/icons/Nature';
import VerifiedUser from '@material-ui/icons/VerifiedUser';
import Tooltip from '@material-ui/core/Tooltip';
import HelpOutline from '@material-ui/icons/HelpOutline';
import Star from '@material-ui/icons/Star';
import IconButton from '@material-ui/core/IconButton';

import COLOURS from '../../../../util/COLOURS';
import StyledSelect from '../../../Filters/StyledSelect';
import withScrollReset from '../../HOCs/withScrollReset';
import FreeEmissionsEstimate from '../../../FreeEmissionsEstimate/FreeEmissionsEstimate';
import { mockedSectors } from '../../../../util/constants';
import {
    mapDjangoChoiceTuplesToSelectOptions,
    mapFacilityTypeOptions,
    mapProcessingTypeOptions,
} from '../../../../util/util';

// TODO: Move these to constants file
const BETA_TOOLTIP_TEXT =
    "What does beta mean? Open Supply Hub is developing a Premium offering for facilities, to help you use your OS Hub profile to connect with more customers and build your business. Once live, all fields that say beta will be a part of this new package. For now, these beta fields will appear on your profile just like all the others. Once the Premium offering is live, you'll receive next steps about how it will work and whether you will want to keep these beta fields live.";

const AFFILIATIONS_OPTIONS = [
    { value: 'fla', label: 'Fair Labor Association (FLA)' },
    { value: 'wrap', label: 'WRAP' },
    { value: 'sedex', label: 'Sedex' },
    { value: 'bsci', label: 'BSCI' },
];

const CERTIFICATIONS_OPTIONS = [
    { value: 'iso_9001', label: 'ISO 9001' },
    { value: 'iso_14001', label: 'ISO 14001' },
    { value: 'sa8000', label: 'SA8000' },
    { value: 'oeko_tex', label: 'OEKO-TEX' },
    { value: 'gots', label: 'GOTS (Global Organic Textile Standard)' },
    { value: 'bluesign', label: 'bluesign' },
];

const profileStepStyles = theme =>
    Object.freeze({
        expansionPanel: Object.freeze({
            marginBottom: theme.spacing.unit * 2,
            boxShadow: 'none',
            border: `1px solid ${COLOURS.GREY}`,
            '&:before': {
                display: 'none',
            },
        }),
        expansionPanelSummary: Object.freeze({
            padding: `${theme.spacing.unit * 2}px ${theme.spacing.unit * 2}px`,
            '&:hover': {
                backgroundColor: 'transparent',
            },
        }),
        sectionIconWrapper: Object.freeze({
            padding: theme.spacing.unit,
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginRight: theme.spacing.unit * 1.5,
        }),
        blueBg: Object.freeze({
            backgroundColor: COLOURS.EXTRA_LIGHT_BLUE,
        }),
        amberBg: Object.freeze({
            backgroundColor: '#fff8e1',
        }),
        purpleBg: Object.freeze({
            backgroundColor: COLOURS.LIGHT_PURPLE_BG,
        }),
        greenBg: Object.freeze({
            backgroundColor: COLOURS.LIGHT_GREEN,
        }),
        sectionIcon: Object.freeze({
            fontSize: '1.25rem',
        }),
        blueIcon: Object.freeze({
            color: COLOURS.MATERIAL_BLUE,
        }),
        amberIcon: Object.freeze({
            color: '#f57c00',
        }),
        purpleIcon: Object.freeze({
            color: COLOURS.DARK_PURPLE,
        }),
        greenIcon: Object.freeze({
            color: COLOURS.MATERIAL_GREEN,
        }),
        sectionHeader: Object.freeze({
            display: 'flex',
            alignItems: 'flex-start',
        }),
        sectionTitleWrapper: Object.freeze({
            flex: 1,
        }),
        sectionTitle: Object.freeze({
            fontWeight: 600,
            fontSize: '22px',
            marginBottom: theme.spacing.unit / 2,
        }),
        sectionDescription: Object.freeze({
            fontSize: '16px',
            color: COLOURS.DARK_GREY,
        }),
        expansionPanelDetails: Object.freeze({
            padding: `${theme.spacing.unit * 2}px ${theme.spacing.unit * 3}px ${
                theme.spacing.unit * 3
            }px`,
            display: 'block',
        }),
        field: Object.freeze({
            marginBottom: theme.spacing.unit * 3,
        }),
        fieldLabel: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            marginBottom: theme.spacing.unit,
            fontSize: '16px',
            '& .MuiTypography-root': {
                fontSize: '16px',
            },
        }),
        helpIcon: Object.freeze({
            fontSize: '1rem',
            color: COLOURS.DARK_GREY,
            marginLeft: theme.spacing.unit / 2,
        }),
        helpIconButton: Object.freeze({
            padding: 0,
            '&:hover': {
                backgroundColor: 'transparent',
            },
        }),
        betaLabel: Object.freeze({
            display: 'inline-flex',
            alignItems: 'center',
            padding: '2px 10px',
            borderRadius: '12px',
            background: 'linear-gradient(90deg, #7B2CBF 0%, #E91E63 100%)',
            color: COLOURS.WHITE,
            fontSize: '12px',
            fontWeight: 600,
            marginLeft: theme.spacing.unit,
            cursor: 'pointer',
        }),
        betaIcon: Object.freeze({
            fontSize: '12px',
            marginRight: '2px',
        }),
        tooltip: Object.freeze({
            fontSize: '14px',
            backgroundColor: COLOURS.WHITE,
            color: 'rgba(0, 0, 0, 0.87)',
            border: `1px solid ${COLOURS.GREY}`,
            padding: theme.spacing.unit * 1.5,
            maxWidth: 300,
        }),
        subsectionTitle: Object.freeze({
            fontWeight: 500,
            fontSize: '16px',
            marginBottom: theme.spacing.unit * 2,
            marginTop: theme.spacing.unit * 2,
        }),
        subsectionSubtitle: Object.freeze({
            color: COLOURS.DARK_GREY,
            fontWeight: 'normal',
        }),
    });

const ProfileStep = ({
    classes,
    formData,
    handleChange,
    touched,
    errors,
    countryOptions,
    processingTypeOptions,
}) => {
    const [
        freeEmissionsEstimateHasErrors,
        setFreeEmissionsEstimateHasErrors,
    ] = useState(false);

    const [enabledTaxonomy, setEnabledTaxonomy] = useState(false);

    useEffect(() => {
        console.log(freeEmissionsEstimateHasErrors);
    }, [freeEmissionsEstimateHasErrors]);

    useEffect(() => {
        setEnabledTaxonomy(
            formData.sector &&
                formData.sector.length === 1 &&
                formData.sector[0].value === 'Apparel',
        );
    }, [formData.sector]);

    return (
        <Grid container spacing={24}>
            <Grid item xs={12}>
                {/* Section 1: Production Location Overview */}
                <ExpansionPanel
                    className={classes.expansionPanel}
                    defaultExpanded
                >
                    <ExpansionPanelSummary
                        expandIcon={<ExpandMoreIcon />}
                        className={classes.expansionPanelSummary}
                    >
                        <div className={classes.sectionHeader}>
                            <div
                                className={`${classes.sectionIconWrapper} ${classes.blueBg}`}
                            >
                                <Business
                                    className={`${classes.sectionIcon} ${classes.blueIcon}`}
                                />
                            </div>
                            <div className={classes.sectionTitleWrapper}>
                                <Typography className={classes.sectionTitle}>
                                    Production Location Overview
                                </Typography>
                                <Typography
                                    className={classes.sectionDescription}
                                >
                                    Basic facility identification and contact
                                    information
                                </Typography>
                            </div>
                        </div>
                    </ExpansionPanelSummary>
                    <ExpansionPanelDetails
                        className={classes.expansionPanelDetails}
                    >
                        {/* Local Language Name */}
                        <div className={classes.field}>
                            <div className={classes.fieldLabel}>
                                <Typography
                                    variant="body2"
                                    component="label"
                                    style={{ fontSize: '16px' }}
                                >
                                    Production Location Name in Native Language
                                </Typography>
                                <Tooltip
                                    title="Enter the production location name in the local language if different from the English name"
                                    placement="top"
                                    classes={{ tooltip: classes.tooltip }}
                                >
                                    <IconButton
                                        size="small"
                                        disableRipple
                                        className={classes.helpIconButton}
                                    >
                                        <HelpOutline
                                            className={classes.helpIcon}
                                        />
                                    </IconButton>
                                </Tooltip>
                            </div>
                            <TextField
                                fullWidth
                                variant="outlined"
                                value={formData.localLanguageName || ''}
                                onChange={e =>
                                    handleChange(
                                        'localLanguageName',
                                        e.target.value,
                                    )
                                }
                                placeholder="Enter location name in native language (if different from English)"
                                error={
                                    touched.localLanguageName &&
                                    !!errors.localLanguageName
                                }
                                helperText={
                                    touched.localLanguageName &&
                                    errors.localLanguageName
                                }
                            />
                        </div>

                        <Grid container spacing={24}>
                            {/* Facility Phone */}
                            <Grid item xs={12} md={6}>
                                <div className={classes.field}>
                                    <div className={classes.fieldLabel}>
                                        <Typography
                                            variant="body2"
                                            component="label"
                                            style={{ fontSize: '16px' }}
                                        >
                                            Company Phone
                                        </Typography>
                                        <Tooltip
                                            title={BETA_TOOLTIP_TEXT}
                                            placement="top"
                                            classes={{
                                                tooltip: classes.tooltip,
                                            }}
                                        >
                                            <div className={classes.betaLabel}>
                                                <Star
                                                    className={classes.betaIcon}
                                                />
                                                BETA
                                            </div>
                                        </Tooltip>
                                        <Tooltip
                                            title="Main phone number for contacting this production location directly"
                                            placement="top"
                                            classes={{
                                                tooltip: classes.tooltip,
                                            }}
                                        >
                                            <IconButton
                                                size="small"
                                                disableRipple
                                                className={
                                                    classes.helpIconButton
                                                }
                                            >
                                                <HelpOutline
                                                    className={classes.helpIcon}
                                                />
                                            </IconButton>
                                        </Tooltip>
                                    </div>
                                    <TextField
                                        fullWidth
                                        variant="outlined"
                                        value={formData.facilityPhone || ''}
                                        onChange={e =>
                                            handleChange(
                                                'facilityPhone',
                                                e.target.value,
                                            )
                                        }
                                        placeholder="+1 (555) 123-4567"
                                    />
                                </div>
                            </Grid>

                            {/* Facility Website */}
                            <Grid item xs={12} md={6}>
                                <div className={classes.field}>
                                    <div className={classes.fieldLabel}>
                                        <Typography
                                            variant="body2"
                                            component="label"
                                            style={{ fontSize: '16px' }}
                                        >
                                            Company Website
                                        </Typography>
                                        <Tooltip
                                            title="Official website URL for this specific production location (if available)"
                                            placement="top"
                                            classes={{
                                                tooltip: classes.tooltip,
                                            }}
                                        >
                                            <IconButton
                                                size="small"
                                                disableRipple
                                                className={
                                                    classes.helpIconButton
                                                }
                                            >
                                                <HelpOutline
                                                    className={classes.helpIcon}
                                                />
                                            </IconButton>
                                        </Tooltip>
                                    </div>
                                    <TextField
                                        fullWidth
                                        variant="outlined"
                                        value={formData.facilityWebsite || ''}
                                        onChange={e =>
                                            handleChange(
                                                'facilityWebsite',
                                                e.target.value,
                                            )
                                        }
                                        placeholder="https://company.com"
                                    />
                                </div>
                            </Grid>
                        </Grid>

                        {/* Description */}
                        <div className={classes.field}>
                            <div className={classes.fieldLabel}>
                                <Typography
                                    variant="body2"
                                    component="label"
                                    style={{ fontSize: '16px' }}
                                >
                                    Production Location Description
                                </Typography>
                                <Tooltip
                                    title={BETA_TOOLTIP_TEXT}
                                    placement="top"
                                    classes={{ tooltip: classes.tooltip }}
                                >
                                    <div className={classes.betaLabel}>
                                        <Star className={classes.betaIcon} />
                                        BETA
                                    </div>
                                </Tooltip>
                                <Tooltip
                                    title="Provide a brief overview of what this production location manufactures and its main business activities"
                                    placement="top"
                                    classes={{ tooltip: classes.tooltip }}
                                >
                                    <IconButton
                                        size="small"
                                        disableRipple
                                        className={classes.helpIconButton}
                                    >
                                        <HelpOutline
                                            className={classes.helpIcon}
                                        />
                                    </IconButton>
                                </Tooltip>
                            </div>
                            <TextField
                                fullWidth
                                multiline
                                rows={4}
                                variant="outlined"
                                value={formData.description || ''}
                                onChange={e =>
                                    handleChange('description', e.target.value)
                                }
                                placeholder="Brief description of what this production location produces or its main activities"
                            />
                        </div>
                    </ExpansionPanelDetails>
                </ExpansionPanel>

                {/* Section 2: Company Information */}
                <ExpansionPanel
                    className={classes.expansionPanel}
                    defaultExpanded
                >
                    <ExpansionPanelSummary
                        expandIcon={<ExpandMoreIcon />}
                        className={classes.expansionPanelSummary}
                    >
                        <div className={classes.sectionHeader}>
                            <div
                                className={`${classes.sectionIconWrapper} ${classes.amberBg}`}
                            >
                                <Business
                                    className={`${classes.sectionIcon} ${classes.amberIcon}`}
                                />
                            </div>
                            <div className={classes.sectionTitleWrapper}>
                                <Typography className={classes.sectionTitle}>
                                    Company Information
                                </Typography>
                                <Typography
                                    className={classes.sectionDescription}
                                >
                                    Parent company and office information
                                </Typography>
                            </div>
                        </div>
                    </ExpansionPanelSummary>
                    <ExpansionPanelDetails
                        className={classes.expansionPanelDetails}
                    >
                        {/* Parent Company Information */}
                        <Typography className={classes.subsectionTitle}>
                            Parent Company / Owner Information
                        </Typography>

                        <Grid container spacing={16}>
                            <Grid item xs={12} md={6}>
                                <div className={classes.field}>
                                    <div className={classes.fieldLabel}>
                                        <Typography
                                            variant="body2"
                                            component="label"
                                            style={{ fontSize: '16px' }}
                                        >
                                            Parent Company Name / Supplier Group
                                        </Typography>
                                        <Tooltip
                                            title="The name of the parent company or corporate group that owns this production location"
                                            placement="top"
                                            classes={{
                                                tooltip: classes.tooltip,
                                            }}
                                        >
                                            <IconButton
                                                size="small"
                                                disableRipple
                                                className={
                                                    classes.helpIconButton
                                                }
                                            >
                                                <HelpOutline
                                                    className={classes.helpIcon}
                                                />
                                            </IconButton>
                                        </Tooltip>
                                    </div>
                                    <TextField
                                        fullWidth
                                        variant="outlined"
                                        value={formData.parentCompanyName || ''}
                                        onChange={e =>
                                            handleChange(
                                                'parentCompanyName',
                                                e.target.value,
                                            )
                                        }
                                        placeholder="Parent company name"
                                    />
                                </div>
                            </Grid>
                        </Grid>

                        {/* Office Information */}
                        <Typography className={classes.subsectionTitle}>
                            Office Information{' '}
                            <span className={classes.subsectionSubtitle}>
                                (if different from production location)
                            </span>
                        </Typography>

                        <Grid container spacing={16}>
                            <Grid item xs={12} md={6}>
                                <div className={classes.field}>
                                    <div className={classes.fieldLabel}>
                                        <Typography
                                            variant="body2"
                                            component="label"
                                            style={{ fontSize: '16px' }}
                                        >
                                            Office Name
                                        </Typography>
                                        <Tooltip
                                            title="Name of the corporate office or headquarters"
                                            placement="top"
                                            classes={{
                                                tooltip: classes.tooltip,
                                            }}
                                        >
                                            <IconButton
                                                size="small"
                                                disableRipple
                                                className={
                                                    classes.helpIconButton
                                                }
                                            >
                                                <HelpOutline
                                                    className={classes.helpIcon}
                                                />
                                            </IconButton>
                                        </Tooltip>
                                    </div>
                                    <TextField
                                        fullWidth
                                        variant="outlined"
                                        value={formData.officeName || ''}
                                        onChange={e =>
                                            handleChange(
                                                'officeName',
                                                e.target.value,
                                            )
                                        }
                                        placeholder="Office name"
                                    />
                                </div>
                            </Grid>
                            <Grid item xs={12} md={6}>
                                <div className={classes.field}>
                                    <div className={classes.fieldLabel}>
                                        <Typography
                                            variant="body2"
                                            component="label"
                                            style={{ fontSize: '16px' }}
                                        >
                                            Office Address
                                        </Typography>
                                        <Tooltip
                                            title="Physical address of the office location"
                                            placement="top"
                                            classes={{
                                                tooltip: classes.tooltip,
                                            }}
                                        >
                                            <IconButton
                                                size="small"
                                                disableRipple
                                                className={
                                                    classes.helpIconButton
                                                }
                                            >
                                                <HelpOutline
                                                    className={classes.helpIcon}
                                                />
                                            </IconButton>
                                        </Tooltip>
                                    </div>
                                    <TextField
                                        fullWidth
                                        variant="outlined"
                                        value={formData.officeAddress || ''}
                                        onChange={e =>
                                            handleChange(
                                                'officeAddress',
                                                e.target.value,
                                            )
                                        }
                                        placeholder="Office address"
                                    />
                                </div>
                            </Grid>
                            <Grid item xs={12} md={6}>
                                <div className={classes.field}>
                                    <div className={classes.fieldLabel}>
                                        <Typography
                                            variant="body2"
                                            component="label"
                                            style={{ fontSize: '16px' }}
                                        >
                                            Office Country
                                        </Typography>
                                        <Tooltip
                                            title="Country where the office is located"
                                            placement="top"
                                            classes={{
                                                tooltip: classes.tooltip,
                                            }}
                                        >
                                            <IconButton
                                                size="small"
                                                disableRipple
                                                className={
                                                    classes.helpIconButton
                                                }
                                            >
                                                <HelpOutline
                                                    className={classes.helpIcon}
                                                />
                                            </IconButton>
                                        </Tooltip>
                                    </div>
                                    <StyledSelect
                                        id="officeCountry"
                                        name="officeCountry"
                                        aria-label="Office Country"
                                        options={countryOptions || []}
                                        value={formData.officeCountry || null}
                                        onChange={value =>
                                            handleChange('officeCountry', value)
                                        }
                                        placeholder="Select country..."
                                    />
                                </div>
                            </Grid>
                        </Grid>
                    </ExpansionPanelDetails>
                </ExpansionPanel>

                {/* Section 3: Operations & Capabilities */}
                <ExpansionPanel
                    className={classes.expansionPanel}
                    defaultExpanded
                >
                    <ExpansionPanelSummary
                        expandIcon={<ExpandMoreIcon />}
                        className={classes.expansionPanelSummary}
                    >
                        <div className={classes.sectionHeader}>
                            <div
                                className={`${classes.sectionIconWrapper} ${classes.blueBg}`}
                            >
                                <Build
                                    className={`${classes.sectionIcon} ${classes.blueIcon}`}
                                />
                            </div>
                            <div className={classes.sectionTitleWrapper}>
                                <Typography className={classes.sectionTitle}>
                                    Operations & Capabilities
                                </Typography>
                                <Typography
                                    className={classes.sectionDescription}
                                >
                                    Production and operations details for your
                                    location
                                </Typography>
                            </div>
                        </div>
                    </ExpansionPanelSummary>
                    <ExpansionPanelDetails
                        className={classes.expansionPanelDetails}
                    >
                        <Grid container spacing={24}>
                            {/* Sector */}
                            <Grid item xs={12} md={6}>
                                <div className={classes.field}>
                                    <div className={classes.fieldLabel}>
                                        <Typography
                                            variant="body2"
                                            component="label"
                                            style={{ fontSize: '16px' }}
                                        >
                                            Industry / Sectors
                                        </Typography>
                                    </div>
                                    <StyledSelect
                                        id="sector"
                                        name="sector"
                                        aria-label="Select sector"
                                        isMulti
                                        options={
                                            mapDjangoChoiceTuplesToSelectOptions(
                                                mockedSectors,
                                            ) || []
                                        }
                                        value={formData.sector || []}
                                        onChange={values =>
                                            handleChange('sector', values)
                                        }
                                        placeholder="Select sectors..."
                                    />
                                </div>
                            </Grid>

                            {/* Location Type */}
                            <Grid item xs={12} md={6}>
                                <div className={classes.field}>
                                    <div className={classes.fieldLabel}>
                                        <Typography
                                            variant="body2"
                                            component="label"
                                            style={{ fontSize: '16px' }}
                                        >
                                            Location Type(s)
                                        </Typography>
                                        <Tooltip
                                            title="Select or enter the location type(s) for this production location. For example: Final Product Assembly, Raw Materials Production or Processing, Office/HQ."
                                            placement="top"
                                            classes={{
                                                tooltip: classes.tooltip,
                                            }}
                                        >
                                            <IconButton
                                                size="small"
                                                disableRipple
                                                className={
                                                    classes.helpIconButton
                                                }
                                            >
                                                <HelpOutline
                                                    className={classes.helpIcon}
                                                />
                                            </IconButton>
                                        </Tooltip>
                                    </div>
                                    {enabledTaxonomy ? (
                                        <StyledSelect
                                            id="location_type"
                                            name="location-type"
                                            aria-label="Location type"
                                            isMulti
                                            options={mapFacilityTypeOptions(
                                                processingTypeOptions || [],
                                                formData.processingType || [],
                                            )}
                                            value={formData.locationType || []}
                                            onChange={values =>
                                                handleChange(
                                                    'locationType',
                                                    values,
                                                )
                                            }
                                            placeholder="Select location type(s)"
                                        />
                                    ) : (
                                        <StyledSelect
                                            creatable
                                            isMulti
                                            name="location-type"
                                            aria-label="Location type"
                                            value={formData.locationType || []}
                                            onChange={values =>
                                                handleChange(
                                                    'locationType',
                                                    values,
                                                )
                                            }
                                            placeholder="Enter location type(s)"
                                        />
                                    )}
                                </div>
                            </Grid>
                        </Grid>

                        {/* Processing Type */}
                        <div className={classes.field}>
                            <div className={classes.fieldLabel}>
                                <Typography
                                    variant="body2"
                                    component="label"
                                    style={{ fontSize: '16px' }}
                                >
                                    Processing Type(s)
                                </Typography>
                                <Tooltip
                                    title="Select or enter the type of processing activities that take place at this location. For example: Printing, Tooling, Assembly."
                                    placement="top"
                                    classes={{ tooltip: classes.tooltip }}
                                >
                                    <IconButton
                                        size="small"
                                        disableRipple
                                        className={classes.helpIconButton}
                                    >
                                        <HelpOutline
                                            className={classes.helpIcon}
                                        />
                                    </IconButton>
                                </Tooltip>
                            </div>
                            {enabledTaxonomy ? (
                                <StyledSelect
                                    id="processing_type"
                                    name="processing-type"
                                    aria-label="Processing Type"
                                    isMulti
                                    options={mapProcessingTypeOptions(
                                        processingTypeOptions || [],
                                        formData.locationType || [],
                                    )}
                                    value={formData.processingType || []}
                                    onChange={values =>
                                        handleChange('processingType', values)
                                    }
                                    placeholder="Select processing type(s)"
                                />
                            ) : (
                                <StyledSelect
                                    creatable
                                    isMulti
                                    name="processing-type"
                                    aria-label="Processing Type"
                                    value={formData.processingType || []}
                                    onChange={values =>
                                        handleChange('processingType', values)
                                    }
                                    placeholder="Enter processing type(s)"
                                />
                            )}
                        </div>

                        {/* Product Types */}
                        <div className={classes.field}>
                            <div className={classes.fieldLabel}>
                                <Typography
                                    variant="body2"
                                    component="label"
                                    style={{ fontSize: '16px' }}
                                >
                                    Product Types
                                </Typography>
                                <Tooltip
                                    title="Examples: T-shirts, Jeans, Dresses, Shirts, Jackets, Underwear, Sportswear, Children's clothing"
                                    placement="top"
                                    classes={{ tooltip: classes.tooltip }}
                                >
                                    <IconButton
                                        size="small"
                                        disableRipple
                                        className={classes.helpIconButton}
                                    >
                                        <HelpOutline
                                            className={classes.helpIcon}
                                        />
                                    </IconButton>
                                </Tooltip>
                            </div>
                            <TextField
                                fullWidth
                                variant="outlined"
                                value={formData.productTypes || ''}
                                onChange={e =>
                                    handleChange('productTypes', e.target.value)
                                }
                                placeholder="e.g., T-shirts, Jeans, Dresses"
                            />
                        </div>

                        <Grid container spacing={24}>
                            {/* Number of Workers */}
                            <Grid item xs={12} md={6}>
                                <div className={classes.field}>
                                    <div className={classes.fieldLabel}>
                                        <Typography
                                            variant="body2"
                                            component="label"
                                            style={{ fontSize: '16px' }}
                                        >
                                            Number of Workers
                                        </Typography>
                                        <Tooltip
                                            title="Total number of employees working at this production location"
                                            placement="top"
                                            classes={{
                                                tooltip: classes.tooltip,
                                            }}
                                        >
                                            <IconButton
                                                size="small"
                                                disableRipple
                                                className={
                                                    classes.helpIconButton
                                                }
                                            >
                                                <HelpOutline
                                                    className={classes.helpIcon}
                                                />
                                            </IconButton>
                                        </Tooltip>
                                    </div>
                                    <TextField
                                        fullWidth
                                        variant="outlined"
                                        type="number"
                                        value={formData.numberOfWorkers || ''}
                                        onChange={e =>
                                            handleChange(
                                                'numberOfWorkers',
                                                e.target.value,
                                            )
                                        }
                                        placeholder="e.g., 500"
                                    />
                                </div>
                            </Grid>

                            {/* Female Workers */}
                            <Grid item xs={12} md={6}>
                                <div className={classes.field}>
                                    <div className={classes.fieldLabel}>
                                        <Typography
                                            variant="body2"
                                            component="label"
                                            style={{ fontSize: '16px' }}
                                        >
                                            % of Female Workers
                                        </Typography>
                                        <Tooltip
                                            title="Percentage of female employees out of the total workforce at this location"
                                            placement="top"
                                            classes={{
                                                tooltip: classes.tooltip,
                                            }}
                                        >
                                            <IconButton
                                                size="small"
                                                disableRipple
                                                className={
                                                    classes.helpIconButton
                                                }
                                            >
                                                <HelpOutline
                                                    className={classes.helpIcon}
                                                />
                                            </IconButton>
                                        </Tooltip>
                                    </div>
                                    <TextField
                                        fullWidth
                                        variant="outlined"
                                        value={formData.femaleWorkers || ''}
                                        onChange={e =>
                                            handleChange(
                                                'femaleWorkers',
                                                e.target.value,
                                            )
                                        }
                                        placeholder="e.g., 45%"
                                    />
                                </div>
                            </Grid>
                        </Grid>

                        <Grid container spacing={24}>
                            {/* Minimum Order Quantity */}
                            <Grid item xs={12} md={6}>
                                <div className={classes.field}>
                                    <div className={classes.fieldLabel}>
                                        <Typography
                                            variant="body2"
                                            component="label"
                                            style={{ fontSize: '16px' }}
                                        >
                                            Minimum Order Quantity
                                        </Typography>
                                        <Tooltip
                                            title={BETA_TOOLTIP_TEXT}
                                            placement="top"
                                            classes={{
                                                tooltip: classes.tooltip,
                                            }}
                                        >
                                            <div className={classes.betaLabel}>
                                                <Star
                                                    className={classes.betaIcon}
                                                />
                                                BETA
                                            </div>
                                        </Tooltip>
                                        <Tooltip
                                            title="Smallest order quantity this production location will accept from customers"
                                            placement="top"
                                            classes={{
                                                tooltip: classes.tooltip,
                                            }}
                                        >
                                            <IconButton
                                                size="small"
                                                disableRipple
                                                className={
                                                    classes.helpIconButton
                                                }
                                            >
                                                <HelpOutline
                                                    className={classes.helpIcon}
                                                />
                                            </IconButton>
                                        </Tooltip>
                                    </div>
                                    <TextField
                                        fullWidth
                                        variant="outlined"
                                        value={
                                            formData.minimumOrderQuantity || ''
                                        }
                                        onChange={e =>
                                            handleChange(
                                                'minimumOrderQuantity',
                                                e.target.value,
                                            )
                                        }
                                        placeholder="e.g., 1000 units"
                                    />
                                </div>
                            </Grid>

                            {/* Average Lead Time */}
                            <Grid item xs={12} md={6}>
                                <div className={classes.field}>
                                    <div className={classes.fieldLabel}>
                                        <Typography
                                            variant="body2"
                                            component="label"
                                            style={{ fontSize: '16px' }}
                                        >
                                            Average Lead Time
                                        </Typography>
                                        <Tooltip
                                            title={BETA_TOOLTIP_TEXT}
                                            placement="top"
                                            classes={{
                                                tooltip: classes.tooltip,
                                            }}
                                        >
                                            <div className={classes.betaLabel}>
                                                <Star
                                                    className={classes.betaIcon}
                                                />
                                                BETA
                                            </div>
                                        </Tooltip>
                                        <Tooltip
                                            title="Typical time required from order confirmation to product delivery"
                                            placement="top"
                                            classes={{
                                                tooltip: classes.tooltip,
                                            }}
                                        >
                                            <IconButton
                                                size="small"
                                                disableRipple
                                                className={
                                                    classes.helpIconButton
                                                }
                                            >
                                                <HelpOutline
                                                    className={classes.helpIcon}
                                                />
                                            </IconButton>
                                        </Tooltip>
                                    </div>
                                    <TextField
                                        fullWidth
                                        variant="outlined"
                                        value={formData.averageLeadTime || ''}
                                        onChange={e =>
                                            handleChange(
                                                'averageLeadTime',
                                                e.target.value,
                                            )
                                        }
                                        placeholder="e.g., 30 days"
                                    />
                                </div>
                            </Grid>
                        </Grid>
                    </ExpansionPanelDetails>
                </ExpansionPanel>

                {/* Section 4: Compliance & Partnerships */}
                <ExpansionPanel
                    className={classes.expansionPanel}
                    defaultExpanded
                >
                    <ExpansionPanelSummary
                        expandIcon={<ExpandMoreIcon />}
                        className={classes.expansionPanelSummary}
                    >
                        <div className={classes.sectionHeader}>
                            <div
                                className={`${classes.sectionIconWrapper} ${classes.purpleBg}`}
                            >
                                <VerifiedUser
                                    className={`${classes.sectionIcon} ${classes.purpleIcon}`}
                                />
                            </div>
                            <div className={classes.sectionTitleWrapper}>
                                <Typography className={classes.sectionTitle}>
                                    Compliance & Partnerships
                                </Typography>
                                <Typography
                                    className={classes.sectionDescription}
                                >
                                    Certifications, affiliations, and industry
                                    standards
                                </Typography>
                            </div>
                        </div>
                    </ExpansionPanelSummary>
                    <ExpansionPanelDetails
                        className={classes.expansionPanelDetails}
                    >
                        {/* Affiliations */}
                        <div className={classes.field}>
                            <div className={classes.fieldLabel}>
                                <Typography
                                    variant="body2"
                                    component="label"
                                    style={{ fontSize: '16px' }}
                                >
                                    Affiliations
                                </Typography>
                                <Tooltip
                                    title={BETA_TOOLTIP_TEXT}
                                    placement="top"
                                    classes={{ tooltip: classes.tooltip }}
                                >
                                    <div className={classes.betaLabel}>
                                        <Star className={classes.betaIcon} />
                                        BETA
                                    </div>
                                </Tooltip>
                                <Tooltip
                                    title="Organizations, parent companies, or partner entities your facility is formally connected to"
                                    placement="top"
                                    classes={{ tooltip: classes.tooltip }}
                                >
                                    <IconButton
                                        size="small"
                                        disableRipple
                                        className={classes.helpIconButton}
                                    >
                                        <HelpOutline
                                            className={classes.helpIcon}
                                        />
                                    </IconButton>
                                </Tooltip>
                            </div>
                            <StyledSelect
                                id="affiliations"
                                name="affiliations"
                                aria-label="Affiliations"
                                isMulti
                                options={AFFILIATIONS_OPTIONS}
                                value={formData.affiliations || []}
                                onChange={values =>
                                    handleChange('affiliations', values)
                                }
                                placeholder="Select affiliations..."
                            />
                        </div>

                        {/* Certifications */}
                        <div className={classes.field}>
                            <div className={classes.fieldLabel}>
                                <Typography
                                    variant="body2"
                                    component="label"
                                    style={{ fontSize: '16px' }}
                                >
                                    Certifications / Standards / Regulations
                                </Typography>
                                <Tooltip
                                    title={BETA_TOOLTIP_TEXT}
                                    placement="top"
                                    classes={{ tooltip: classes.tooltip }}
                                >
                                    <div className={classes.betaLabel}>
                                        <Star className={classes.betaIcon} />
                                        BETA
                                    </div>
                                </Tooltip>
                            </div>
                            <StyledSelect
                                id="certifications"
                                name="certifications"
                                aria-label="Certifications"
                                isMulti
                                options={CERTIFICATIONS_OPTIONS}
                                value={formData.certifications || []}
                                onChange={values =>
                                    handleChange('certifications', values)
                                }
                                placeholder="Select certifications..."
                            />
                        </div>
                    </ExpansionPanelDetails>
                </ExpansionPanel>

                {/* Section 5: Environmental Data */}
                <ExpansionPanel
                    className={classes.expansionPanel}
                    defaultExpanded
                >
                    <ExpansionPanelSummary
                        expandIcon={<ExpandMoreIcon />}
                        className={classes.expansionPanelSummary}
                    >
                        <div className={classes.sectionHeader}>
                            <div
                                className={`${classes.sectionIconWrapper} ${classes.greenBg}`}
                            >
                                <Nature
                                    className={`${classes.sectionIcon} ${classes.greenIcon}`}
                                />
                            </div>
                            <div className={classes.sectionTitleWrapper}>
                                <Typography className={classes.sectionTitle}>
                                    Environmental Data
                                </Typography>
                                <Typography
                                    className={classes.sectionDescription}
                                >
                                    Emissions estimates and energy consumption
                                    data
                                </Typography>
                            </div>
                        </div>
                    </ExpansionPanelSummary>
                    <ExpansionPanelDetails
                        className={classes.expansionPanelDetails}
                    >
                        <FreeEmissionsEstimate
                            onValidationChange={
                                setFreeEmissionsEstimateHasErrors
                            }
                        />
                    </ExpansionPanelDetails>
                </ExpansionPanel>
            </Grid>
        </Grid>
    );
};

ProfileStep.propTypes = {
    classes: object.isRequired,
    formData: object.isRequired,
    handleChange: func.isRequired,
    touched: object,
    errors: object,
    countryOptions: object,
    processingTypeOptions: object,
};

ProfileStep.defaultProps = {
    touched: {},
    errors: {},
    countryOptions: null,
    processingTypeOptions: null,
};

export default withStyles(profileStepStyles)(withScrollReset(ProfileStep));
