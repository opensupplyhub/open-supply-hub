import React from 'react';
import { func, object } from 'prop-types';
import { connect } from 'react-redux';
import EmissionsEstimateForm from '../../../FreeEmissionsEstimate/EmissionsEstimateForm';
import { updateClaimFormField } from '../../../../actions/claimForm';

/**
 * Wrapper component for EmissionsEstimateForm connected to claimForm Redux state.
 * Used in the initial claim flow (ProfileStep).
 */
const ClaimEmissionsEstimate = ({
    formData,
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
    onValidationChange,
}) => (
    <EmissionsEstimateForm
        formData={formData}
        updateOpeningDate={updateOpeningDate}
        updateClosingDate={updateClosingDate}
        updateEstimatedAnnualThroughput={updateEstimatedAnnualThroughput}
        updateEnergyCoal={updateEnergyCoal}
        updateEnergyNaturalGas={updateEnergyNaturalGas}
        updateEnergyDiesel={updateEnergyDiesel}
        updateEnergyKerosene={updateEnergyKerosene}
        updateEnergyBiomass={updateEnergyBiomass}
        updateEnergyCharcoal={updateEnergyCharcoal}
        updateEnergyAnimalWaste={updateEnergyAnimalWaste}
        updateEnergyElectricity={updateEnergyElectricity}
        updateEnergyOther={updateEnergyOther}
        updateEnergyCoalEnabled={updateEnergyCoalEnabled}
        updateEnergyNaturalGasEnabled={updateEnergyNaturalGasEnabled}
        updateEnergyDieselEnabled={updateEnergyDieselEnabled}
        updateEnergyKeroseneEnabled={updateEnergyKeroseneEnabled}
        updateEnergyBiomassEnabled={updateEnergyBiomassEnabled}
        updateEnergyCharcoalEnabled={updateEnergyCharcoalEnabled}
        updateEnergyAnimalWasteEnabled={updateEnergyAnimalWasteEnabled}
        updateEnergyElectricityEnabled={updateEnergyElectricityEnabled}
        updateEnergyOtherEnabled={updateEnergyOtherEnabled}
        onValidationChange={onValidationChange}
        disabled={false}
    />
);

ClaimEmissionsEstimate.propTypes = {
    formData: object.isRequired,
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
    updateOpeningDate: date =>
        dispatch(updateClaimFormField({ field: 'openingDate', value: date })),
    updateClosingDate: date =>
        dispatch(updateClaimFormField({ field: 'closingDate', value: date })),
    updateEstimatedAnnualThroughput: value =>
        dispatch(
            updateClaimFormField({
                field: 'estimatedAnnualThroughput',
                value,
            }),
        ),
    updateEnergyCoal: value =>
        dispatch(updateClaimFormField({ field: 'energyCoal', value })),
    updateEnergyNaturalGas: value =>
        dispatch(updateClaimFormField({ field: 'energyNaturalGas', value })),
    updateEnergyDiesel: value =>
        dispatch(updateClaimFormField({ field: 'energyDiesel', value })),
    updateEnergyKerosene: value =>
        dispatch(updateClaimFormField({ field: 'energyKerosene', value })),
    updateEnergyBiomass: value =>
        dispatch(updateClaimFormField({ field: 'energyBiomass', value })),
    updateEnergyCharcoal: value =>
        dispatch(updateClaimFormField({ field: 'energyCharcoal', value })),
    updateEnergyAnimalWaste: value =>
        dispatch(updateClaimFormField({ field: 'energyAnimalWaste', value })),
    updateEnergyElectricity: value =>
        dispatch(updateClaimFormField({ field: 'energyElectricity', value })),
    updateEnergyOther: value =>
        dispatch(updateClaimFormField({ field: 'energyOther', value })),
    updateEnergyCoalEnabled: enabled =>
        dispatch(
            updateClaimFormField({
                field: 'energyCoalEnabled',
                value: enabled,
            }),
        ),
    updateEnergyNaturalGasEnabled: enabled =>
        dispatch(
            updateClaimFormField({
                field: 'energyNaturalGasEnabled',
                value: enabled,
            }),
        ),
    updateEnergyDieselEnabled: enabled =>
        dispatch(
            updateClaimFormField({
                field: 'energyDieselEnabled',
                value: enabled,
            }),
        ),
    updateEnergyKeroseneEnabled: enabled =>
        dispatch(
            updateClaimFormField({
                field: 'energyKeroseneEnabled',
                value: enabled,
            }),
        ),
    updateEnergyBiomassEnabled: enabled =>
        dispatch(
            updateClaimFormField({
                field: 'energyBiomassEnabled',
                value: enabled,
            }),
        ),
    updateEnergyCharcoalEnabled: enabled =>
        dispatch(
            updateClaimFormField({
                field: 'energyCharcoalEnabled',
                value: enabled,
            }),
        ),
    updateEnergyAnimalWasteEnabled: enabled =>
        dispatch(
            updateClaimFormField({
                field: 'energyAnimalWasteEnabled',
                value: enabled,
            }),
        ),
    updateEnergyElectricityEnabled: enabled =>
        dispatch(
            updateClaimFormField({
                field: 'energyElectricityEnabled',
                value: enabled,
            }),
        ),
    updateEnergyOtherEnabled: enabled =>
        dispatch(
            updateClaimFormField({
                field: 'energyOtherEnabled',
                value: enabled,
            }),
        ),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(ClaimEmissionsEstimate);
