import { slcValidationSchema } from '../../util/util';
import { SLC_FORM_CONSTRAINTS } from '../../util/constants';

// Minimal valid base values — only name, address, and country are required.
// Optional string fields use undefined so Yup skips their tests (empty string
// fails the meaningful-characters check for non-required text fields, and
// fails the format-and-range check for numberOfWorkers).
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

// Helper: build an array of N valid { label, value } items.
const makeItems = count =>
    Array.from({ length: count }, (_, i) => ({
        label: `Item ${i + 1}`,
        value: `item-${i + 1}`,
    }));

// Helper: build a single { label, value } item whose label is N characters.
const makeItemOfLength = length => {
    const label = 'A'.repeat(length);
    return { label, value: label };
};

describe('slcValidationSchema', () => {
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

    describe('address field', () => {
        it('accepts a standard Latin address', async () => {
            await expect(
                isValid({ address: '10 Downing Street, London' }),
            ).resolves.toBe(true);
        });

        it('accepts accented Latin characters in address', async () => {
            await expect(
                isValid({ address: "12 Rue de l'Église, Montréal" }),
            ).resolves.toBe(true);
        });

        it('accepts an address of exactly 200 characters', async () => {
            await expect(
                isValid({ address: 'A'.repeat(200) }),
            ).resolves.toBe(true);
        });

        it('rejects an address exceeding 200 characters', async () => {
            await expect(
                validate({ address: 'A'.repeat(201) }),
            ).rejects.toThrow('cannot exceed 200 characters');
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

    describe('numberOfWorkers field', () => {
        it('accepts an empty optional field (real initial value)', async () => {
            await expect(isValid({ parentCompany: '', numberOfWorkers: '' })).resolves.toBe(
                true
            );
        });

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
            ).rejects.toThrow('Enter a single positive number');
        });

        it('rejects Arabic-Indic digits', async () => {
            await expect(
                validate({ numberOfWorkers: '١٠٠' }),
            ).rejects.toThrow('Enter a single positive number');
        });
    });

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

        it(`accepts exactly ${SLC_FORM_CONSTRAINTS.MAX_PRODUCT_TYPE_COUNT} items`, async () => {
            await expect(
                isValid({
                    productType: makeItems(
                        SLC_FORM_CONSTRAINTS.MAX_PRODUCT_TYPE_COUNT,
                    ),
                }),
            ).resolves.toBe(true);
        });

        it(`rejects more than ${SLC_FORM_CONSTRAINTS.MAX_PRODUCT_TYPE_COUNT} items`, async () => {
            await expect(
                validate({
                    productType: makeItems(
                        SLC_FORM_CONSTRAINTS.MAX_PRODUCT_TYPE_COUNT + 1,
                    ),
                }),
            ).rejects.toThrow('product types allowed');
        });

        it('rejects an item with a Chinese label', async () => {
            await expect(
                validate({
                    productType: [{ label: '衬衫', value: '衬衫' }],
                }),
            ).rejects.toThrow('Product type(s) must contain only Latin characters');
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

        it(`accepts an item of exactly ${SLC_FORM_CONSTRAINTS.MAX_STRING_LENGTH} characters`, async () => {
            await expect(
                isValid({
                    productType: [
                        makeItemOfLength(
                            SLC_FORM_CONSTRAINTS.MAX_STRING_LENGTH,
                        ),
                    ],
                }),
            ).resolves.toBe(true);
        });

        it(`rejects when only one item exceeds ${SLC_FORM_CONSTRAINTS.MAX_STRING_LENGTH} characters`, async () => {
            await expect(
                validate({
                    productType: [
                        { label: 'Shirts', value: 'Shirts' },
                        makeItemOfLength(
                            SLC_FORM_CONSTRAINTS.MAX_STRING_LENGTH + 1,
                        ),
                    ],
                }),
            ).rejects.toThrow(
                `Each value in Product type(s) cannot exceed ${SLC_FORM_CONSTRAINTS.MAX_STRING_LENGTH} characters`,
            );
        });
    });

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
            ).rejects.toThrow('Location type(s) must contain only Latin characters');
        });

        it(`accepts an item of exactly ${SLC_FORM_CONSTRAINTS.MAX_STRING_LENGTH} characters`, async () => {
            await expect(
                isValid({
                    locationType: [
                        makeItemOfLength(
                            SLC_FORM_CONSTRAINTS.MAX_STRING_LENGTH,
                        ),
                    ],
                }),
            ).resolves.toBe(true);
        });

        it(`rejects an item exceeding ${SLC_FORM_CONSTRAINTS.MAX_STRING_LENGTH} characters`, async () => {
            await expect(
                validate({
                    locationType: [
                        makeItemOfLength(
                            SLC_FORM_CONSTRAINTS.MAX_STRING_LENGTH + 1,
                        ),
                    ],
                }),
            ).rejects.toThrow(
                `Each value in Location type(s) cannot exceed ${SLC_FORM_CONSTRAINTS.MAX_STRING_LENGTH} characters`,
            );
        });
    });

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
            ).rejects.toThrow('Processing type(s) must contain only Latin characters');
        });

        it(`accepts an item of exactly ${SLC_FORM_CONSTRAINTS.MAX_STRING_LENGTH} characters`, async () => {
            await expect(
                isValid({
                    processingType: [
                        makeItemOfLength(
                            SLC_FORM_CONSTRAINTS.MAX_STRING_LENGTH,
                        ),
                    ],
                }),
            ).resolves.toBe(true);
        });

        it(`rejects an item exceeding ${SLC_FORM_CONSTRAINTS.MAX_STRING_LENGTH} characters`, async () => {
            await expect(
                validate({
                    processingType: [
                        makeItemOfLength(
                            SLC_FORM_CONSTRAINTS.MAX_STRING_LENGTH + 1,
                        ),
                    ],
                }),
            ).rejects.toThrow(
                `Each value in Processing type(s) cannot exceed ${SLC_FORM_CONSTRAINTS.MAX_STRING_LENGTH} characters`,
            );
        });
    });

    describe('dateOfSource field (data-center provenance, OSDEV-3074)', () => {
        it('accepts an empty value', async () => {
            await expect(isValid({ dateOfSource: '' })).resolves.toBe(true);
        });

        it('accepts ISO reduced-precision dates (YYYY, YYYY-MM, YYYY-MM-DD)', async () => {
            await expect(isValid({ dateOfSource: '2024' })).resolves.toBe(
                true,
            );
            await expect(isValid({ dateOfSource: '2024-06' })).resolves.toBe(
                true,
            );
            await expect(
                isValid({ dateOfSource: '2024-06-15' }),
            ).resolves.toBe(true);
        });

        it('rejects free-text and out-of-range dates', async () => {
            await expect(
                validate({ dateOfSource: 'June 2024' }),
            ).rejects.toThrow(
                'Date of source must be a date in YYYY, YYYY-MM, or YYYY-MM-DD format.',
            );
            await expect(
                validate({ dateOfSource: '2024-13' }),
            ).rejects.toThrow(
                'Date of source must be a date in YYYY, YYYY-MM, or YYYY-MM-DD format.',
            );
            await expect(
                validate({ dateOfSource: '15/06/2024' }),
            ).rejects.toThrow(
                'Date of source must be a date in YYYY, YYYY-MM, or YYYY-MM-DD format.',
            );
        });
    });
});
