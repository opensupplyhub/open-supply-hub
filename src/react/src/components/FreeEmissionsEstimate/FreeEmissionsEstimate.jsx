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
    onEmissionsValueChange,
    onEmissionsEnabledChange,
    onValidationChange,
}) => (
    <EmissionsEstimateForm
        formData={formData}
        onEmissionsValueChange={onEmissionsValueChange}
        onEmissionsEnabledChange={onEmissionsEnabledChange}
        onValidationChange={onValidationChange}
        disabled={fetching}
    />
);

FreeEmissionsEstimate.propTypes = {
    formData: object.isRequired,
    fetching: bool.isRequired,
    onEmissionsValueChange: func.isRequired,
    onEmissionsEnabledChange: func.isRequired,
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

const mapDispatchToProps = dispatch => {
    const valueDispatchers = {
        openingDate: date => dispatch(updateClaimOpeningDate(date)),
        closingDate: date => dispatch(updateClaimClosingDate(date)),
        estimatedAnnualThroughput: value =>
            dispatch(updateClaimEstimatedAnnualThroughput(value)),
        energyCoal: value => dispatch(updateClaimEnergyCoal(value)),
        energyNaturalGas: value => dispatch(updateClaimEnergyNaturalGas(value)),
        energyDiesel: value => dispatch(updateClaimEnergyDiesel(value)),
        energyKerosene: value => dispatch(updateClaimEnergyKerosene(value)),
        energyBiomass: value => dispatch(updateClaimEnergyBiomass(value)),
        energyCharcoal: value => dispatch(updateClaimEnergyCharcoal(value)),
        energyAnimalWaste: value =>
            dispatch(updateClaimEnergyAnimalWaste(value)),
        energyElectricity: value =>
            dispatch(updateClaimEnergyElectricity(value)),
        energyOther: value => dispatch(updateClaimEnergyOther(value)),
    };

    const enabledDispatchers = {
        energyCoalEnabled: enabled =>
            dispatch(updateClaimEnergyCoalEnabled(enabled)),
        energyNaturalGasEnabled: enabled =>
            dispatch(updateClaimEnergyNaturalGasEnabled(enabled)),
        energyDieselEnabled: enabled =>
            dispatch(updateClaimEnergyDieselEnabled(enabled)),
        energyKeroseneEnabled: enabled =>
            dispatch(updateClaimEnergyKeroseneEnabled(enabled)),
        energyBiomassEnabled: enabled =>
            dispatch(updateClaimEnergyBiomassEnabled(enabled)),
        energyCharcoalEnabled: enabled =>
            dispatch(updateClaimEnergyCharcoalEnabled(enabled)),
        energyAnimalWasteEnabled: enabled =>
            dispatch(updateClaimEnergyAnimalWasteEnabled(enabled)),
        energyElectricityEnabled: enabled =>
            dispatch(updateClaimEnergyElectricityEnabled(enabled)),
        energyOtherEnabled: enabled =>
            dispatch(updateClaimEnergyOtherEnabled(enabled)),
    };

    return {
        onEmissionsValueChange: (field, value) =>
            valueDispatchers[field]?.(value),
        onEmissionsEnabledChange: (field, enabled) =>
            enabledDispatchers[field]?.(enabled),
    };
};

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(FreeEmissionsEstimate);
