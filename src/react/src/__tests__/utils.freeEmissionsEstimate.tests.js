import freeEmissionsEstimateValidationSchema from '../components/FreeEmissionsEstimate/utils';

describe('freeEmissionsEstimateValidationSchema', () => {
    describe('Date validation', () => {
        describe('openingDate', () => {
            it('accepts a valid past date', async () => {
                const data = { openingDate: '2020-01-01' };
                await expect(
                    freeEmissionsEstimateValidationSchema.validate(data),
                ).resolves.toBeDefined();
            });

            it('accepts today\'s date', async () => {
                const today = new Date().toISOString().split('T')[0];
                const data = { openingDate: today };
                await expect(
                    freeEmissionsEstimateValidationSchema.validate(data),
                ).resolves.toBeDefined();
            });

            it('rejects a future date', async () => {
                const futureDate = new Date();
                futureDate.setFullYear(futureDate.getFullYear() + 1);
                const data = {
                    openingDate: futureDate.toISOString().split('T')[0],
                };
                await expect(
                    freeEmissionsEstimateValidationSchema.validate(data),
                ).rejects.toThrow('Please enter a valid date (not in the future).');
            });

            it('rejects an invalid date format', async () => {
                const data = { openingDate: 'invalid-date' };
                await expect(
                    freeEmissionsEstimateValidationSchema.validate(data),
                ).rejects.toThrow('Please enter a valid date (not in the future).');
            });

            it('accepts empty/null opening date', async () => {
                const data = { openingDate: '' };
                await expect(
                    freeEmissionsEstimateValidationSchema.validate(data),
                ).resolves.toBeDefined();
            });

            it('rejects opening date after closing date', async () => {
                const data = {
                    openingDate: '2023-12-31',
                    closingDate: '2020-01-01',
                };
                await expect(
                    freeEmissionsEstimateValidationSchema.validate(data),
                ).rejects.toThrow();
            });

            it('accepts opening date equal to closing date', async () => {
                const data = {
                    openingDate: '2020-01-01',
                    closingDate: '2020-01-01',
                };
                await expect(
                    freeEmissionsEstimateValidationSchema.validate(data),
                ).resolves.toBeDefined();
            });

            it('accepts opening date before closing date', async () => {
                const data = {
                    openingDate: '2020-01-01',
                    closingDate: '2023-12-31',
                };
                await expect(
                    freeEmissionsEstimateValidationSchema.validate(data),
                ).resolves.toBeDefined();
            });
        });

        describe('closingDate', () => {
            it('accepts a valid past date', async () => {
                const data = { closingDate: '2023-12-31' };
                await expect(
                    freeEmissionsEstimateValidationSchema.validate(data),
                ).resolves.toBeDefined();
            });

            it('accepts today\'s date', async () => {
                const today = new Date().toISOString().split('T')[0];
                const data = { closingDate: today };
                await expect(
                    freeEmissionsEstimateValidationSchema.validate(data),
                ).resolves.toBeDefined();
            });

            it('rejects a future date', async () => {
                const futureDate = new Date();
                futureDate.setFullYear(futureDate.getFullYear() + 1);
                const data = {
                    closingDate: futureDate.toISOString().split('T')[0],
                };
                await expect(
                    freeEmissionsEstimateValidationSchema.validate(data),
                ).rejects.toThrow('Please enter a valid date (not in the future).');
            });

            it('rejects an invalid date format', async () => {
                const data = { closingDate: 'not-a-date' };
                await expect(
                    freeEmissionsEstimateValidationSchema.validate(data),
                ).rejects.toThrow('Please enter a valid date (not in the future).');
            });

            it('accepts empty/null closing date', async () => {
                const data = { closingDate: '' };
                await expect(
                    freeEmissionsEstimateValidationSchema.validate(data),
                ).resolves.toBeDefined();
            });

            it('rejects closing date before opening date', async () => {
                const data = {
                    openingDate: '2023-12-31',
                    closingDate: '2020-01-01',
                };
                await expect(
                    freeEmissionsEstimateValidationSchema.validate(data),
                ).rejects.toThrow();
            });
        });

        describe('Date range validation', () => {
            it('skips validation when only opening date is provided', async () => {
                const data = { openingDate: '2020-01-01' };
                await expect(
                    freeEmissionsEstimateValidationSchema.validate(data),
                ).resolves.toBeDefined();
            });

            it('skips validation when only closing date is provided', async () => {
                const data = { closingDate: '2023-12-31' };
                await expect(
                    freeEmissionsEstimateValidationSchema.validate(data),
                ).resolves.toBeDefined();
            });

            it('validates date range when both dates are provided', async () => {
                const data = {
                    openingDate: '2020-01-01',
                    closingDate: '2019-12-31',
                };
                await expect(
                    freeEmissionsEstimateValidationSchema.validate(data),
                ).rejects.toThrow();
            });
        });
    });

    describe('Estimated annual throughput validation', () => {
        it('accepts a valid positive integer', async () => {
            const data = { estimatedAnnualThroughput: '100000' };
            await expect(
                freeEmissionsEstimateValidationSchema.validate(data),
            ).resolves.toBeDefined();
        });

        it('accepts empty value', async () => {
            const data = { estimatedAnnualThroughput: '' };
            await expect(
                freeEmissionsEstimateValidationSchema.validate(data),
            ).resolves.toBeDefined();
        });

        it('rejects zero', async () => {
            const data = { estimatedAnnualThroughput: '0' };
            await expect(
                freeEmissionsEstimateValidationSchema.validate(data),
            ).rejects.toThrow(
                `Please enter a positive integer that is less than or equal to ${Number.MAX_SAFE_INTEGER}.`,
            );
        });

        it('rejects negative numbers', async () => {
            const data = { estimatedAnnualThroughput: '-100' };
            await expect(
                freeEmissionsEstimateValidationSchema.validate(data),
            ).rejects.toThrow(
                `Please enter a positive integer that is less than or equal to ${Number.MAX_SAFE_INTEGER}.`,
            );
        });

        it('rejects decimal numbers', async () => {
            const data = { estimatedAnnualThroughput: '100.5' };
            await expect(
                freeEmissionsEstimateValidationSchema.validate(data),
            ).rejects.toThrow(
                `Please enter a positive integer that is less than or equal to ${Number.MAX_SAFE_INTEGER}.`,
            );
        });

        it('rejects numbers with leading spaces', async () => {
            const data = { estimatedAnnualThroughput: ' 100' };
            await expect(
                freeEmissionsEstimateValidationSchema.validate(data),
            ).rejects.toThrow(
                'Remove spaces at start and end of the provided value.',
            );
        });

        it('rejects numbers with trailing spaces', async () => {
            const data = { estimatedAnnualThroughput: '100 ' };
            await expect(
                freeEmissionsEstimateValidationSchema.validate(data),
            ).rejects.toThrow(
                'Remove spaces at start and end of the provided value.',
            );
        });

        it('rejects non-numeric values', async () => {
            const data = { estimatedAnnualThroughput: 'not-a-number' };
            await expect(
                freeEmissionsEstimateValidationSchema.validate(data),
            ).rejects.toThrow(
                `Please enter a positive integer that is less than or equal to ${Number.MAX_SAFE_INTEGER}.`,
            );
        });

        it('rejects values exceeding MAX_SAFE_INTEGER', async () => {
            const data = {
                estimatedAnnualThroughput: (
                    Number.MAX_SAFE_INTEGER + 1
                ).toString(),
            };
            await expect(
                freeEmissionsEstimateValidationSchema.validate(data),
            ).rejects.toThrow(
                `Please enter a positive integer that is less than or equal to ${Number.MAX_SAFE_INTEGER}.`,
            );
        });

        it('accepts MAX_SAFE_INTEGER', async () => {
            const data = {
                estimatedAnnualThroughput: Number.MAX_SAFE_INTEGER.toString(),
            };
            await expect(
                freeEmissionsEstimateValidationSchema.validate(data),
            ).resolves.toBeDefined();
        });
    });

    describe('Energy field validation', () => {
        const energyFields = [
            { field: 'energyCoal', enabledField: 'energyCoalEnabled' },
            {
                field: 'energyNaturalGas',
                enabledField: 'energyNaturalGasEnabled',
            },
            { field: 'energyDiesel', enabledField: 'energyDieselEnabled' },
            { field: 'energyKerosene', enabledField: 'energyKeroseneEnabled' },
            { field: 'energyBiomass', enabledField: 'energyBiomassEnabled' },
            { field: 'energyCharcoal', enabledField: 'energyCharcoalEnabled' },
            {
                field: 'energyAnimalWaste',
                enabledField: 'energyAnimalWasteEnabled',
            },
            {
                field: 'energyElectricity',
                enabledField: 'energyElectricityEnabled',
            },
            { field: 'energyOther', enabledField: 'energyOtherEnabled' },
        ];

        describe.each(energyFields)('$field', ({ field, enabledField }) => {
            it('accepts valid value when enabled', async () => {
                const data = {
                    [enabledField]: true,
                    [field]: '50000',
                };
                await expect(
                    freeEmissionsEstimateValidationSchema.validate(data),
                ).resolves.toBeDefined();
            });

            it('requires value when enabled', async () => {
                const data = {
                    [enabledField]: true,
                    [field]: '',
                };
                await expect(
                    freeEmissionsEstimateValidationSchema.validate(data),
                ).rejects.toThrow(
                    'Once the checkbox is checked, you must enter a value.',
                );
            });

            it('allows empty value when not enabled', async () => {
                const data = {
                    [enabledField]: false,
                    [field]: '',
                };
                await expect(
                    freeEmissionsEstimateValidationSchema.validate(data),
                ).resolves.toBeDefined();
            });

            it('rejects zero when enabled', async () => {
                const data = {
                    [enabledField]: true,
                    [field]: '0',
                };
                await expect(
                    freeEmissionsEstimateValidationSchema.validate(data),
                ).rejects.toThrow(
                    `Please enter a positive integer that is less than or equal to ${Number.MAX_SAFE_INTEGER}.`,
                );
            });

            it('rejects negative number when enabled', async () => {
                const data = {
                    [enabledField]: true,
                    [field]: '-100',
                };
                await expect(
                    freeEmissionsEstimateValidationSchema.validate(data),
                ).rejects.toThrow(
                    `Please enter a positive integer that is less than or equal to ${Number.MAX_SAFE_INTEGER}.`,
                );
            });

            it('rejects decimal number when enabled', async () => {
                const data = {
                    [enabledField]: true,
                    [field]: '100.5',
                };
                await expect(
                    freeEmissionsEstimateValidationSchema.validate(data),
                ).rejects.toThrow(
                    `Please enter a positive integer that is less than or equal to ${Number.MAX_SAFE_INTEGER}.`,
                );
            });

            it('rejects value with leading spaces when enabled', async () => {
                const data = {
                    [enabledField]: true,
                    [field]: ' 100',
                };
                await expect(
                    freeEmissionsEstimateValidationSchema.validate(data),
                ).rejects.toThrow(
                    'Remove spaces at start and end of the provided value.',
                );
            });

            it('rejects value with trailing spaces when enabled', async () => {
                const data = {
                    [enabledField]: true,
                    [field]: '100 ',
                };
                await expect(
                    freeEmissionsEstimateValidationSchema.validate(data),
                ).rejects.toThrow(
                    'Remove spaces at start and end of the provided value.',
                );
            });

            it('rejects non-numeric value when enabled', async () => {
                const data = {
                    [enabledField]: true,
                    [field]: 'not-a-number',
                };
                await expect(
                    freeEmissionsEstimateValidationSchema.validate(data),
                ).rejects.toThrow(
                    `Please enter a positive integer that is less than or equal to ${Number.MAX_SAFE_INTEGER}.`,
                );
            });

            it('accepts MAX_SAFE_INTEGER when enabled', async () => {
                const data = {
                    [enabledField]: true,
                    [field]: Number.MAX_SAFE_INTEGER.toString(),
                };
                await expect(
                    freeEmissionsEstimateValidationSchema.validate(data),
                ).resolves.toBeDefined();
            });

            it('rejects value exceeding MAX_SAFE_INTEGER when enabled', async () => {
                const data = {
                    [enabledField]: true,
                    [field]: (Number.MAX_SAFE_INTEGER + 1).toString(),
                };
                await expect(
                    freeEmissionsEstimateValidationSchema.validate(data),
                ).rejects.toThrow(
                    `Please enter a positive integer that is less than or equal to ${Number.MAX_SAFE_INTEGER}.`,
                );
            });
        });
    });

    describe('Complete form validation', () => {
        it('validates a complete valid form', async () => {
            const data = {
                openingDate: '2020-01-01',
                closingDate: '2023-12-31',
                estimatedAnnualThroughput: '100000',
                energyCoalEnabled: true,
                energyCoal: '50000',
                energyNaturalGasEnabled: true,
                energyNaturalGas: '30000',
                energyDieselEnabled: false,
                energyDiesel: '',
                energyKeroseneEnabled: false,
                energyKerosene: '',
                energyBiomassEnabled: false,
                energyBiomass: '',
                energyCharcoalEnabled: false,
                energyCharcoal: '',
                energyAnimalWasteEnabled: false,
                energyAnimalWaste: '',
                energyElectricityEnabled: true,
                energyElectricity: '1000000',
                energyOtherEnabled: false,
                energyOther: '',
            };
            await expect(
                freeEmissionsEstimateValidationSchema.validate(data),
            ).resolves.toBeDefined();
        });

        it('validates a minimal valid form', async () => {
            const data = {
                openingDate: '',
                closingDate: '',
                estimatedAnnualThroughput: '',
                energyCoalEnabled: false,
                energyNaturalGasEnabled: false,
                energyDieselEnabled: false,
                energyKeroseneEnabled: false,
                energyBiomassEnabled: false,
                energyCharcoalEnabled: false,
                energyAnimalWasteEnabled: false,
                energyElectricityEnabled: false,
                energyOtherEnabled: false,
            };
            await expect(
                freeEmissionsEstimateValidationSchema.validate(data),
            ).resolves.toBeDefined();
        });

        it('rejects form with multiple validation errors', async () => {
            const futureDate = new Date();
            futureDate.setFullYear(futureDate.getFullYear() + 1);

            const data = {
                openingDate: futureDate.toISOString().split('T')[0],
                closingDate: '2020-01-01',
                estimatedAnnualThroughput: '-100',
                energyCoalEnabled: true,
                energyCoal: '', // Missing required value.
                energyNaturalGasEnabled: true,
                energyNaturalGas: '0', // Invalid zero value.
            };

            await expect(
                freeEmissionsEstimateValidationSchema.validate(data),
            ).rejects.toThrow();
        });
    });
});

