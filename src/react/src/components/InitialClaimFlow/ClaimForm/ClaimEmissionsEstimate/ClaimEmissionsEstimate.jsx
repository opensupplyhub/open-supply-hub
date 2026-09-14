import React from 'react';
import { func, object } from 'prop-types';
import { connect } from 'react-redux';
import EmissionsEstimateForm from '../../../FreeEmissionsEstimate/EmissionsEstimateForm';
import { updateClaimFormField } from '../../../../actions/claimForm';

/**
 * Wrapper component for EmissionsEstimateForm connected to claimForm Redux
 * state. Used in the initial claim flow (ProfileStep).
 *
 * When formData / change handlers are passed in as props (the pending
 * claim edit view, whose form state lives in its own slice — OSDEV-3371),
 * they take precedence over the claimForm slice wiring.
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

const pickEmissionsFields = formData => ({
    openingDate: formData.openingDate,
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
});

const mapStateToProps = ({ claimForm: { formData } }, ownProps) => ({
    formData: pickEmissionsFields(ownProps.formData || formData),
});

const mapDispatchToProps = (dispatch, ownProps) => ({
    onEmissionsValueChange:
        ownProps.onEmissionsValueChange ||
        ((field, value) => dispatch(updateClaimFormField({ field, value }))),
    onEmissionsEnabledChange:
        ownProps.onEmissionsEnabledChange ||
        ((field, value) => dispatch(updateClaimFormField({ field, value }))),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(ClaimEmissionsEstimate);
