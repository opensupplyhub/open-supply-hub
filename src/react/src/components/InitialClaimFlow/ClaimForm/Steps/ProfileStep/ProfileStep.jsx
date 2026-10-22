import React, { useState, useEffect } from 'react';
import { array, func, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import TextField from '@material-ui/core/TextField';
import Business from '@material-ui/icons/Business';
import Build from '@material-ui/icons/Build';
import VerifiedUser from '@material-ui/icons/VerifiedUser';
import Spa from '@material-ui/icons/Spa';

import Switch from '@material-ui/core/Switch';
import FormFieldTitle from '../../../Shared/FormFieldTitle/FormFieldTitle';
import FormFieldHint from '../../../Shared/FormFieldHint/FormFieldHint';
import IconComponent from '../../../../Shared/IconComponent/IconComponent';
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
    PROCESSING_TYPES_TOOLTIP,
    PROCESSING_TYPES_TAXONOMY_TOOLTIP,
    PRODUCT_TYPES_TOOLTIP,
    LOCATION_TYPES_TOOLTIP,
    LOCATION_TYPES_TAXONOMY_TOOLTIP,
    COMPANY_WEBSITE_TOOLTIP,
    LOCATION_TYPE_SELECT_PLACEHOLDER,
    PROCESSING_TYPE_SELECT_PLACEHOLDER,
    PRODUCT_TYPE_SELECT_PLACEHOLDER,
} from './constants';
import { profileStepStyles } from './styles';
import { selectStyles } from '../../styles';
import { profileStepSchema } from '../../validationSchemas';

const isValidPersistedBusinessWebsite = website => {
    if (!website) {
        return false;
    }

    return profileStepSchema.fields.businessWebsite.isValidSync(website);
};

