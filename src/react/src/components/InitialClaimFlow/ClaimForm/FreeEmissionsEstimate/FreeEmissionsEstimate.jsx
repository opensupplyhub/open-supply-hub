import React, { useEffect } from 'react';
import { func, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import { connect } from 'react-redux';
import Typography from '@material-ui/core/Typography';
import TextField from '@material-ui/core/TextField';
import Grid from '@material-ui/core/Grid';
import YearPicker from './YearPicker';
import MonthYearPicker from './MonthYearPicker';
import InputErrorText from '../../../Contribute/InputErrorText';
import EnergySourceInput from './EnergySourceInput';
import LabelWithTooltip from './LabelWithTooltip';

import { freeEmissionsEstimateStyles } from './styles';
import {
    useFreeEmissionsEstimateForm,
    useFormFieldSync,
    useFreeEmissionsEstimateValidation,
} from './hooks';
import { freeEmissionsEstimateFormConfig } from './constants';

import { updateClaimFormField } from '../../../../actions/claimForm';

const {
    title,
    description,
    openingDateField,
    closingDateField,
    estimatedAnnualThroughputField,
    energyConsumptionLabel,
    energySourcesData,
} = freeEmissionsEstimateFormConfig;

const FreeEmissionsEstimate = ({
    // Redux state values.
    formData,
    // Redux dispatch functions.
    updateOpeningDate,
    updateClosingDate,
    updateEstimatedAnnualThroughput,
    updateEnergyCoal,
    updateEnergyNaturalGas,
    updateEnergyDiesel,
    updateEnergyKerosene,
    updateEnergyBiomass,
    updateEnergyCharcoal,
    updateEnergyAnimalWaste,
    updateEnergyElectricity,
    updateEnergyOther,
    updateEnergyCoalEnabled,
    updateEnergyNaturalGasEnabled,
    updateEnergyDieselEnabled,
    updateEnergyKeroseneEnabled,
    updateEnergyBiomassEnabled,
    updateEnergyCharcoalEnabled,
    updateEnergyAnimalWasteEnabled,
    updateEnergyElectricityEnabled,
    updateEnergyOtherEnabled,
    // Other props.
    onValidationChange,
    classes,
}) => {
    // Initialize the form.
    const freeEmissionsEstimateForm = useFreeEmissionsEstimateForm(formData);

    // Track validation.
    const hasValidationErrors = useFreeEmissionsEstimateValidation(
        freeEmissionsEstimateForm,
    );

    /*
    Notify parent when validation state changes.
    It is necessary to notify the parent because the parent is
    responsible for determining if the form is valid via custom
    error handling not by the Formik library as in this component.
    */
    useEffect(() => {
        onValidationChange(hasValidationErrors);
    }, [hasValidationErrors, onValidationChange]);

    /*
    Sync the form values, specifically the Formik form values,
    with the Redux store. It is necessary to sync the form values
    with the Redux store because the form values are not
    automatically updated in the Redux store when the form values
    are changed. And also because after form submission the
    function that handles the whole form takes the values from the
    Redux store.
    */
    useFormFieldSync(
        freeEmissionsEstimateForm.values.openingDate,
        formData.openingDate,
        updateOpeningDate,
    );

    useFormFieldSync(
        freeEmissionsEstimateForm.values.closingDate,
        formData.closingDate,
        updateClosingDate,
    );

    useFormFieldSync(
        freeEmissionsEstimateForm.values.estimatedAnnualThroughput,
        formData.estimatedAnnualThroughput,
        updateEstimatedAnnualThroughput,
    );

    useFormFieldSync(
        freeEmissionsEstimateForm.values.energyCoal,
        formData.energyCoal,
        updateEnergyCoal,
    );
    useFormFieldSync(
        freeEmissionsEstimateForm.values.energyCoalEnabled,
        formData.energyCoalEnabled,
        updateEnergyCoalEnabled,
    );

    useFormFieldSync(
        freeEmissionsEstimateForm.values.energyNaturalGas,
        formData.energyNaturalGas,
        updateEnergyNaturalGas,
    );
    useFormFieldSync(
        freeEmissionsEstimateForm.values.energyNaturalGasEnabled,
        formData.energyNaturalGasEnabled,
        updateEnergyNaturalGasEnabled,
    );

    useFormFieldSync(
        freeEmissionsEstimateForm.values.energyDiesel,
        formData.energyDiesel,
        updateEnergyDiesel,
    );
    useFormFieldSync(
        freeEmissionsEstimateForm.values.energyDieselEnabled,
        formData.energyDieselEnabled,
        updateEnergyDieselEnabled,
    );

    useFormFieldSync(
        freeEmissionsEstimateForm.values.energyKerosene,
        formData.energyKerosene,
        updateEnergyKerosene,
    );
    useFormFieldSync(
        freeEmissionsEstimateForm.values.energyKeroseneEnabled,
        formData.energyKeroseneEnabled,
        updateEnergyKeroseneEnabled,
    );

    useFormFieldSync(
        freeEmissionsEstimateForm.values.energyBiomass,
        formData.energyBiomass,
        updateEnergyBiomass,
    );
    useFormFieldSync(
        freeEmissionsEstimateForm.values.energyBiomassEnabled,
        formData.energyBiomassEnabled,
        updateEnergyBiomassEnabled,
    );

    useFormFieldSync(
        freeEmissionsEstimateForm.values.energyCharcoal,
        formData.energyCharcoal,
        updateEnergyCharcoal,
    );
    useFormFieldSync(
        freeEmissionsEstimateForm.values.energyCharcoalEnabled,
        formData.energyCharcoalEnabled,
        updateEnergyCharcoalEnabled,
    );

    useFormFieldSync(
        freeEmissionsEstimateForm.values.energyAnimalWaste,
        formData.energyAnimalWaste,
        updateEnergyAnimalWaste,
    );
    useFormFieldSync(
        freeEmissionsEstimateForm.values.energyAnimalWasteEnabled,
        formData.energyAnimalWasteEnabled,
        updateEnergyAnimalWasteEnabled,
    );

    useFormFieldSync(
        freeEmissionsEstimateForm.values.energyElectricity,
        formData.energyElectricity,
        updateEnergyElectricity,
    );
    useFormFieldSync(
        freeEmissionsEstimateForm.values.energyElectricityEnabled,
        formData.energyElectricityEnabled,
        updateEnergyElectricityEnabled,
    );

    useFormFieldSync(
        freeEmissionsEstimateForm.values.energyOther,
        formData.energyOther,
        updateEnergyOther,
    );
    useFormFieldSync(
        freeEmissionsEstimateForm.values.energyOtherEnabled,
        formData.energyOtherEnabled,
        updateEnergyOtherEnabled,
    );

    const estimatedAnnualThroughputHasError =
        freeEmissionsEstimateForm.touched.estimatedAnnualThroughput &&
        !!freeEmissionsEstimateForm.errors.estimatedAnnualThroughput;

    const openingDateHasError =
        freeEmissionsEstimateForm.touched.openingDate &&
        !!freeEmissionsEstimateForm.errors.openingDate;

    const closingDateHasError =
        freeEmissionsEstimateForm.touched.closingDate &&
        !!freeEmissionsEstimateForm.errors.closingDate;

    return (
        <div className={classes.emissionsSection}>
            <Typography className={classes.sectionTitle}>
                {title.label}
            </Typography>
            <Typography className={classes.sectionDescription}>
                {description.label}
            </Typography>
            <Grid
                container
                spacing={40}
                className={classes.datePickerContainer}
            >
                <Grid item xs={12} md={6}>
                    <YearPicker
                        value={freeEmissionsEstimateForm.values.openingDate}
                        label={openingDateField.label}
                        tooltipText={openingDateField.tooltipText}
                        placeholder={openingDateField.placeholder}
                        helperText={
                            openingDateHasError && (
                                <InputErrorText
                                    text={
                                        freeEmissionsEstimateForm.errors
                                            .openingDate
                                    }
                                />
                            )
                        }
                        error={openingDateHasError}
                        onChange={value => {
                            freeEmissionsEstimateForm.setFieldValue(
                                openingDateField.valueFieldName,
                                value,
                            );
                            freeEmissionsEstimateForm.setFieldTouched(
                                openingDateField.valueFieldName,
                                true,
                                false,
                            );
                        }}
                    />
                </Grid>
                <Grid item xs={12} md={6}>
                    <MonthYearPicker
                        value={freeEmissionsEstimateForm.values.closingDate}
                        label={closingDateField.label}
                        tooltipText={closingDateField.tooltipText}
                        placeholderMonth={closingDateField.placeholderMonth}
                        placeholderYear={closingDateField.placeholderYear}
                        helperText={
                            closingDateHasError && (
                                <InputErrorText
                                    text={
                                        freeEmissionsEstimateForm.errors
                                            .closingDate
                                    }
                                />
                            )
                        }
                        error={closingDateHasError}
                        onChange={value => {
                            freeEmissionsEstimateForm.setFieldValue(
                                closingDateField.valueFieldName,
                                value,
                            );
                            freeEmissionsEstimateForm.setFieldTouched(
                                closingDateField.valueFieldName,
                                true,
                                false,
                            );
                        }}
                    />
                </Grid>
            </Grid>
            <Grid
                container
                spacing={8}
                className={classes.estimatedAnnualThroughputContainer}
            >
                <Grid item xs={12}>
                    <LabelWithTooltip
                        label={estimatedAnnualThroughputField.label}
                        tooltipText={estimatedAnnualThroughputField.tooltipText}
                    />
                </Grid>
                <Grid item xs={12}>
                    <TextField
                        value={
                            freeEmissionsEstimateForm.values
                                .estimatedAnnualThroughput
                        }
                        placeholder={estimatedAnnualThroughputField.placeholder}
                        helperText={
                            estimatedAnnualThroughputHasError && (
                                <InputErrorText
                                    text={
                                        freeEmissionsEstimateForm.errors
                                            .estimatedAnnualThroughput
                                    }
                                />
                            )
                        }
                        error={estimatedAnnualThroughputHasError}
                        onChange={event => {
                            freeEmissionsEstimateForm.setFieldValue(
                                estimatedAnnualThroughputField.valueFieldName,
                                event.target.value,
                            );
                            freeEmissionsEstimateForm.setFieldTouched(
                                estimatedAnnualThroughputField.valueFieldName,
                                true,
                                false,
                            );
                        }}
                        variant="outlined"
                        fullWidth
                    />
                </Grid>
            </Grid>
            <Grid container spacing={8}>
                <Grid item xs={12}>
                    <Typography
                        variant="subheading"
                        className={classes.energyConsumptionTitle}
                    >
                        {energyConsumptionLabel.label}
                    </Typography>
                </Grid>
                {energySourcesData.map(energyData => (
                    <Grid item xs={12} key={energyData.source.label}>
                        <EnergySourceInput
                            source={energyData.source}
                            freeEmissionsEstimateForm={
                                freeEmissionsEstimateForm
                            }
                            enabledFieldName={energyData.enabledFieldName}
                            valueFieldName={energyData.valueFieldName}
                        />
                    </Grid>
                ))}
            </Grid>
        </div>
    );
};

FreeEmissionsEstimate.propTypes = {
    // Redux state.
    formData: object.isRequired,
    // Redux dispatch functions.
    updateOpeningDate: func.isRequired,
    updateClosingDate: func.isRequired,
    updateEstimatedAnnualThroughput: func.isRequired,
    updateEnergyCoal: func.isRequired,
    updateEnergyNaturalGas: func.isRequired,
    updateEnergyDiesel: func.isRequired,
    updateEnergyKerosene: func.isRequired,
    updateEnergyBiomass: func.isRequired,
    updateEnergyCharcoal: func.isRequired,
    updateEnergyAnimalWaste: func.isRequired,
    updateEnergyElectricity: func.isRequired,
    updateEnergyOther: func.isRequired,
    updateEnergyCoalEnabled: func.isRequired,
    updateEnergyNaturalGasEnabled: func.isRequired,
    updateEnergyDieselEnabled: func.isRequired,
    updateEnergyKeroseneEnabled: func.isRequired,
    updateEnergyBiomassEnabled: func.isRequired,
    updateEnergyCharcoalEnabled: func.isRequired,
    updateEnergyAnimalWasteEnabled: func.isRequired,
    updateEnergyElectricityEnabled: func.isRequired,
    updateEnergyOtherEnabled: func.isRequired,
    // Other props.
    classes: object.isRequired,
    onValidationChange: func.isRequired,
};

const mapStateToProps = ({ claimForm: { formData } }) => ({
    formData: {
        openingDate: formData.openingDate,
        closingDate: formData.closingDate,
        estimatedAnnualThroughput: formData.estimatedAnnualThroughput,
        energyCoal: formData.energyCoal,
        energyNaturalGas: formData.energyNaturalGas,
        energyDiesel: formData.energyDiesel,
        energyKerosene: formData.energyKerosene,
        energyBiomass: formData.energyBiomass,
        energyCharcoal: formData.energyCharcoal,
        energyAnimalWaste: formData.energyAnimalWaste,
        energyElectricity: formData.energyElectricity,
        energyOther: formData.energyOther,
        energyCoalEnabled: formData.energyCoalEnabled,
        energyNaturalGasEnabled: formData.energyNaturalGasEnabled,
        energyDieselEnabled: formData.energyDieselEnabled,
        energyKeroseneEnabled: formData.energyKeroseneEnabled,
        energyBiomassEnabled: formData.energyBiomassEnabled,
        energyCharcoalEnabled: formData.energyCharcoalEnabled,
        energyAnimalWasteEnabled: formData.energyAnimalWasteEnabled,
        energyElectricityEnabled: formData.energyElectricityEnabled,
        energyOtherEnabled: formData.energyOtherEnabled,
    },
});

const mapDispatchToProps = dispatch => ({
    updateOpeningDate: date => dispatch(updateClaimFormField(date)),
    updateClosingDate: date => dispatch(updateClaimFormField(date)),
    updateEstimatedAnnualThroughput: value =>
        dispatch(updateClaimFormField(value)),
    updateEnergyCoal: value => dispatch(updateClaimFormField(value)),
    updateEnergyNaturalGas: value => dispatch(updateClaimFormField(value)),
    updateEnergyDiesel: value => dispatch(updateClaimFormField(value)),
    updateEnergyKerosene: value => dispatch(updateClaimFormField(value)),
    updateEnergyBiomass: value => dispatch(updateClaimFormField(value)),
    updateEnergyCharcoal: value => dispatch(updateClaimFormField(value)),
    updateEnergyAnimalWaste: value => dispatch(updateClaimFormField(value)),
    updateEnergyElectricity: value => dispatch(updateClaimFormField(value)),
    updateEnergyOther: value => dispatch(updateClaimFormField(value)),
    updateEnergyCoalEnabled: enabled => dispatch(updateClaimFormField(enabled)),
    updateEnergyNaturalGasEnabled: enabled =>
        dispatch(updateClaimFormField(enabled)),
    updateEnergyDieselEnabled: enabled =>
        dispatch(updateClaimFormField(enabled)),
    updateEnergyKeroseneEnabled: enabled =>
        dispatch(updateClaimFormField(enabled)),
    updateEnergyBiomassEnabled: enabled =>
        dispatch(updateClaimFormField(enabled)),
    updateEnergyCharcoalEnabled: enabled =>
        dispatch(updateClaimFormField(enabled)),
    updateEnergyAnimalWasteEnabled: enabled =>
        dispatch(updateClaimFormField(enabled)),
    updateEnergyElectricityEnabled: enabled =>
        dispatch(updateClaimFormField(enabled)),
    updateEnergyOtherEnabled: enabled =>
        dispatch(updateClaimFormField(enabled)),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(freeEmissionsEstimateStyles)(FreeEmissionsEstimate));
