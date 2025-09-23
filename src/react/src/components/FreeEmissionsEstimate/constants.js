const freeEmissionsEstimateFormConfig = Object.freeze({
    title: Object.freeze({
        label: '🌍 Free Emissions Estimates',
    }),
    description: Object.freeze({
        label:
            'Fill in these fields, and Open Supply Hub—together with Climate TRACE—will provide a free emissions estimate for this location. This also helps your partners calculate emissions across their entire value chain.',
    }),
    openingDateField: Object.freeze({
        id: 'opening-date',
        label: 'Opening Date',
        placeholder: 'Select year',
        valueFieldName: 'openingDate',
    }),
    closingDateField: Object.freeze({
        id: 'closing-date',
        label: 'Closing Date',
        placeholder: 'Select month/year',
        valueFieldName: 'closingDate',
    }),
    estimatedAnnualThroughputField: Object.freeze({
        id: 'estimated-annual-throughput',
        label: 'Estimated Annual Throughput',
        placeholder: 'Enter value in kg/year',
        valueFieldName: 'estimatedAnnualThroughput',
    }),
    energyConsumptionLabel: Object.freeze({
        label: 'Actual Annual Energy Consumption',
    }),
    energySourcesData: Object.freeze([
        Object.freeze({
            source: Object.freeze({
                id: 'energy-coal',
                label: 'Coal',
                unit: 'J',
                placeholder: 'Enter value in J',
            }),
            enabledFieldName: 'energyCoalEnabled',
            valueFieldName: 'energyCoal',
        }),
        Object.freeze({
            source: Object.freeze({
                id: 'energy-natural-gas',
                label: 'Natural Gas',
                unit: 'J',
                placeholder: 'Enter value in J',
            }),
            enabledFieldName: 'energyNaturalGasEnabled',
            valueFieldName: 'energyNaturalGas',
        }),
        Object.freeze({
            source: Object.freeze({
                id: 'energy-diesel',
                label: 'Diesel',
                unit: 'J',
                placeholder: 'Enter value in J',
            }),
            enabledFieldName: 'energyDieselEnabled',
            valueFieldName: 'energyDiesel',
        }),
        Object.freeze({
            source: Object.freeze({
                id: 'energy-kerosene',
                label: 'Kerosene',
                unit: 'J',
                placeholder: 'Enter value in J',
            }),
            enabledFieldName: 'energyKeroseneEnabled',
            valueFieldName: 'energyKerosene',
        }),
        Object.freeze({
            source: Object.freeze({
                id: 'energy-biomass',
                label: 'Biomass',
                unit: 'J',
                placeholder: 'Enter value in J',
            }),
            enabledFieldName: 'energyBiomassEnabled',
            valueFieldName: 'energyBiomass',
        }),
        Object.freeze({
            source: Object.freeze({
                id: 'energy-charcoal',
                label: 'Charcoal',
                unit: 'J',
                placeholder: 'Enter value in J',
            }),
            enabledFieldName: 'energyCharcoalEnabled',
            valueFieldName: 'energyCharcoal',
        }),
        Object.freeze({
            source: Object.freeze({
                id: 'energy-animal-waste',
                label: 'Animal Waste',
                unit: 'J',
                placeholder: 'Enter value in J',
            }),
            enabledFieldName: 'energyAnimalWasteEnabled',
            valueFieldName: 'energyAnimalWaste',
        }),
        Object.freeze({
            source: Object.freeze({
                id: 'energy-electricity',
                label: 'Electricity',
                unit: 'MWh',
                placeholder: 'Enter value in MWh',
            }),
            enabledFieldName: 'energyElectricityEnabled',
            valueFieldName: 'energyElectricity',
        }),
        Object.freeze({
            source: Object.freeze({
                id: 'energy-other',
                label: 'Other',
                unit: 'J',
                placeholder: 'Enter value in J',
            }),
            enabledFieldName: 'energyOtherEnabled',
            valueFieldName: 'energyOther',
        }),
    ]),
});

export default freeEmissionsEstimateFormConfig;
