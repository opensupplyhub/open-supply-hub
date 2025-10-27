import React from 'react';
import { bool, func, object } from 'prop-types';
import { connect } from 'react-redux';
import EmissionsEstimateForm from './EmissionsEstimateForm';
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
} from '../../actions/claimFacility';

/**
 * Wrapper component for EmissionsEstimateForm connected to claimFacility Redux state.
 * Used in the claim facility flow (ClaimFacilityAdditionalData, ClaimFacilityStepper).
 */
const FreeEmissionsEstimate = ({
    formData,
    fetching,
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
        disabled={fetching}
    />
);

FreeEmissionsEstimate.propTypes = {
    formData: object.isRequired,
    fetching: bool.isRequired,
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
)(FreeEmissionsEstimate);
