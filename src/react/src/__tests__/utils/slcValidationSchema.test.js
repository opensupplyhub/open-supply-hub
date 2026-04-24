import { slcValidationSchema } from '../../util/util';

// Minimal valid base values — only name, address, and country are required.
// Optional string fields use undefined so Yup skips their tests (empty string
// fails the meaningful-characters check for non-required slcTextFieldValidation
// fields, and fails the format-and-range check for numberOfWorkers).
const validBase = {
    name: 'Test Facility',
    address: '123 Main Street',
    country: { value: 'US', label: 'United States' },
    sector: [],
    productType: [],
    locationType: [],
    processingType: [],
    numberOfWorkers: undefined,
    parentCompany: undefined,
};

// Helper: validate a partial override against the full schema.
const validate = (overrides = {}) =>
    slcValidationSchema.validate(
        { ...validBase, ...overrides },
        { abortEarly: true },
    );

const isValid = (overrides = {}) =>
    slcValidationSchema.isValid({ ...validBase, ...overrides });

describe('slcValidationSchema — non-Latin character validation', () => {
    // -------------------------------------------------------------------------
    // name
    // -------------------------------------------------------------------------
    describe('name field', () => {
        it('accepts plain ASCII text', async () => {
            await expect(isValid({ name: 'Acme Factory' })).resolves.toBe(true);
        });

        it('accepts accented Latin characters (é, ü, ñ, ø)', async () => {
            await expect(
                isValid({ name: 'Ärger über niño café' }),
            ).resolves.toBe(true);
        });

        it('rejects Chinese characters', async () => {
            await expect(
                validate({ name: '工厂名称' }),
            ).rejects.toThrow('must contain only Latin characters');
        });

        it('rejects Cyrillic characters', async () => {
            await expect(
                validate({ name: 'Фабрика' }),
            ).rejects.toThrow('must contain only Latin characters');
        });

        it('rejects Arabic characters', async () => {
            await expect(
                validate({ name: 'مصنع' }),
            ).rejects.toThrow('must contain only Latin characters');
        });

        it('rejects a mixed Latin and non-Latin string', async () => {
            await expect(
                validate({ name: 'Acme 工厂' }),
            ).rejects.toThrow('must contain only Latin characters');
        });
    });

    // -------------------------------------------------------------------------
    // address
    // -------------------------------------------------------------------------
    describe('address field', () => {
        it('accepts a standard Latin address', async () => {
            await expect(
                isValid({ address: '10 Downing Street, London' }),
            ).resolves.toBe(true);
        });

        it('accepts accented Latin characters in address', async () => {
            await expect(
                isValid({ address: '12 Rue de l\'Église, Montréal' }),
            ).resolves.toBe(true);
        });

        it('rejects Chinese characters in address', async () => {
            await expect(
                validate({ address: '北京市朝阳区' }),
            ).rejects.toThrow('must contain only Latin characters');
        });

        it('rejects Arabic characters in address', async () => {
            await expect(
                validate({ address: 'شارع الملك فهد' }),
            ).rejects.toThrow('must contain only Latin characters');
        });
    });

    // -------------------------------------------------------------------------
    // parentCompany
    // -------------------------------------------------------------------------
    describe('parentCompany field', () => {
        it('accepts a Latin parent company name', async () => {
            await expect(
                isValid({ parentCompany: 'Global Holdings Ltd.' }),
            ).resolves.toBe(true);
        });

        it('accepts accented Latin characters in parent company', async () => {
            await expect(
                isValid({ parentCompany: 'Société Générale' }),
            ).resolves.toBe(true);
        });

        it('rejects Japanese characters in parent company', async () => {
            await expect(
                validate({ parentCompany: '株式会社' }),
            ).rejects.toThrow('must contain only Latin characters');
        });

        it('rejects Cyrillic characters in parent company', async () => {
            await expect(
                validate({ parentCompany: 'Компания' }),
            ).rejects.toThrow('must contain only Latin characters');
        });
    });

    // -------------------------------------------------------------------------
    // numberOfWorkers
    // -------------------------------------------------------------------------
    describe('numberOfWorkers field', () => {
        it('accepts standard ASCII digits', async () => {
            await expect(isValid({ numberOfWorkers: '500' })).resolves.toBe(
                true,
            );
        });

        it('accepts a valid range with ASCII digits', async () => {
            await expect(
                isValid({ numberOfWorkers: '100-500' }),
            ).resolves.toBe(true);
        });

        it('rejects fullwidth (Japanese) digits', async () => {
            await expect(
                validate({ numberOfWorkers: '１００' }),
            ).rejects.toThrow('Only Latin characters are accepted');
        });

        it('rejects Arabic-Indic digits', async () => {
            await expect(
                validate({ numberOfWorkers: '١٠٠' }),
            ).rejects.toThrow('Only Latin characters are accepted');
        });
    });

    // -------------------------------------------------------------------------
    // productType (array of { label, value } objects)
    // -------------------------------------------------------------------------
    describe('productType field', () => {
        it('accepts an empty array', async () => {
            await expect(isValid({ productType: [] })).resolves.toBe(true);
        });

        it('accepts items with Latin labels', async () => {
            await expect(
                isValid({
                    productType: [
                        { label: 'Shirts', value: 'Shirts' },
                        { label: 'Trousers', value: 'Trousers' },
                    ],
                }),
            ).resolves.toBe(true);
        });

        it('rejects an item with a Chinese label', async () => {
            await expect(
                validate({
                    productType: [{ label: '衬衫', value: '衬衫' }],
                }),
            ).rejects.toThrow('must contain only Latin characters');
        });

        it('rejects when only one item in the list is non-Latin', async () => {
            await expect(
                validate({
                    productType: [
                        { label: 'Shirts', value: 'Shirts' },
                        { label: 'Рубашки', value: 'Рубашки' },
                    ],
                }),
            ).rejects.toThrow('must contain only Latin characters');
        });
    });

    // -------------------------------------------------------------------------
    // locationType (array of { label, value } objects)
    // -------------------------------------------------------------------------
    describe('locationType field', () => {
        it('accepts an empty array', async () => {
            await expect(isValid({ locationType: [] })).resolves.toBe(true);
        });

        it('accepts items with Latin labels', async () => {
            await expect(
                isValid({
                    locationType: [
                        { label: 'Final Assembly', value: 'Final Assembly' },
                    ],
                }),
            ).resolves.toBe(true);
        });

        it('rejects an item with a non-Latin label', async () => {
            await expect(
                validate({
                    locationType: [{ label: '组装', value: '组装' }],
                }),
            ).rejects.toThrow('must contain only Latin characters');
        });
    });

    // -------------------------------------------------------------------------
    // processingType (array of { label, value } objects)
    // -------------------------------------------------------------------------
    describe('processingType field', () => {
        it('accepts an empty array', async () => {
            await expect(isValid({ processingType: [] })).resolves.toBe(true);
        });

        it('accepts items with Latin labels', async () => {
            await expect(
                isValid({
                    processingType: [
                        { label: 'Printing', value: 'Printing' },
                    ],
                }),
            ).resolves.toBe(true);
        });

        it('rejects an item with a non-Latin label', async () => {
            await expect(
                validate({
                    processingType: [{ label: 'طباعة', value: 'طباعة' }],
                }),
            ).rejects.toThrow('must contain only Latin characters');
        });
    });
});
