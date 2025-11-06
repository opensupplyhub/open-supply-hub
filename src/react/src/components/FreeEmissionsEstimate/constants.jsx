import React from 'react';

export const freeEmissionsEstimateFormConfig = Object.freeze({
    title: Object.freeze({
        label: '🌍 Free Emissions Estimates',
    }),
    description: Object.freeze({
        label: (
            <>
                Fill in these fields, and Open Supply Hub—together with{' '}
                <strong>Climate TRACE</strong>—will provide a free emissions
                estimate for this location. This also helps your partners
                calculate emissions across their entire value chain.
            </>
        ),
    }),
    openingDateField: Object.freeze({
        label: 'Opening Date',
        tooltipText:
            'Enter the date your production location officially started operations.',
        placeholder: 'Select year',
        valueFieldName: 'openingDate',
    }),
    closingDateField: Object.freeze({
        label: 'Closing Date',
        tooltipText:
            'Enter the date your production location permanently stopped operating. Leave blank if still active.',
        placeholderMonth: 'Select month',
        placeholderYear: 'Select year',
        valueFieldName: 'closingDate',
    }),
    estimatedAnnualThroughputField: Object.freeze({
        label: 'Estimated Annual Throughput',
        tooltipText:
            'Total amount of materials or products processed by this location per year.',
        placeholder: 'Enter value in kg/year',
        valueFieldName: 'estimatedAnnualThroughput',
    }),
    energyConsumptionLabel: Object.freeze({
        label: 'Actual Annual Energy Consumption',
        tooltipText:
            "Report your facility's total annual energy consumption by source. You can enter a mix of various energy sources with the checkbox selection. Solid and liquid fuel sources are shown in Joules (J) such as Coal, Natural Gas, Diesel, Kerosene, Biomass, Charcoal, Animal Waste, and Other sources. Electricity is shown in megawatt-hours (MWh).",
    }),
    energySourcesData: Object.freeze([
        Object.freeze({
            source: Object.freeze({
                label: 'Coal',
                unit: 'J',
                placeholder: 'Enter value in J',
            }),
            enabledFieldName: 'energyCoalEnabled',
            valueFieldName: 'energyCoal',
        }),
        Object.freeze({
            source: Object.freeze({
                label: 'Natural Gas',
                unit: 'J',
                placeholder: 'Enter value in J',
            }),
            enabledFieldName: 'energyNaturalGasEnabled',
            valueFieldName: 'energyNaturalGas',
        }),
        Object.freeze({
            source: Object.freeze({
                label: 'Diesel',
                unit: 'J',
                placeholder: 'Enter value in J',
            }),
            enabledFieldName: 'energyDieselEnabled',
            valueFieldName: 'energyDiesel',
        }),
        Object.freeze({
            source: Object.freeze({
                label: 'Kerosene',
                unit: 'J',
                placeholder: 'Enter value in J',
            }),
            enabledFieldName: 'energyKeroseneEnabled',
            valueFieldName: 'energyKerosene',
        }),
        Object.freeze({
            source: Object.freeze({
                label: 'Biomass',
                unit: 'J',
                placeholder: 'Enter value in J',
            }),
            enabledFieldName: 'energyBiomassEnabled',
            valueFieldName: 'energyBiomass',
        }),
        Object.freeze({
            source: Object.freeze({
                label: 'Charcoal',
                unit: 'J',
                placeholder: 'Enter value in J',
            }),
            enabledFieldName: 'energyCharcoalEnabled',
            valueFieldName: 'energyCharcoal',
        }),
        Object.freeze({
            source: Object.freeze({
                label: 'Animal Waste',
                unit: 'J',
                placeholder: 'Enter value in J',
            }),
            enabledFieldName: 'energyAnimalWasteEnabled',
            valueFieldName: 'energyAnimalWaste',
        }),
        Object.freeze({
            source: Object.freeze({
                label: 'Electricity',
                unit: 'MWh',
                placeholder: 'Enter value in MWh',
            }),
            enabledFieldName: 'energyElectricityEnabled',
            valueFieldName: 'energyElectricity',
        }),
        Object.freeze({
            source: Object.freeze({
                label: 'Other',
                unit: 'J',
                placeholder: 'Enter value in J',
            }),
            enabledFieldName: 'energyOtherEnabled',
            valueFieldName: 'energyOther',
        }),
    ]),
});

export const MONTHS = Object.freeze([
    Object.freeze({ value: 1, label: 'January' }),
    Object.freeze({ value: 2, label: 'February' }),
    Object.freeze({ value: 3, label: 'March' }),
    Object.freeze({ value: 4, label: 'April' }),
    Object.freeze({ value: 5, label: 'May' }),
    Object.freeze({ value: 6, label: 'June' }),
    Object.freeze({ value: 7, label: 'July' }),
    Object.freeze({ value: 8, label: 'August' }),
    Object.freeze({ value: 9, label: 'September' }),
    Object.freeze({ value: 10, label: 'October' }),
    Object.freeze({ value: 11, label: 'November' }),
    Object.freeze({ value: 12, label: 'December' }),
]);

// Generate dynamic year options from 1000 to current year.
export const generateYearOptions = () => {
    const currentYear = new Date().getFullYear();
    const minYear = 1500;
    const years = [];

    // Generate years in descending order (current year first).
    for (let year = currentYear; year >= minYear; year -= 1) {
        years.push(Object.freeze({ value: year, label: year.toString() }));
    }

    return Object.freeze(years);
};
