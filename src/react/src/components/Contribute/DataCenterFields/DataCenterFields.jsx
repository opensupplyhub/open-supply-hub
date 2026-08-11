import React, { useState } from 'react';
import { object } from 'prop-types';
import Typography from '@material-ui/core/Typography';
import TextField from '@material-ui/core/TextField';
import Collapse from '@material-ui/core/Collapse';
import { withStyles } from '@material-ui/core/styles';

import ExpandToggleChevron from '../../Shared/ExpandToggleChevron/ExpandToggleChevron.jsx';
import InputErrorText from '../InputErrorText';
import { DATA_CENTER_FORM_SECTIONS } from './constants';
import dataCenterFieldsStyles from './styles';

/**
 * Data-center-specific SLC form sections (OSDEV-3074). Rendered when the
 * contributor selects Data Center as the location type. Sections are
 * collapsible and collapsed by default; all fields are optional free text.
 * Measures with units render as a value + units input pair.
 */
const DataCenterFields = ({ classes, contributionForm }) => {
    const [openSections, setOpenSections] = useState({});

    const toggleSection = label =>
        setOpenSections(previous => ({
            ...previous,
            [label]: !previous[label],
        }));

    const handleFieldChange = formName => event => {
        contributionForm.setFieldValue(formName, event.target.value);
        contributionForm.setFieldTouched(formName, true, false);
    };

    const renderInput = (formName, label, placeholder) => {
        const hasError =
            contributionForm.touched[formName] &&
            !!contributionForm.errors[formName];

        return (
            <TextField
                id={`dc_${formName}`}
                variant="outlined"
                className={classes.textInputStyles}
                value={contributionForm.values[formName] ?? ''}
                onChange={handleFieldChange(formName)}
                placeholder={placeholder}
                error={hasError}
                helperText={
                    hasError && (
                        <InputErrorText
                            text={contributionForm.errors[formName]}
                        />
                    )
                }
                FormHelperTextProps={{ className: classes.helperText }}
                /*
                `inputProps` (lowercase) targets the native <input>, so the
                accessible name belongs to the focusable control, while
                `InputProps` (capital) targets the Input wrapper and is used
                only for styling. They are separate MUI APIs, but
                react/jsx-no-duplicate-props is configured with ignoreCase and
                reports them as duplicates.
                */
                inputProps={{ 'aria-label': label }}
                // eslint-disable-next-line react/jsx-no-duplicate-props
                InputProps={{
                    classes: {
                        notchedOutline: classes.notchedOutlineStyles,
                    },
                }}
            />
        );
    };

    return (
        <div data-testid="data-center-fields">
            <Typography component="h2" className={classes.sectionsTitle}>
                Data Center Details
            </Typography>
            <Typography component="h4" className={classes.sectionsSubTitle}>
                All fields are optional — enter whatever information is
                available from your source.
            </Typography>
            {DATA_CENTER_FORM_SECTIONS.map(section => {
                const isOpen = !!openSections[section.label];
                return (
                    <div key={section.label} className={classes.section}>
                        <div
                            className={classes.sectionHeader}
                            role="button"
                            tabIndex={0}
                            aria-expanded={isOpen}
                            onClick={() => toggleSection(section.label)}
                            onKeyDown={event => {
                                if (
                                    event.key === 'Enter' ||
                                    event.key === ' '
                                ) {
                                    event.preventDefault();
                                    toggleSection(section.label);
                                }
                            }}
                            data-testid={`data-center-section-${section.label}`}
                        >
                            <Typography
                                component="h3"
                                className={classes.sectionTitle}
                            >
                                {section.label}
                            </Typography>
                            <ExpandToggleChevron
                                isExpanded={isOpen}
                                className={classes.chevron}
                                expandLessTestId={`data-center-section-expand-less-${section.label}`}
                                expandMoreTestId={`data-center-section-expand-more-${section.label}`}
                            />
                        </div>
                        <Collapse in={isOpen}>
                            <div className={classes.sectionContent}>
                                {section.fields.map(field => (
                                    <div
                                        key={field.formName}
                                        className={classes.fieldWrap}
                                    >
                                        <Typography
                                            component="h4"
                                            className={classes.fieldLabel}
                                        >
                                            {field.label}
                                        </Typography>
                                        {field.description ? (
                                            <Typography
                                                component="h5"
                                                className={
                                                    classes.fieldDescription
                                                }
                                            >
                                                {field.description}
                                            </Typography>
                                        ) : null}
                                        {field.unitsFormName ? (
                                            <div className={classes.unitsRow}>
                                                <div
                                                    className={
                                                        classes.unitsValue
                                                    }
                                                >
                                                    {renderInput(
                                                        field.formName,
                                                        field.label,
                                                        `Enter the ${field.label.toLowerCase()}`,
                                                    )}
                                                </div>
                                                <div
                                                    className={
                                                        classes.unitsUnit
                                                    }
                                                >
                                                    {renderInput(
                                                        field.unitsFormName,
                                                        `${field.label} units`,
                                                        'Units (e.g. MW)',
                                                    )}
                                                </div>
                                            </div>
                                        ) : (
                                            renderInput(
                                                field.formName,
                                                field.label,
                                                `Enter the ${field.label.toLowerCase()}`,
                                            )
                                        )}
                                    </div>
                                ))}
                            </div>
                        </Collapse>
                    </div>
                );
            })}
        </div>
    );
};

DataCenterFields.propTypes = {
    classes: object.isRequired,
    contributionForm: object.isRequired,
};

export default withStyles(dataCenterFieldsStyles)(DataCenterFields);
