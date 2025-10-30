import React, { useState, useEffect } from 'react';
import { array, func, object } from 'prop-types';
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

import StyledSelect from '../../../../Filters/StyledSelect';
import InputSection from '../../../../InputSection';
import withScrollReset from '../../../HOCs/withScrollReset';
import ClaimEmissionsEstimate from '../../ClaimEmissionsEstimate/ClaimEmissionsEstimate';
import { mockedSectors } from '../../../../../util/constants';
import {
    mapDjangoChoiceTuplesToSelectOptions,
    mapFacilityTypeOptions,
    mapProcessingTypeOptions,
} from '../../../../../util/util';
import {
    BETA_TOOLTIP_TEXT,
    AFFILIATIONS_OPTIONS,
    CERTIFICATIONS_OPTIONS,
} from './constants';
import { profileStepStyles, selectStyles } from './styles';

const ProfileStep = ({
    classes,
    formData,
    handleChange,
    handleBlur,
    touched,
    errors,
    countryOptions,
    processingTypeOptions,
    parentCompanyOptions,
    onEmissionsValidationChange,
}) => {
    const [
        claimEmissionsEstimateHasErrors,
        setClaimEmissionsEstimateHasErrors,
    ] = useState(false);

    const [enabledTaxonomy, setEnabledTaxonomy] = useState(false);

    const [shouldHideBusinessWebsite] = useState(
        () => !!formData.businessWebsite,
    );

    useEffect(() => {
        if (onEmissionsValidationChange) {
            onEmissionsValidationChange(claimEmissionsEstimateHasErrors);
        }
    }, [claimEmissionsEstimateHasErrors, onEmissionsValidationChange]);

    useEffect(() => {
        setEnabledTaxonomy(
            formData.sectors &&
                formData.sectors.length === 1 &&
                formData.sectors[0].value === 'Apparel',
        );
    }, [formData.sectors]);

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
                                        value={formData.officePhoneNumber || ''}
                                        onChange={e =>
                                            handleChange(
                                                'officePhoneNumber',
                                                e.target.value,
                                            )
                                        }
                                        onBlur={handleBlur}
                                        placeholder="+1 (555) 123-4567"
                                        error={
                                            touched.officePhoneNumber &&
                                            !!errors.officePhoneNumber
                                        }
                                        helperText={
                                            touched.officePhoneNumber &&
                                            errors.officePhoneNumber
                                        }
                                    />
                                </div>
                            </Grid>

                            {/* Facility Website - Hidden if businessWebsite is already provided */}
                            {!shouldHideBusinessWebsite && (
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
                                                        className={
                                                            classes.helpIcon
                                                        }
                                                    />
                                                </IconButton>
                                            </Tooltip>
                                        </div>
                                        <TextField
                                            fullWidth
                                            type="url"
                                            variant="outlined"
                                            value={
                                                formData.businessWebsite || ''
                                            }
                                            onChange={e =>
                                                handleChange(
                                                    'businessWebsite',
                                                    e.target.value,
                                                )
                                            }
                                            onBlur={handleBlur}
                                            placeholder="https://company.com"
                                            error={
                                                touched.businessWebsite &&
                                                !!errors.businessWebsite
                                            }
                                            helperText={
                                                touched.businessWebsite &&
                                                errors.businessWebsite
                                            }
                                        />
                                    </div>
                                </Grid>
                            )}
                        </Grid>

                        {/* Description */}
                        <div
                            className={classes.field}
                            style={{ paddingRight: '28px' }}
                        >
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
                                value={formData.facilityDescription || ''}
                                onChange={e =>
                                    handleChange(
                                        'facilityDescription',
                                        e.target.value,
                                    )
                                }
                                onBlur={handleBlur}
                                placeholder="Brief description of what this production location produces or its main activities"
                                error={
                                    touched.facilityDescription &&
                                    !!errors.facilityDescription
                                }
                                helperText={
                                    touched.facilityDescription &&
                                    errors.facilityDescription
                                }
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
                                    <InputSection
                                        label="Parent Company Name / Supplier Group"
                                        isSelect
                                        selectOptions={
                                            parentCompanyOptions || []
                                        }
                                        value={formData.parentCompanyName || ''}
                                        onChange={option =>
                                            handleChange(
                                                'parentCompanyName',
                                                option?.value || '',
                                            )
                                        }
                                        selectPlaceholder="Select parent company..."
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
                                        value={
                                            formData.officeOfficialName || ''
                                        }
                                        onChange={e =>
                                            handleChange(
                                                'officeOfficialName',
                                                e.target.value,
                                            )
                                        }
                                        onBlur={handleBlur}
                                        placeholder="Office name"
                                        error={
                                            touched.officeOfficialName &&
                                            !!errors.officeOfficialName
                                        }
                                        helperText={
                                            touched.officeOfficialName &&
                                            errors.officeOfficialName
                                        }
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
                                        onBlur={handleBlur}
                                        placeholder="Office address"
                                        error={
                                            touched.officeAddress &&
                                            !!errors.officeAddress
                                        }
                                        helperText={
                                            touched.officeAddress &&
                                            errors.officeAddress
                                        }
                                    />
                                </div>
                            </Grid>
                            <Grid item xs={12} md={6}>
                                <div className={classes.field}>
                                    <InputSection
                                        label="Office Country"
                                        isSelect
                                        selectOptions={countryOptions || []}
                                        value={formData.officeCountryCode || ''}
                                        onChange={option =>
                                            handleChange(
                                                'officeCountryCode',
                                                option?.value || '',
                                            )
                                        }
                                        selectPlaceholder="Select country..."
                                        menuPlacement="top"
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
                                        id="sectors"
                                        name="sectors"
                                        aria-label="Select sector"
                                        isMulti
                                        options={
                                            mapDjangoChoiceTuplesToSelectOptions(
                                                mockedSectors,
                                            ) || []
                                        }
                                        value={formData.sectors || []}
                                        onChange={values =>
                                            handleChange('sectors', values)
                                        }
                                        placeholder="Select sectors..."
                                        styles={selectStyles}
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
                                                formData.facilityProductionTypes ||
                                                    [],
                                            )}
                                            value={formData.facilityType || []}
                                            onChange={values =>
                                                handleChange(
                                                    'facilityType',
                                                    values,
                                                )
                                            }
                                            placeholder="Select location type(s)"
                                            styles={selectStyles}
                                        />
                                    ) : (
                                        <StyledSelect
                                            creatable
                                            isMulti
                                            name="location-type"
                                            aria-label="Location type"
                                            value={formData.facilityType || []}
                                            onChange={values =>
                                                handleChange(
                                                    'facilityType',
                                                    values,
                                                )
                                            }
                                            placeholder="Enter location type(s)"
                                            styles={selectStyles}
                                        />
                                    )}
                                </div>
                            </Grid>

                            {/* Processing Type */}
                            <Grid item xs={12} md={6}>
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
                                            id="processing_type"
                                            name="processing-type"
                                            aria-label="Processing Type"
                                            isMulti
                                            options={mapProcessingTypeOptions(
                                                processingTypeOptions || [],
                                                formData.facilityType || [],
                                            )}
                                            value={
                                                formData.facilityProductionTypes ||
                                                []
                                            }
                                            onChange={values =>
                                                handleChange(
                                                    'facilityProductionTypes',
                                                    values,
                                                )
                                            }
                                            placeholder="Select processing type(s)"
                                            styles={selectStyles}
                                        />
                                    ) : (
                                        <StyledSelect
                                            creatable
                                            isMulti
                                            name="processing-type"
                                            aria-label="Processing Type"
                                            value={
                                                formData.facilityProductionTypes ||
                                                []
                                            }
                                            onChange={values =>
                                                handleChange(
                                                    'facilityProductionTypes',
                                                    values,
                                                )
                                            }
                                            placeholder="Enter processing type(s)"
                                            styles={selectStyles}
                                        />
                                    )}
                                </div>
                            </Grid>

                            {/* Product Types */}
                            <Grid item xs={12} md={6}>
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
                                        creatable
                                        isMulti
                                        name="product-types"
                                        aria-label="Product Types"
                                        value={
                                            formData.facilityProductTypes || []
                                        }
                                        onChange={values =>
                                            handleChange(
                                                'facilityProductTypes',
                                                values,
                                            )
                                        }
                                        placeholder="Enter product types..."
                                        styles={selectStyles}
                                    />
                                </div>
                            </Grid>
                        </Grid>

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
                                        value={formData.numberOfWorkers || ''}
                                        onChange={e =>
                                            handleChange(
                                                'numberOfWorkers',
                                                e.target.value,
                                            )
                                        }
                                        onBlur={handleBlur}
                                        placeholder="e.g., 500"
                                        error={
                                            touched.numberOfWorkers &&
                                            !!errors.numberOfWorkers
                                        }
                                        helperText={
                                            touched.numberOfWorkers &&
                                            errors.numberOfWorkers
                                        }
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
                                        value={
                                            formData.facilityFemaleWorkersPercentage ||
                                            ''
                                        }
                                        onChange={e =>
                                            handleChange(
                                                'facilityFemaleWorkersPercentage',
                                                e.target.value,
                                            )
                                        }
                                        onBlur={handleBlur}
                                        placeholder="e.g., 45%"
                                        error={
                                            touched.facilityFemaleWorkersPercentage &&
                                            !!errors.facilityFemaleWorkersPercentage
                                        }
                                        helperText={
                                            touched.facilityFemaleWorkersPercentage &&
                                            errors.facilityFemaleWorkersPercentage
                                        }
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
                                            formData.facilityMinimumOrderQuantity ||
                                            ''
                                        }
                                        onChange={e =>
                                            handleChange(
                                                'facilityMinimumOrderQuantity',
                                                e.target.value,
                                            )
                                        }
                                        onBlur={handleBlur}
                                        placeholder="e.g., 1000 units"
                                        error={
                                            touched.facilityMinimumOrderQuantity &&
                                            !!errors.facilityMinimumOrderQuantity
                                        }
                                        helperText={
                                            touched.facilityMinimumOrderQuantity &&
                                            errors.facilityMinimumOrderQuantity
                                        }
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
                                        value={
                                            formData.facilityAverageLeadTime ||
                                            ''
                                        }
                                        onChange={e =>
                                            handleChange(
                                                'facilityAverageLeadTime',
                                                e.target.value,
                                            )
                                        }
                                        onBlur={handleBlur}
                                        placeholder="e.g., 30 days"
                                        error={
                                            touched.facilityAverageLeadTime &&
                                            !!errors.facilityAverageLeadTime
                                        }
                                        helperText={
                                            touched.facilityAverageLeadTime &&
                                            errors.facilityAverageLeadTime
                                        }
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
                                value={formData.facilityAffiliations || []}
                                onChange={values =>
                                    handleChange('facilityAffiliations', values)
                                }
                                placeholder="Select affiliations..."
                                styles={selectStyles}
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
                                value={formData.facilityCertifications || []}
                                onChange={values =>
                                    handleChange(
                                        'facilityCertifications',
                                        values,
                                    )
                                }
                                placeholder="Select certifications..."
                                styles={selectStyles}
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
                        <ClaimEmissionsEstimate
                            onValidationChange={
                                setClaimEmissionsEstimateHasErrors
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
    handleBlur: func.isRequired,
    touched: object,
    errors: object,
    countryOptions: array,
    processingTypeOptions: array,
    parentCompanyOptions: array,
    onEmissionsValidationChange: func,
};

ProfileStep.defaultProps = {
    touched: {},
    errors: {},
    countryOptions: null,
    processingTypeOptions: null,
    parentCompanyOptions: null,
    onEmissionsValidationChange: null,
};

export default withStyles(profileStepStyles)(withScrollReset(ProfileStep));
