import React, { useEffect } from 'react';
import { bool, func, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import { connect } from 'react-redux';
import Typography from '@material-ui/core/Typography';
import TextField from '@material-ui/core/TextField';
import InputLabel from '@material-ui/core/InputLabel';
import Grid from '@material-ui/core/Grid';
import DatePicker from '../DatePicker.jsx';
import InputErrorText from '../Contribute/InputErrorText.jsx';
import EnergySourceInput from './EnergySourceInput.jsx';

import {
    updateClaimOpeningDate,
    updateClaimClosingDate,
    updateClaimAnnualThroughput,
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
import { useFreeEmissionsEstimateForm } from './hooks.js';
import { freeEmissionsEstimateFormFields } from './constants.js';

const {
    title,
    description,
    openingDateForm,
    closingDateForm,
    annualThroughputForm,
    energyConsumptionLabel,
    energySources,
} = freeEmissionsEstimateFormFields;

const FreeEmissionsEstimate = ({
    // Redux state values
    formData,
    fetching,
    // Redux dispatch functions
    updateOpeningDate,
    updateClosingDate,
    updateAnnualThroughput,
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
    // Other props
    classes,
}) => {
    // Initialize Formik form
    const formik = useFreeEmissionsEstimateForm(formData);

    // Sync Formik values with Redux store
    useEffect(() => {
        if (formik.values.openingDate !== formData.openingDate) {
            updateOpeningDate(formik.values.openingDate);
        }
    }, [formik.values.openingDate, formData.openingDate, updateOpeningDate]);

    useEffect(() => {
        if (formik.values.closingDate !== formData.closingDate) {
            updateClosingDate(formik.values.closingDate);
        }
    }, [formik.values.closingDate, formData.closingDate, updateClosingDate]);

    useEffect(() => {
        if (formik.values.annualThroughput !== formData.annualThroughput) {
            updateAnnualThroughput(formik.values.annualThroughput);
        }
    }, [
        formik.values.annualThroughput,
        formData.annualThroughput,
        updateAnnualThroughput,
    ]);

    // Energy sources sync effects
    useEffect(() => {
        if (formik.values.energyCoal !== formData.energyCoal) {
            updateEnergyCoal(formik.values.energyCoal);
        }
    }, [formik.values.energyCoal, formData.energyCoal, updateEnergyCoal]);

    useEffect(() => {
        if (formik.values.energyCoalEnabled !== formData.energyCoalEnabled) {
            updateEnergyCoalEnabled(formik.values.energyCoalEnabled);
        }
    }, [
        formik.values.energyCoalEnabled,
        formData.energyCoalEnabled,
        updateEnergyCoalEnabled,
    ]);

    useEffect(() => {
        if (formik.values.energyNaturalGas !== formData.energyNaturalGas) {
            updateEnergyNaturalGas(formik.values.energyNaturalGas);
        }
    }, [
        formik.values.energyNaturalGas,
        formData.energyNaturalGas,
        updateEnergyNaturalGas,
    ]);

    useEffect(() => {
        if (
            formik.values.energyNaturalGasEnabled !==
            formData.energyNaturalGasEnabled
        ) {
            updateEnergyNaturalGasEnabled(
                formik.values.energyNaturalGasEnabled,
            );
        }
    }, [
        formik.values.energyNaturalGasEnabled,
        formData.energyNaturalGasEnabled,
        updateEnergyNaturalGasEnabled,
    ]);

    useEffect(() => {
        if (formik.values.energyDiesel !== formData.energyDiesel) {
            updateEnergyDiesel(formik.values.energyDiesel);
        }
    }, [formik.values.energyDiesel, formData.energyDiesel, updateEnergyDiesel]);

    useEffect(() => {
        if (
            formik.values.energyDieselEnabled !== formData.energyDieselEnabled
        ) {
            updateEnergyDieselEnabled(formik.values.energyDieselEnabled);
        }
    }, [
        formik.values.energyDieselEnabled,
        formData.energyDieselEnabled,
        updateEnergyDieselEnabled,
    ]);

    useEffect(() => {
        if (formik.values.energyKerosene !== formData.energyKerosene) {
            updateEnergyKerosene(formik.values.energyKerosene);
        }
    }, [
        formik.values.energyKerosene,
        formData.energyKerosene,
        updateEnergyKerosene,
    ]);

    useEffect(() => {
        if (
            formik.values.energyKeroseneEnabled !==
            formData.energyKeroseneEnabled
        ) {
            updateEnergyKeroseneEnabled(formik.values.energyKeroseneEnabled);
        }
    }, [
        formik.values.energyKeroseneEnabled,
        formData.energyKeroseneEnabled,
        updateEnergyKeroseneEnabled,
    ]);

    useEffect(() => {
        if (formik.values.energyBiomass !== formData.energyBiomass) {
            updateEnergyBiomass(formik.values.energyBiomass);
        }
    }, [
        formik.values.energyBiomass,
        formData.energyBiomass,
        updateEnergyBiomass,
    ]);

    useEffect(() => {
        if (
            formik.values.energyBiomassEnabled !== formData.energyBiomassEnabled
        ) {
            updateEnergyBiomassEnabled(formik.values.energyBiomassEnabled);
        }
    }, [
        formik.values.energyBiomassEnabled,
        formData.energyBiomassEnabled,
        updateEnergyBiomassEnabled,
    ]);

    useEffect(() => {
        if (formik.values.energyCharcoal !== formData.energyCharcoal) {
            updateEnergyCharcoal(formik.values.energyCharcoal);
        }
    }, [
        formik.values.energyCharcoal,
        formData.energyCharcoal,
        updateEnergyCharcoal,
    ]);

    useEffect(() => {
        if (
            formik.values.energyCharcoalEnabled !==
            formData.energyCharcoalEnabled
        ) {
            updateEnergyCharcoalEnabled(formik.values.energyCharcoalEnabled);
        }
    }, [
        formik.values.energyCharcoalEnabled,
        formData.energyCharcoalEnabled,
        updateEnergyCharcoalEnabled,
    ]);

    useEffect(() => {
        if (formik.values.energyAnimalWaste !== formData.energyAnimalWaste) {
            updateEnergyAnimalWaste(formik.values.energyAnimalWaste);
        }
    }, [
        formik.values.energyAnimalWaste,
        formData.energyAnimalWaste,
        updateEnergyAnimalWaste,
    ]);

    useEffect(() => {
        if (
            formik.values.energyAnimalWasteEnabled !==
            formData.energyAnimalWasteEnabled
        ) {
            updateEnergyAnimalWasteEnabled(
                formik.values.energyAnimalWasteEnabled,
            );
        }
    }, [
        formik.values.energyAnimalWasteEnabled,
        formData.energyAnimalWasteEnabled,
        updateEnergyAnimalWasteEnabled,
    ]);

    useEffect(() => {
        if (formik.values.energyElectricity !== formData.energyElectricity) {
            updateEnergyElectricity(formik.values.energyElectricity);
        }
    }, [
        formik.values.energyElectricity,
        formData.energyElectricity,
        updateEnergyElectricity,
    ]);

    useEffect(() => {
        if (
            formik.values.energyElectricityEnabled !==
            formData.energyElectricityEnabled
        ) {
            updateEnergyElectricityEnabled(
                formik.values.energyElectricityEnabled,
            );
        }
    }, [
        formik.values.energyElectricityEnabled,
        formData.energyElectricityEnabled,
        updateEnergyElectricityEnabled,
    ]);

    useEffect(() => {
        if (formik.values.energyOther !== formData.energyOther) {
            updateEnergyOther(formik.values.energyOther);
        }
    }, [formik.values.energyOther, formData.energyOther, updateEnergyOther]);

    useEffect(() => {
        if (formik.values.energyOtherEnabled !== formData.energyOtherEnabled) {
            updateEnergyOtherEnabled(formik.values.energyOtherEnabled);
        }
    }, [
        formik.values.energyOtherEnabled,
        formData.energyOtherEnabled,
        updateEnergyOtherEnabled,
    ]);

    const energySourcesData = [
        {
            source: energySources.coal,
            enabledFieldName: 'energyCoalEnabled',
            valueFieldName: 'energyCoal',
        },
        {
            source: energySources.naturalGas,
            enabledFieldName: 'energyNaturalGasEnabled',
            valueFieldName: 'energyNaturalGas',
        },
        {
            source: energySources.diesel,
            enabledFieldName: 'energyDieselEnabled',
            valueFieldName: 'energyDiesel',
        },
        {
            source: energySources.kerosene,
            enabledFieldName: 'energyKeroseneEnabled',
            valueFieldName: 'energyKerosene',
        },
        {
            source: energySources.biomass,
            enabledFieldName: 'energyBiomassEnabled',
            valueFieldName: 'energyBiomass',
        },
        {
            source: energySources.charcoal,
            enabledFieldName: 'energyCharcoalEnabled',
            valueFieldName: 'energyCharcoal',
        },
        {
            source: energySources.animalWaste,
            enabledFieldName: 'energyAnimalWasteEnabled',
            valueFieldName: 'energyAnimalWaste',
        },
        {
            source: energySources.electricity,
            enabledFieldName: 'energyElectricityEnabled',
            valueFieldName: 'energyElectricity',
        },
        {
            source: energySources.other,
            enabledFieldName: 'energyOtherEnabled',
            valueFieldName: 'energyOther',
        },
    ];

    const annualThroughputHasError =
        formik.touched.annualThroughput && formik.errors.annualThroughput;

    return (
        <div className={classes.emissionsSection}>
            <Typography className={classes.sectionTitle}>
                {title.label}
            </Typography>
            <Typography className={classes.sectionDescription}>
                {description.label}
            </Typography>

            <form onSubmit={formik.handleSubmit}>
                <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                        <DatePicker
                            label={openingDateForm.label}
                            name="openingDate"
                            value={formik.values.openingDate}
                            onChange={value =>
                                formik.setFieldValue('openingDate', value)
                            }
                            disabled={fetching}
                            placeholder={openingDateForm.placeholder}
                            fullWidth
                            size="small"
                        />
                    </Grid>

                    <Grid item xs={12} md={6}>
                        <DatePicker
                            label={closingDateForm.label}
                            name="closingDate"
                            value={formik.values.closingDate}
                            onChange={value =>
                                formik.setFieldValue('closingDate', value)
                            }
                            disabled={fetching}
                            placeholder={closingDateForm.placeholder}
                            fullWidth
                            size="small"
                        />
                    </Grid>
                </Grid>

                <div className={classes.inputGroupStyles}>
                    <InputLabel htmlFor="annualThroughput">
                        <Typography
                            variant="subtitle1"
                            style={{ fontWeight: 500 }}
                        >
                            {annualThroughputForm.label}
                        </Typography>
                    </InputLabel>
                    <TextField
                        id="annualThroughput"
                        name="annualThroughput"
                        variant="outlined"
                        size="small"
                        fullWidth
                        value={formik.values.annualThroughput}
                        placeholder={annualThroughputForm.placeholder}
                        onChange={formik.handleChange}
                        onBlur={formik.handleBlur}
                        disabled={fetching}
                        error={annualThroughputHasError}
                        helperText={
                            annualThroughputHasError && (
                                <InputErrorText
                                    text={formik.errors.annualThroughput}
                                />
                            )
                        }
                        style={{ marginTop: '8px' }}
                    />
                </div>

                <div className={classes.inputGroupStyles}>
                    <Typography
                        variant="subtitle1"
                        style={{ fontWeight: 500, marginBottom: '16px' }}
                    >
                        {energyConsumptionLabel.label}
                    </Typography>

                    {energySourcesData.map(energyData => (
                        <EnergySourceInput
                            key={energyData.source.id}
                            source={energyData.source}
                            formik={formik}
                            enabledFieldName={energyData.enabledFieldName}
                            valueFieldName={energyData.valueFieldName}
                            disabled={fetching}
                            classes={classes}
                        />
                    ))}
                </div>
            </form>
        </div>
    );
};

FreeEmissionsEstimate.propTypes = {
    // Redux state
    formData: object.isRequired,
    fetching: bool.isRequired,
    // Redux dispatch functions
    updateOpeningDate: func.isRequired,
    updateClosingDate: func.isRequired,
    updateAnnualThroughput: func.isRequired,
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
    // Other props
    classes: object.isRequired,
};

function mapStateToProps({
    claimFacility: {
        claimData: { formData, fetching },
    },
}) {
    return {
        formData: {
            openingDate: formData.openingDate,
            closingDate: formData.closingDate,
            annualThroughput: formData.annualThroughput,
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
    };
}

function mapDispatchToProps(dispatch) {
    return {
        updateOpeningDate: date => dispatch(updateClaimOpeningDate(date)),
        updateClosingDate: date => dispatch(updateClaimClosingDate(date)),
        updateAnnualThroughput: value =>
            dispatch(updateClaimAnnualThroughput(value)),
        updateEnergyCoal: value => dispatch(updateClaimEnergyCoal(value)),
        updateEnergyNaturalGas: value =>
            dispatch(updateClaimEnergyNaturalGas(value)),
        updateEnergyDiesel: value => dispatch(updateClaimEnergyDiesel(value)),
        updateEnergyKerosene: value =>
            dispatch(updateClaimEnergyKerosene(value)),
        updateEnergyBiomass: value => dispatch(updateClaimEnergyBiomass(value)),
        updateEnergyCharcoal: value =>
            dispatch(updateClaimEnergyCharcoal(value)),
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
    };
}

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(freeEmissionsEstimateStyles)(FreeEmissionsEstimate));
