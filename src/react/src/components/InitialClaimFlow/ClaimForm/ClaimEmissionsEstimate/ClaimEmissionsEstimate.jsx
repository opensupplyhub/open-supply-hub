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
    onEmissionsValueChange,
    onEmissionsEnabledChange,
    onValidationChange,
}) => (
    <EmissionsEstimateForm
        formData={formData}
        onEmissionsValueChange={onEmissionsValueChange}
        onEmissionsEnabledChange={onEmissionsEnabledChange}
        onValidationChange={onValidationChange}
        disabled={false}
    />
);

ClaimEmissionsEstimate.propTypes = {
    formData: object.isRequired,
    onEmissionsValueChange: func.isRequired,
    onEmissionsEnabledChange: func.isRequired,
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
    onEmissionsValueChange: (field, value) =>
        dispatch(updateClaimFormField({ field, value })),
    onEmissionsEnabledChange: (field, value) =>
        dispatch(updateClaimFormField({ field, value })),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(ClaimEmissionsEstimate);