const ProfileStep = ({
    classes,
    formData,
    handleChange,
    handleBlur,
    touched,
    errors,
    countryOptions,
    processingTypeOptions,
    onEmissionsValidationChange,
    // Optional overrides for the emissions section, used when the form
    // state lives outside the claimForm slice (pending claim edit view).
    emissionsFormData,
    onEmissionsValueChange,
    onEmissionsEnabledChange,
}) => {
    const [
        claimEmissionsEstimateHasErrors,
        setClaimEmissionsEstimateHasErrors,
    ] = useState(false);

    const [enabledTaxonomy, setEnabledTaxonomy] = useState(false);

    // Only hide a prefilled website when it already passes client validation,
    // so invalid persisted values remain editable.
    const [shouldHideBusinessWebsite] = useState(() =>
        isValidPersistedBusinessWebsite(formData.businessWebsite),
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

    const [
        isFreeEmissionsEstimateVisible,
        setIsFreeEmissionsEstimateVisible,
    ] = useState(true);

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
                                    <IconComponent
                                        className={classes.helpTooltip}
                                        title="Enter the production location name in the local language if different from the English name"
                                    />
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
                    <div className={classes.doubleFieldContainer}>
                        <div className={classes.fieldContainer}>
                            <FormFieldTitle
                                label={
                                    <>
                                        Company Phone
                                        <IconComponent
                                            className={classes.helpTooltip}
                                            title="Main phone number for contacting this production location directly"
                                        />
                                    </>
                                }
                                classes={{ title: classes.formLabel }}
                            />
                            <TextField
                                fullWidth
                                variant="outlined"
                                value={formData.facilityPhoneNumber || ''}
                                onChange={e =>
                                    handleChange(
                                        'facilityPhoneNumber',
                                        e.target.value,
                                    )
                                }
                                onBlur={handleBlur}
                                placeholder="+1 (555) 123-4567"
                                error={
                                    touched.facilityPhoneNumber &&
                                    !!errors.facilityPhoneNumber
                                }
                                InputProps={{
                                    classes: {
                                        input: classes.inputStyles,
                                        notchedOutline:
                                            classes.notchedOutlineStyles,
                                    },
                                }}
                            />
                            {touched.facilityPhoneNumber &&
                                errors.facilityPhoneNumber && (
                                    <div className={classes.errorWrapStyles}>
                                        <InputErrorText
                                            text={errors.facilityPhoneNumber}
                                        />
                                    </div>
                                )}
                            <DialogTooltip
                                text={BETA_TOOLTIP_TEXT}
                                childComponent={
                                    <span
                                        className={`${classes.betaBadge} ${classes.betaBadgeColumn}`}
                                    >
                                        BETA
                                    </span>
                                }
                            />
                        </div>
                        {!shouldHideBusinessWebsite && (
                            <div className={classes.fieldContainer}>
                                <FormFieldTitle
                                    label={
                                        <>
                                            Company Website
                                            <IconComponent
                                                className={classes.helpTooltip}
                                                title={COMPANY_WEBSITE_TOOLTIP}
                                            />
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
                                    placeholder="https://company.com (max 200 characters)"
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
                                {touched.businessWebsite &&
                                    errors.businessWebsite && (
                                        <div
                                            className={classes.errorWrapStyles}
                                        >
                                            <InputErrorText
                                                text={errors.businessWebsite}
                                            />
                                        </div>
                                    )}
                                <DialogTooltip
                                    text={BETA_TOOLTIP_TEXT}
                                    childComponent={
                                        <span
                                            className={`${classes.betaBadge} ${classes.betaBadgeColumn}`}
                                        >
                                            BETA
                                        </span>
                                    }
                                />
                            </div>
                        )}
                    </div>
                    <div className={classes.textareaFieldContainer}>
                        <FormFieldTitle
                            label={
                                <>
                                    Production Location Description
                                    <IconComponent
                                        className={classes.helpTooltip}
                                        title="Provide a brief overview of what this production location manufactures and its main business activities"
                                    />
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
                            onBlur={handleBlur}
                            placeholder="Parent company name"
                            error={
                                touched.parentCompanyName &&
                                !!errors.parentCompanyName
                            }
                            InputProps={{
                                classes: {
                                    input: classes.inputStyles,
                                    notchedOutline:
                                        classes.notchedOutlineStyles,
                                },
                            }}
                        />
                        {touched.parentCompanyName && errors.parentCompanyName && (
                            <div className={classes.errorWrapStyles}>
                                <InputErrorText
                                    text={errors.parentCompanyName}
                                />
                            </div>
                        )}
                    </div>
                    <div className={classes.doubleFieldContainer}>
                        <div className={classes.fieldContainer}>
                            <FormFieldTitle
                                label={
                                    <>
                                        Office Name
                                        <IconComponent
                                            className={classes.helpTooltip}
                                            title="Name of the corporate office or headquarters"
                                        />
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
                                        <IconComponent
                                            className={classes.helpTooltip}
                                            title="Physical address of the office location"
                                        />
                                    </>
                                }
                                classes={{ title: classes.formLabel }}
                            />
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
                                    <InputErrorText
                                        text={errors.officeAddress}
                                    />
                                </div>
                            )}
                        </div>
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
                            value={
                                (countryOptions || []).find(
                                    option =>
                                        option.value ===
                                        formData.officeCountryCode,
                                ) || null
                            }
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
                    <div className={classes.doubleFieldContainer}>
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
                                onChange={values =>
                                    handleChange('sectors', values)
                                }
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
                                        <IconComponent
                                            className={classes.helpTooltip}
                                            title={
                                                enabledTaxonomy
                                                    ? LOCATION_TYPES_TAXONOMY_TOOLTIP
                                                    : LOCATION_TYPES_TOOLTIP
                                            }
                                        />
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
                                    placeholder={
                                        LOCATION_TYPE_SELECT_PLACEHOLDER
                                    }
                                    styles={getSelectStyles(
                                        touched.facilityType &&
                                            !!errors.facilityType,
                                        selectStyles,
                                    )}
                                    components={{
                                        DropdownIndicator: null,
                                        IndicatorSeparator: null,
                                    }}
                                />
                            )}
                            {touched.facilityType && errors.facilityType && (
                                <div className={classes.errorWrapStyles}>
                                    <InputErrorText
                                        text={errors.facilityType}
                                    />
                                </div>
                            )}
                        </div>
                    </div>
                    <div className={classes.doubleFieldContainer}>
                        <div className={classes.fieldContainer}>
                            <FormFieldTitle
                                label={
                                    <>
                                        Processing Type(s)
                                        <IconComponent
                                            className={classes.helpTooltip}
                                            title={
                                                enabledTaxonomy
                                                    ? PROCESSING_TYPES_TAXONOMY_TOOLTIP
                                                    : PROCESSING_TYPES_TOOLTIP
                                            }
                                        />
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
                                    value={
                                        formData.facilityProductionTypes || []
                                    }
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
                                    value={
                                        formData.facilityProductionTypes || []
                                    }
                                    onChange={values =>
                                        handleChange(
                                            'facilityProductionTypes',
                                            values,
                                        )
                                    }
                                    placeholder={
                                        PROCESSING_TYPE_SELECT_PLACEHOLDER
                                    }
                                    styles={getSelectStyles(
                                        touched.facilityProductionTypes &&
                                            !!errors.facilityProductionTypes,
                                        selectStyles,
                                    )}
                                    components={{
                                        DropdownIndicator: null,
                                        IndicatorSeparator: null,
                                    }}
                                />
                            )}
                            {touched.facilityProductionTypes &&
                                errors.facilityProductionTypes && (
                                    <div className={classes.errorWrapStyles}>
                                        <InputErrorText
                                            text={
                                                errors.facilityProductionTypes
                                            }
                                        />
                                    </div>
                                )}
                        </div>
                        <div className={classes.fieldContainer}>
                            <FormFieldTitle
                                label={
                                    <>
                                        Product Types
                                        <IconComponent
                                            className={classes.helpTooltip}
                                            title={PRODUCT_TYPES_TOOLTIP}
                                        />
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
                                placeholder={PRODUCT_TYPE_SELECT_PLACEHOLDER}
                                styles={getSelectStyles(
                                    touched.facilityProductTypes &&
                                        !!errors.facilityProductTypes,
                                    selectStyles,
                                )}
                                components={{
                                    DropdownIndicator: null,
                                    IndicatorSeparator: null,
                                }}
                            />
                            {touched.facilityProductTypes &&
                                errors.facilityProductTypes && (
                                    <div className={classes.errorWrapStyles}>
                                        <InputErrorText
                                            text={errors.facilityProductTypes}
                                        />
                                    </div>
                                )}
                        </div>
                    </div>
                    <div className={classes.doubleFieldContainer}>
                        <div className={classes.fieldContainer}>
                            <FormFieldTitle
                                label={
                                    <>
                                        Number of Workers
                                        <IconComponent
                                            className={classes.helpTooltip}
                                            title="Total number of employees working at this production location, can be a number or a range (e.g., 100, 100-150)"
                                        />
                                    </>
                                }
                                classes={{ title: classes.formLabel }}
                            />
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
                                    <InputErrorText
                                        text={errors.numberOfWorkers}
                                    />
                                </div>
                            )}
                        </div>
                        <div className={classes.fieldContainer}>
                            <FormFieldTitle
                                label={
                                    <>
                                        Percentage of Female Workers
                                        <IconComponent
                                            className={classes.helpTooltip}
                                            title="Percentage of female employees out of the total workforce at this location (0–100). You may include a % sign."
                                        />
                                    </>
                                }
                                classes={{ title: classes.formLabel }}
                            />
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
                                placeholder="e.g., 45 (or 45%)"
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
                    </div>
                    <div className={classes.doubleFieldContainer}>
                        <div className={classes.fieldContainer}>
                            <FormFieldTitle
                                label={
                                    <>
                                        Minimum Order Quantity
                                        <IconComponent
                                            className={classes.helpTooltip}
                                            title="Smallest order quantity this production location will accept from customers"
                                        />
                                    </>
                                }
                                classes={{ title: classes.formLabel }}
                            />
                            <TextField
                                fullWidth
                                variant="outlined"
                                value={
                                    formData.facilityMinimumOrderQuantity || ''
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
                                    <span
                                        className={`${classes.betaBadge} ${classes.betaBadgeColumn}`}
                                    >
                                        BETA
                                    </span>
                                }
                            />
                        </div>
                        <div className={classes.fieldContainer}>
                            <FormFieldTitle
                                label={
                                    <>
                                        Average Lead Time
                                        <IconComponent
                                            className={classes.helpTooltip}
                                            title="Typical time required from order confirmation to product delivery"
                                        />
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
                                            text={
                                                errors.facilityAverageLeadTime
                                            }
                                        />
                                    </div>
                                )}
                            <DialogTooltip
                                text={BETA_TOOLTIP_TEXT}
                                childComponent={
                                    <span
                                        className={`${classes.betaBadge} ${classes.betaBadgeColumn}`}
                                    >
                                        BETA
                                    </span>
                                }
                            />
                        </div>
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
                <section className={classes.doubleFieldContainer}>
                    <div className={classes.fieldContainer}>
                        <FormFieldTitle
                            label={
                                <>
                                    Affiliations
                                    <IconComponent
                                        className={classes.helpTooltip}
                                        title="Organizations, parent companies, or partner entities your facility is formally connected to"
                                    />
                                </>
                            }
                            classes={{ title: classes.formLabel }}
                        />
                        <FormFieldHint text="Select any relevant options" />
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
                            components={{
                                DropdownIndicator: null,
                                IndicatorSeparator: null,
                            }}
                        />
                        <DialogTooltip
                            text={BETA_TOOLTIP_TEXT}
                            childComponent={
                                <span
                                    className={`${classes.betaBadge} ${classes.betaBadgeColumnWithHint}`}
                                >
                                    BETA
                                </span>
                            }
                        />
                    </div>
                    <div className={classes.fieldContainer}>
                        <FormFieldTitle
                            label="Certifications / Standards / Regulations"
                            classes={{ title: classes.formLabel }}
                        />
                        <FormFieldHint text="Select any relevant options" />
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
                            components={{
                                DropdownIndicator: null,
                                IndicatorSeparator: null,
                            }}
                        />
                        <DialogTooltip
                            text={BETA_TOOLTIP_TEXT}
                            childComponent={
                                <span
                                    className={`${classes.betaBadge} ${classes.betaBadgeColumnWithHint}`}
                                >
                                    BETA
                                </span>
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
                            className={`${classes.sectionIconWrapper} ${classes.greenBg}`}
                        >
                            <Spa
                                className={`${classes.sectionIcon} ${classes.greenIcon}`}
                            />
                        </div>
                        Environmental Data
                    </Typography>
                    <div className={classes.switchContainer}>
                        <Switch
                            checked={isFreeEmissionsEstimateVisible}
                            onChange={(_, checked) => {
                                setIsFreeEmissionsEstimateVisible(checked);
                            }}
                            color="primary"
                        />
                    </div>
                </div>
                <Typography className={classes.sectionDescription}>
                    Emissions estimate and energy consumption data.
                </Typography>
            </div>
            {isFreeEmissionsEstimateVisible && (
                <div className={classes.emissionsEstimateContainer}>
                    <ClaimEmissionsEstimate
                        onValidationChange={setClaimEmissionsEstimateHasErrors}
                        formData={emissionsFormData}
                        onEmissionsValueChange={onEmissionsValueChange}
                        onEmissionsEnabledChange={onEmissionsEnabledChange}
                    />
                </div>
            )}
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
    onEmissionsValidationChange: func,
    emissionsFormData: object,
    onEmissionsValueChange: func,
    onEmissionsEnabledChange: func,
};

ProfileStep.defaultProps = {
    touched: {},
    errors: {},
    countryOptions: null,
    processingTypeOptions: null,
    onEmissionsValidationChange: null,
    emissionsFormData: null,
    onEmissionsValueChange: null,
    onEmissionsEnabledChange: null,
};

export default withStyles(profileStepStyles)(withScrollReset(ProfileStep));
