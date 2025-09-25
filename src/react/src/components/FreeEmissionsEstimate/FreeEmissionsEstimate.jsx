import React from 'react';
import { bool, func, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import { connect } from 'react-redux';
import Typography from '@material-ui/core/Typography';
import TextField from '@material-ui/core/TextField';
import InputLabel from '@material-ui/core/InputLabel';
import Grid from '@material-ui/core/Grid';
import InfiniteScrollYearDropdown from './InfiniteScrollYearDropdown.jsx';
import MonthYearPicker from './MonthYearPicker.jsx';
import InputErrorText from '../Contribute/InputErrorText.jsx';
import EnergySourceInput from './EnergySourceInput.jsx';

import {
    updateClaimOpeningDate,
    updateClaimClosingDate,
    updateClaimEstimatedAnnualThroughput,
    updateClaimEnergyCoal,
    updateClaimEnergyNaturalGas,
    updateClaimEnergyDiesel,
    updateClaimEnergyKerosene,
    updateClaimEnergyBiomass,
    updateClaimEnergyCharcoal,
    updateClaimEnergyAnimalWaste,
    updateClaimEnergyElectricity,
    updateClaimEnergyOther,
    updateClaimEnergyCoalEnabled,
    updateClaimEnergyNaturalGasEnabled,
    updateClaimEnergyDieselEnabled,
    updateClaimEnergyKeroseneEnabled,
    updateClaimEnergyBiomassEnabled,
    updateClaimEnergyCharcoalEnabled,
    updateClaimEnergyAnimalWasteEnabled,
    updateClaimEnergyElectricityEnabled,
    updateClaimEnergyOtherEnabled,
} from '../../actions/claimFacility.js';

import { freeEmissionsEstimateStyles } from './styles.js';
import { useFreeEmissionsEstimateForm, useFormFieldSync } from './hooks.js';
import { freeEmissionsEstimateFormConfig } from './constants.js';

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
    fetching,
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
    classes,
}) => {
    // Initialize the form.
    const freeEmissionsEstimateForm = useFreeEmissionsEstimateForm(formData);

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
            <Grid container spacing={8}>
                <Grid item xs={12} md={6}>
                    <InfiniteScrollYearDropdown
                        label={openingDateField.label}
                        name={openingDateField.valueFieldName}
                        value={freeEmissionsEstimateForm.values.openingDate}
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
                        disabled={fetching}
                        placeholder={openingDateField.placeholder}
                        error={openingDateHasError}
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
                    />
                </Grid>
                <Grid item xs={12} md={6}>
                    <MonthYearPicker
                        label={closingDateField.label}
                        name={closingDateField.valueFieldName}
                        value={freeEmissionsEstimateForm.values.closingDate}
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
                        disabled={fetching}
                        placeholder={closingDateField.placeholder}
                        error={closingDateHasError}
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
                    />
                </Grid>
            </Grid>
            <Grid container spacing={8}>
                <Grid item xs={12}>
                    <InputLabel htmlFor={estimatedAnnualThroughputField.id}>
                        <Typography
                            variant="subheading"
                            className={classes.fieldLabel}
                        >
                            {estimatedAnnualThroughputField.label}
                        </Typography>
                    </InputLabel>
                </Grid>
                <Grid item xs={12}>
                    <TextField
                        id={estimatedAnnualThroughputField.id}
                        name={estimatedAnnualThroughputField.valueFieldName}
                        variant="outlined"
                        fullWidth
                        value={
                            freeEmissionsEstimateForm.values
                                .estimatedAnnualThroughput
                        }
                        placeholder={estimatedAnnualThroughputField.placeholder}
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
                        disabled={fetching}
                        error={estimatedAnnualThroughputHasError}
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
                    <Grid item xs={12} key={energyData.source.id}>
                        <EnergySourceInput
                            source={energyData.source}
                            freeEmissionsEstimateForm={
                                freeEmissionsEstimateForm
                            }
                            enabledFieldName={energyData.enabledFieldName}
                            valueFieldName={energyData.valueFieldName}
                            disabled={fetching}
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
    fetching: bool.isRequired,
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
};

const mapStateToProps = ({
    claimFacility: {
        claimData: { formData, fetching },
    },
}) => ({
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
    fetching,
});

const mapDispatchToProps = dispatch => ({
    updateOpeningDate: date => dispatch(updateClaimOpeningDate(date)),
    updateClosingDate: date => dispatch(updateClaimClosingDate(date)),
    updateEstimatedAnnualThroughput: value =>
        dispatch(updateClaimEstimatedAnnualThroughput(value)),
    updateEnergyCoal: value => dispatch(updateClaimEnergyCoal(value)),
    updateEnergyNaturalGas: value =>
        dispatch(updateClaimEnergyNaturalGas(value)),
    updateEnergyDiesel: value => dispatch(updateClaimEnergyDiesel(value)),
    updateEnergyKerosene: value => dispatch(updateClaimEnergyKerosene(value)),
    updateEnergyBiomass: value => dispatch(updateClaimEnergyBiomass(value)),
    updateEnergyCharcoal: value => dispatch(updateClaimEnergyCharcoal(value)),
    updateEnergyAnimalWaste: value =>
        dispatch(updateClaimEnergyAnimalWaste(value)),
    updateEnergyElectricity: value =>
        dispatch(updateClaimEnergyElectricity(value)),
    updateEnergyOther: value => dispatch(updateClaimEnergyOther(value)),
    updateEnergyCoalEnabled: enabled =>
        dispatch(updateClaimEnergyCoalEnabled(enabled)),
    updateEnergyNaturalGasEnabled: enabled =>
        dispatch(updateClaimEnergyNaturalGasEnabled(enabled)),
    updateEnergyDieselEnabled: enabled =>
        dispatch(updateClaimEnergyDieselEnabled(enabled)),
    updateEnergyKeroseneEnabled: enabled =>
        dispatch(updateClaimEnergyKeroseneEnabled(enabled)),
    updateEnergyBiomassEnabled: enabled =>
        dispatch(updateClaimEnergyBiomassEnabled(enabled)),
    updateEnergyCharcoalEnabled: enabled =>
        dispatch(updateClaimEnergyCharcoalEnabled(enabled)),
    updateEnergyAnimalWasteEnabled: enabled =>
        dispatch(updateClaimEnergyAnimalWasteEnabled(enabled)),
    updateEnergyElectricityEnabled: enabled =>
        dispatch(updateClaimEnergyElectricityEnabled(enabled)),
    updateEnergyOtherEnabled: enabled =>
        dispatch(updateClaimEnergyOtherEnabled(enabled)),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(freeEmissionsEstimateStyles)(FreeEmissionsEstimate));
