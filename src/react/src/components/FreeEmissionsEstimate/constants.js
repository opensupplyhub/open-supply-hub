export const freeEmissionsEstimateFormFields = Object.freeze({
    title: Object.freeze({
        label: '🌍 Free Emissions Estimates',
    }),
    description: Object.freeze({
        label:
            'Complete these fields and Open Supply Hub will partner with Climate TRACE to provide you with a free emissions estimate for this location.',
    }),
    openingDateForm: Object.freeze({
        id: 'opening-date',
        label: 'Opening Date',
        placeholder: 'Select year',
    }),
    closingDateForm: Object.freeze({
        id: 'closing-date',
        label: 'Closing Date',
        placeholder: 'Select month/year',
    }),
    annualThroughputForm: Object.freeze({
        id: 'annual-throughput',
        label: 'Actual Annual Throughput',
        placeholder: 'e.g., 10,000 kg/year',
    }),
    energyConsumptionLabel: Object.freeze({
        label: 'Actual Annual Energy Consumption',
    }),
    energySources: Object.freeze({
        coal: Object.freeze({
            id: 'energy-coal',
            label: 'Coal',
            unit: 'J',
            placeholder: 'Enter value in J',
        }),
        naturalGas: Object.freeze({
            id: 'energy-natural-gas',
            label: 'Natural Gas',
            unit: 'J',
            placeholder: 'Enter value in J',
        }),
        diesel: Object.freeze({
            id: 'energy-diesel',
            label: 'Diesel',
            unit: 'J',
            placeholder: 'Enter value in J',
        }),
        kerosene: Object.freeze({
            id: 'energy-kerosene',
            label: 'Kerosene',
            unit: 'J',
            placeholder: 'Enter value in J',
        }),
        biomass: Object.freeze({
            id: 'energy-biomass',
            label: 'Biomass',
            unit: 'J',
            placeholder: 'Enter value in J',
        }),
        charcoal: Object.freeze({
            id: 'energy-charcoal',
            label: 'Charcoal',
            unit: 'J',
            placeholder: 'Enter value in J',
        }),
        animalWaste: Object.freeze({
            id: 'energy-animal-waste',
            label: 'Animal Waste',
            unit: 'J',
            placeholder: 'Enter value in J',
        }),
        electricity: Object.freeze({
            id: 'energy-electricity',
            label: 'Electricity',
            unit: 'MWh',
            placeholder: 'Enter value in MWh',
        }),
        other: Object.freeze({
            id: 'energy-other',
            label: 'Other',
            unit: 'J',
            placeholder: 'Enter value in J',
        }),
    }),
});

export const energySourcesData = Object.freeze([
    Object.freeze({
        source: freeEmissionsEstimateFormFields.energySources.coal,
        enabledFieldName: 'energyCoalEnabled',
        valueFieldName: 'energyCoal',
    }),
    Object.freeze({
        source: freeEmissionsEstimateFormFields.energySources.naturalGas,
        enabledFieldName: 'energyNaturalGasEnabled',
        valueFieldName: 'energyNaturalGas',
    }),
    Object.freeze({
        source: freeEmissionsEstimateFormFields.energySources.diesel,
        enabledFieldName: 'energyDieselEnabled',
        valueFieldName: 'energyDiesel',
    }),
    Object.freeze({
        source: freeEmissionsEstimateFormFields.energySources.kerosene,
        enabledFieldName: 'energyKeroseneEnabled',
        valueFieldName: 'energyKerosene',
    }),
    Object.freeze({
        source: freeEmissionsEstimateFormFields.energySources.biomass,
        enabledFieldName: 'energyBiomassEnabled',
        valueFieldName: 'energyBiomass',
    }),
    Object.freeze({
        source: freeEmissionsEstimateFormFields.energySources.charcoal,
        enabledFieldName: 'energyCharcoalEnabled',
        valueFieldName: 'energyCharcoal',
    }),
    Object.freeze({
        source: freeEmissionsEstimateFormFields.energySources.animalWaste,
        enabledFieldName: 'energyAnimalWasteEnabled',
        valueFieldName: 'energyAnimalWaste',
    }),
    Object.freeze({
        source: freeEmissionsEstimateFormFields.energySources.electricity,
        enabledFieldName: 'energyElectricityEnabled',
        valueFieldName: 'energyElectricity',
    }),
    Object.freeze({
        source: freeEmissionsEstimateFormFields.energySources.other,
        enabledFieldName: 'energyOtherEnabled',
        valueFieldName: 'energyOther',
    }),
]);
