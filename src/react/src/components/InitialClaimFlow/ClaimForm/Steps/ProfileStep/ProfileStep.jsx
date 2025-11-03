import React, { useState, useEffect } from 'react';
import { array, func, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import TextField from '@material-ui/core/TextField';
import Business from '@material-ui/icons/Business';
import Build from '@material-ui/icons/Build';
import VerifiedUser from '@material-ui/icons/VerifiedUser';
import Tooltip from '@material-ui/core/Tooltip';
import HelpOutline from '@material-ui/icons/HelpOutline';
import IconButton from '@material-ui/core/IconButton';
import Switch from '@material-ui/core/Switch';
import FormFieldTitle from '../../../Shared/FormFieldTitle.jsx/FormFieldTitle';
import DialogTooltip from '../../../../Contribute/DialogTooltip';
import StyledSelect from '../../../../Filters/StyledSelect';
import InputErrorText from '../../../../Contribute/InputErrorText';
import withScrollReset from '../../../HOCs/withScrollReset';
import ClaimEmissionsEstimate from '../../ClaimEmissionsEstimate/ClaimEmissionsEstimate';
import { mockedSectors } from '../../../../../util/constants';
import {
    mapDjangoChoiceTuplesToSelectOptions,
    mapFacilityTypeOptions,
    mapProcessingTypeOptions,
    getSelectStyles,
} from '../../../../../util/util';
import {
    BETA_TOOLTIP_TEXT,
    AFFILIATIONS_OPTIONS,
    CERTIFICATIONS_OPTIONS,
} from './constants';
import { profileStepStyles } from './styles';
import { selectStyles } from '../../styles';

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

    const [isOverviewVisible, setIsOverviewVisible] = useState(true);
    const [
        isCompanyInformationVisible,
        setIsCompanyInformationVisible,
    ] = useState(true);
    const [
        isOperationsCapabilitiesVisible,
        setIsOperationsCapabilitiesVisible,
    ] = useState(true);
    const [
        isCompliancePartnershipsVisible,
        setIsCompliancePartnershipsVisible,
    ] = useState(true);

    const getBetaSelectStyles = (isErrorState, extendedStyles) => ({
        ...getSelectStyles(isErrorState, extendedStyles),
        indicatorsContainer: () => ({
            display: 'none',
        }),
    });

    return (
        <div>
            <hr className={classes.separator} />
            <div className={classes.sectionContainer}>
                <div className={classes.sectionTitleContainer}>
                    <Typography
                        variant="title"
                        component="h3"
                        className={classes.sectionTitle}
                    >
                        <div
                            className={`${classes.sectionIconWrapper} ${classes.blueBg}`}
                        >
                            <Business
                                className={`${classes.sectionIcon} ${classes.blueIcon}`}
                            />
                        </div>
                        Production Location Overview
                    </Typography>
                    <div className={classes.switchContainer}>
                        <Switch
                            checked={isOverviewVisible}
                            onChange={(_, checked) => {
                                setIsOverviewVisible(checked);
                            }}
                            color="primary"
                        />
                    </div>
                </div>
                <Typography className={classes.sectionDescription}>
                    Basic facility identification and contact information.
                </Typography>
            </div>
            {isOverviewVisible && (
                <section>
                    <div className={classes.fieldContainer}>
                        <FormFieldTitle
                            label={
                                <>
                                    Production Location Name in Native Language
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
                                </>
                            }
                            classes={{ title: classes.formLabel }}
                        />
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
                            InputProps={{
                                classes: {
                                    input: classes.inputStyles,
                                    notchedOutline:
                                        classes.notchedOutlineStyles,
                                },
                            }}
                        />
                        {touched.localLanguageName && errors.localLanguageName && (
                            <div className={classes.errorWrapStyles}>
                                <InputErrorText
                                    text={errors.localLanguageName}
                                />
                            </div>
                        )}
                    </div>
                    <div className={classes.fieldContainer}>
                        <FormFieldTitle
                            label={
                                <>
                                    Company Phone
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
                                            className={classes.helpIconButton}
                                        >
                                            <HelpOutline
                                                className={classes.helpIcon}
                                            />
                                        </IconButton>
                                    </Tooltip>
                                </>
                            }
                            classes={{ title: classes.formLabel }}
                        />
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
                            InputProps={{
                                classes: {
                                    input: classes.inputStyles,
                                    notchedOutline:
                                        classes.notchedOutlineStyles,
                                },
                            }}
                        />
                        {touched.officePhoneNumber && errors.officePhoneNumber && (
                            <div className={classes.errorWrapStyles}>
                                <InputErrorText
                                    text={errors.officePhoneNumber}
                                />
                            </div>
                        )}
                        <DialogTooltip
                            text={BETA_TOOLTIP_TEXT}
                            childComponent={
                                <span className={classes.betaBadge}>BETA</span>
                            }
                        />
                    </div>
                    {!shouldHideBusinessWebsite && (
                        <div className={classes.fieldContainer}>
                            <FormFieldTitle
                                label={
                                    <>
                                        Company Website
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
                                    </>
                                }
                                classes={{ title: classes.formLabel }}
                            />
                            <TextField
                                fullWidth
                                type="url"
                                variant="outlined"
                                value={formData.businessWebsite || ''}
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
                                InputProps={{
                                    classes: {
                                        input: classes.inputStyles,
                                        notchedOutline:
                                            classes.notchedOutlineStyles,
                                    },
                                }}
                            />
                            {touched.businessWebsite && errors.businessWebsite && (
                                <div className={classes.errorWrapStyles}>
                                    <InputErrorText
                                        text={errors.businessWebsite}
                                    />
                                </div>
                            )}
                            <DialogTooltip
                                text={BETA_TOOLTIP_TEXT}
                                childComponent={
                                    <span className={classes.betaBadge}>
                                        BETA
                                    </span>
                                }
                            />
                        </div>
                    )}
                    <div className={classes.textareaFieldContainer}>
                        <FormFieldTitle
                            label={
                                <>
                                    Production Location Description
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
                                </>
                            }
                            classes={{ title: classes.formLabel }}
                        />
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
                            InputProps={{
                                classes: {
                                    input: classes.inputStyles,
                                    notchedOutline:
                                        classes.notchedOutlineStyles,
                                    multiline: classes.multilineInputStyles,
                                },
                            }}
                        />
                        {touched.facilityDescription &&
                            errors.facilityDescription && (
                                <div className={classes.errorWrapStyles}>
                                    <InputErrorText
                                        text={errors.facilityDescription}
                                    />
                                </div>
                            )}
                        <DialogTooltip
                            text={BETA_TOOLTIP_TEXT}
                            childComponent={
                                <span className={classes.betaBadge}>BETA</span>
                            }
                        />
                    </div>
                </section>
            )}
            <hr className={classes.separator} />
            <div className={classes.sectionContainer}>
                <div className={classes.sectionTitleContainer}>
                    <Typography
                        variant="title"
                        component="h3"
                        className={classes.sectionTitle}
                    >
                        <div
                            className={`${classes.sectionIconWrapper} ${classes.amberBg}`}
                        >
                            <Business
                                className={`${classes.sectionIcon} ${classes.amberIcon}`}
                            />
                        </div>
                        Company Information
                    </Typography>
                    <div className={classes.switchContainer}>
                        <Switch
                            checked={isCompanyInformationVisible}
                            onChange={(_, checked) => {
                                setIsCompanyInformationVisible(checked);
                            }}
                            color="primary"
                        />
                    </div>
                </div>
                <Typography className={classes.sectionDescription}>
                    Parent company and office information (if office is
                    different from production location).
                </Typography>
            </div>
            {isCompanyInformationVisible && (
                <section>
                    <div className={classes.fieldContainer}>
                        <FormFieldTitle
                            label="Parent Company Name / Supplier Group"
                            classes={{ title: classes.formLabel }}
                        />
                        <StyledSelect
                            id="parentCompanyName"
                            name="parentCompanyName"
                            aria-label="Parent company name"
                            options={parentCompanyOptions || []}
                            value={formData.parentCompanyName || ''}
                            styles={getSelectStyles(
                                touched.parentCompanyName &&
                                    !!errors.parentCompanyName,
                                selectStyles,
                            )}
                            onChange={option =>
                                handleChange(
                                    'parentCompanyName',
                                    option?.value || '',
                                )
                            }
                            placeholder="Select parent company..."
                        />
                        {touched.parentCompanyName && errors.parentCompanyName && (
                            <div className={classes.errorWrapStyles}>
                                <InputErrorText
                                    text={errors.parentCompanyName}
                                />
                            </div>
                        )}
                    </div>
                    <div className={classes.fieldContainer}>
                        <FormFieldTitle
                            label={
                                <>
                                    Office Name
                                    <Tooltip
                                        title="Name of the corporate office or headquarters"
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
                                </>
                            }
                            classes={{ title: classes.formLabel }}
                        />
                        <TextField
                            fullWidth
                            variant="outlined"
                            value={formData.officeOfficialName || ''}
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
                            InputProps={{
                                classes: {
                                    input: classes.inputStyles,
                                    notchedOutline:
                                        classes.notchedOutlineStyles,
                                },
                            }}
                        />
                        {touched.officeOfficialName &&
                            errors.officeOfficialName && (
                                <div className={classes.errorWrapStyles}>
                                    <InputErrorText
                                        text={errors.officeOfficialName}
                                    />
                                </div>
                            )}
                    </div>
                    <div className={classes.fieldContainer}>
                        <FormFieldTitle
                            label={
                                <>
                                    Office Address
                                    <Tooltip
                                        title="Physical address of the office location"
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
                                </>
                            }
                            classes={{ title: classes.formLabel }}
                        />
                        <TextField
                            fullWidth
                            variant="outlined"
                            value={formData.officeAddress || ''}
                            onChange={e =>
                                handleChange('officeAddress', e.target.value)
                            }
                            onBlur={handleBlur}
                            placeholder="Office address"
                            error={
                                touched.officeAddress && !!errors.officeAddress
                            }
                            InputProps={{
                                classes: {
                                    input: classes.inputStyles,
                                    notchedOutline:
                                        classes.notchedOutlineStyles,
                                },
                            }}
                        />
                        {touched.officeAddress && errors.officeAddress && (
                            <div className={classes.errorWrapStyles}>
                                <InputErrorText text={errors.officeAddress} />
                            </div>
                        )}
                    </div>
                    <div className={classes.fieldContainer}>
                        <FormFieldTitle
                            label="Office Country"
                            classes={{ title: classes.formLabel }}
                        />
                        <StyledSelect
                            id="officeCountryCode"
                            name="officeCountryCode"
                            aria-label="Office country"
                            isMulti={false}
                            options={countryOptions || []}
                            onChange={option =>
                                handleChange(
                                    'officeCountryCode',
                                    option?.value || '',
                                )
                            }
                            placeholder="Select country..."
                            styles={getSelectStyles(
                                touched.officeCountryCode &&
                                    !!errors.officeCountryCode,
                                selectStyles,
                            )}
                        />
                        {touched.officeCountryCode && errors.officeCountryCode && (
                            <div className={classes.errorWrapStyles}>
                                <InputErrorText
                                    text={errors.officeCountryCode}
                                />
                            </div>
                        )}
                    </div>
                </section>
            )}
            <hr className={classes.separator} />
            <div className={classes.sectionContainer}>
                <div className={classes.sectionTitleContainer}>
                    <Typography
                        variant="title"
                        component="h3"
                        className={classes.sectionTitle}
                    >
                        <div
                            className={`${classes.sectionIconWrapper} ${classes.blueBg}`}
                        >
                            <Build
                                className={`${classes.sectionIcon} ${classes.blueIcon}`}
                            />
                        </div>
                        Operations & Capabilities
                    </Typography>
                    <div className={classes.switchContainer}>
                        <Switch
                            checked={isOperationsCapabilitiesVisible}
                            onChange={(_, checked) => {
                                setIsOperationsCapabilitiesVisible(checked);
                            }}
                            color="primary"
                        />
                    </div>
                </div>
                <Typography className={classes.sectionDescription}>
                    Production and operations details for your location.
                </Typography>
            </div>

            {isOperationsCapabilitiesVisible && (
                <section>
                    <div className={classes.fieldContainer}>
                        <FormFieldTitle
                            label="Industry / Sectors"
                            classes={{ title: classes.formLabel }}
                        />
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
                            onChange={values => handleChange('sectors', values)}
                            placeholder="Select sectors..."
                            styles={getSelectStyles(
                                touched.sectors && !!errors.sectors,
                                selectStyles,
                            )}
                        />
                        {touched.sectors && errors.sectors && (
                            <div className={classes.errorWrapStyles}>
                                <InputErrorText text={errors.sectors} />
                            </div>
                        )}
                    </div>
                    <div className={classes.fieldContainer}>
                        <FormFieldTitle
                            label={
                                <>
                                    Location Type(s)
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
                                            className={classes.helpIconButton}
                                        >
                                            <HelpOutline
                                                className={classes.helpIcon}
                                            />
                                        </IconButton>
                                    </Tooltip>
                                </>
                            }
                            classes={{ title: classes.formLabel }}
                        />
                        {enabledTaxonomy ? (
                            <StyledSelect
                                id="location_type"
                                name="location-type"
                                aria-label="Location type"
                                isMulti
                                options={mapFacilityTypeOptions(
                                    processingTypeOptions || [],
                                    formData.facilityProductionTypes || [],
                                )}
                                value={formData.facilityType || []}
                                onChange={values =>
                                    handleChange('facilityType', values)
                                }
                                placeholder="Select location type(s)"
                                styles={getSelectStyles(
                                    touched.facilityType &&
                                        !!errors.facilityType,
                                    selectStyles,
                                )}
                            />
                        ) : (
                            <StyledSelect
                                creatable
                                isMulti
                                name="location-type"
                                aria-label="Location type"
                                value={formData.facilityType || []}
                                onChange={values =>
                                    handleChange('facilityType', values)
                                }
                                placeholder="Enter location type(s)"
                                styles={getSelectStyles(
                                    touched.facilityType &&
                                        !!errors.facilityType,
                                    selectStyles,
                                )}
                            />
                        )}
                    </div>
                    <div className={classes.fieldContainer}>
                        <FormFieldTitle
                            label={
                                <>
                                    Processing Type(s)
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
                                            className={classes.helpIconButton}
                                        >
                                            <HelpOutline
                                                className={classes.helpIcon}
                                            />
                                        </IconButton>
                                    </Tooltip>
                                </>
                            }
                            classes={{ title: classes.formLabel }}
                        />
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
                                value={formData.facilityProductionTypes || []}
                                onChange={values =>
                                    handleChange(
                                        'facilityProductionTypes',
                                        values,
                                    )
                                }
                                placeholder="Select processing type(s)"
                                styles={getSelectStyles(
                                    touched.facilityProductionTypes &&
                                        !!errors.facilityProductionTypes,
                                    selectStyles,
                                )}
                            />
                        ) : (
                            <StyledSelect
                                creatable
                                isMulti
                                name="processing-type"
                                aria-label="Processing Type"
                                value={formData.facilityProductionTypes || []}
                                onChange={values =>
                                    handleChange(
                                        'facilityProductionTypes',
                                        values,
                                    )
                                }
                                placeholder="Enter processing type(s)"
                                styles={getSelectStyles(
                                    touched.facilityProductionTypes &&
                                        !!errors.facilityProductionTypes,
                                    selectStyles,
                                )}
                            />
                        )}
                    </div>
                    <div className={classes.fieldContainer}>
                        <FormFieldTitle
                            label={
                                <>
                                    Product Types
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
                                            className={classes.helpIconButton}
                                        >
                                            <HelpOutline
                                                className={classes.helpIcon}
                                            />
                                        </IconButton>
                                    </Tooltip>
                                </>
                            }
                            classes={{ title: classes.formLabel }}
                        />
                        <StyledSelect
                            creatable
                            isMulti
                            name="product-types"
                            aria-label="Product Types"
                            value={formData.facilityProductTypes || []}
                            onChange={values =>
                                handleChange('facilityProductTypes', values)
                            }
                            placeholder="Enter product types..."
                            styles={getSelectStyles(
                                touched.facilityProductTypes &&
                                    !!errors.facilityProductTypes,
                                selectStyles,
                            )}
                        />
                    </div>
                    <div className={classes.fieldContainer}>
                        <FormFieldTitle
                            label={
                                <>
                                    Number of Workers
                                    <Tooltip
                                        title="Total number of employees working at this production location, can be a number or a range (e.g., 100, 100-150)"
                                        placement="top"
                                        classes={{
                                            tooltip: classes.tooltip,
                                        }}
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
                                </>
                            }
                            classes={{ title: classes.formLabel }}
                        />
                        <TextField
                            fullWidth
                            variant="outlined"
                            value={formData.numberOfWorkers || ''}
                            onChange={e =>
                                handleChange('numberOfWorkers', e.target.value)
                            }
                            onBlur={handleBlur}
                            placeholder="e.g., 500"
                            error={
                                touched.numberOfWorkers &&
                                !!errors.numberOfWorkers
                            }
                            InputProps={{
                                classes: {
                                    input: classes.inputStyles,
                                    notchedOutline:
                                        classes.notchedOutlineStyles,
                                },
                            }}
                        />
                        {touched.numberOfWorkers && errors.numberOfWorkers && (
                            <div className={classes.errorWrapStyles}>
                                <InputErrorText text={errors.numberOfWorkers} />
                            </div>
                        )}
                    </div>
                    <div className={classes.fieldContainer}>
                        <FormFieldTitle
                            label={
                                <>
                                    Percentage of Female Workers
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
                                            className={classes.helpIconButton}
                                        >
                                            <HelpOutline
                                                className={classes.helpIcon}
                                            />
                                        </IconButton>
                                    </Tooltip>
                                </>
                            }
                            classes={{ title: classes.formLabel }}
                        />
                        <TextField
                            fullWidth
                            variant="outlined"
                            value={
                                formData.facilityFemaleWorkersPercentage || ''
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
                            InputProps={{
                                classes: {
                                    input: classes.inputStyles,
                                    notchedOutline:
                                        classes.notchedOutlineStyles,
                                },
                            }}
                        />
                        {touched.facilityFemaleWorkersPercentage &&
                            errors.facilityFemaleWorkersPercentage && (
                                <div className={classes.errorWrapStyles}>
                                    <InputErrorText
                                        text={
                                            errors.facilityFemaleWorkersPercentage
                                        }
                                    />
                                </div>
                            )}
                    </div>
                    <div className={classes.fieldContainer}>
                        <FormFieldTitle
                            label={
                                <>
                                    Minimum Order Quantity
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
                                            className={classes.helpIconButton}
                                        >
                                            <HelpOutline
                                                className={classes.helpIcon}
                                            />
                                        </IconButton>
                                    </Tooltip>
                                </>
                            }
                            classes={{ title: classes.formLabel }}
                        />
                        <TextField
                            fullWidth
                            variant="outlined"
                            value={formData.facilityMinimumOrderQuantity || ''}
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
                            InputProps={{
                                classes: {
                                    input: classes.inputStyles,
                                    notchedOutline:
                                        classes.notchedOutlineStyles,
                                },
                            }}
                        />
                        {touched.facilityMinimumOrderQuantity &&
                            errors.facilityMinimumOrderQuantity && (
                                <div className={classes.errorWrapStyles}>
                                    <InputErrorText
                                        text={
                                            errors.facilityMinimumOrderQuantity
                                        }
                                    />
                                </div>
                            )}
                        <DialogTooltip
                            text={BETA_TOOLTIP_TEXT}
                            childComponent={
                                <span className={classes.betaBadge}>BETA</span>
                            }
                        />
                    </div>
                    <div className={classes.fieldContainer}>
                        <FormFieldTitle
                            label={
                                <>
                                    Average Lead Time
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
                                            className={classes.helpIconButton}
                                        >
                                            <HelpOutline
                                                className={classes.helpIcon}
                                            />
                                        </IconButton>
                                    </Tooltip>
                                </>
                            }
                            classes={{ title: classes.formLabel }}
                        />
                        <TextField
                            fullWidth
                            variant="outlined"
                            value={formData.facilityAverageLeadTime || ''}
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
                            InputProps={{
                                classes: {
                                    input: classes.inputStyles,
                                    notchedOutline:
                                        classes.notchedOutlineStyles,
                                },
                            }}
                        />
                        {touched.facilityAverageLeadTime &&
                            errors.facilityAverageLeadTime && (
                                <div className={classes.errorWrapStyles}>
                                    <InputErrorText
                                        text={errors.facilityAverageLeadTime}
                                    />
                                </div>
                            )}
                        <DialogTooltip
                            text={BETA_TOOLTIP_TEXT}
                            childComponent={
                                <span className={classes.betaBadge}>BETA</span>
                            }
                        />
                    </div>
                </section>
            )}

            <hr className={classes.separator} />
            <div className={classes.sectionContainer}>
                <div className={classes.sectionTitleContainer}>
                    <Typography
                        variant="title"
                        component="h3"
                        className={classes.sectionTitle}
                    >
                        <div
                            className={`${classes.sectionIconWrapper} ${classes.purpleBg}`}
                        >
                            <VerifiedUser
                                className={`${classes.sectionIcon} ${classes.purpleIcon}`}
                            />
                        </div>
                        Compliance & Partnerships
                    </Typography>
                    <div className={classes.switchContainer}>
                        <Switch
                            checked={isCompliancePartnershipsVisible}
                            onChange={(_, checked) => {
                                setIsCompliancePartnershipsVisible(checked);
                            }}
                            color="primary"
                        />
                    </div>
                </div>
                <Typography className={classes.sectionDescription}>
                    Certifications, affiliations, and industry standards.
                </Typography>
            </div>
            {isCompliancePartnershipsVisible && (
                <section>
                    <div className={classes.fieldContainer}>
                        <FormFieldTitle
                            label={
                                <>
                                    Affiliations
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
                                </>
                            }
                            classes={{ title: classes.formLabel }}
                        />
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
                            styles={getBetaSelectStyles(
                                touched.facilityAffiliations &&
                                    !!errors.facilityAffiliations,
                                selectStyles,
                            )}
                        />
                        <DialogTooltip
                            text={BETA_TOOLTIP_TEXT}
                            childComponent={
                                <span className={classes.betaBadge}>BETA</span>
                            }
                        />
                    </div>
                    <div className={classes.fieldContainer}>
                        <FormFieldTitle
                            label="Certifications / Standards / Regulations"
                            classes={{ title: classes.formLabel }}
                        />
                        <StyledSelect
                            id="certifications"
                            name="certifications"
                            aria-label="Certifications"
                            isMulti
                            options={CERTIFICATIONS_OPTIONS}
                            value={formData.facilityCertifications || []}
                            onChange={values =>
                                handleChange('facilityCertifications', values)
                            }
                            placeholder="Select certifications..."
                            styles={getBetaSelectStyles(
                                touched.facilityCertifications &&
                                    !!errors.facilityCertifications,
                                selectStyles,
                            )}
                        />
                        <DialogTooltip
                            text={BETA_TOOLTIP_TEXT}
                            childComponent={
                                <span className={classes.betaBadge}>BETA</span>
                            }
                        />
                    </div>
                </section>
            )}

            <div className={classes.emissionsEstimateContainer}>
                <ClaimEmissionsEstimate
                    onValidationChange={setClaimEmissionsEstimateHasErrors}
                />
            </div>
        </div>
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
