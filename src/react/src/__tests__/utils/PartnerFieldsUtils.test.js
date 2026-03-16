import moment from 'moment';
import {
    getTitleFromSchema,
    getLinkTextFromSchema,
    getFormattedDateValue,
} from '../../components/PartnerFields/utils';

describe('getTitleFromSchema', () => {
    const schemaProperties = {
        name: { title: 'Full Name', type: 'string' },
        status: { type: 'string' },
    };

    it('returns the title when the property has one', () => {
        expect(getTitleFromSchema('name', schemaProperties)).toBe('Full Name');
    });

    it('returns null when the property has no title', () => {
        expect(getTitleFromSchema('status', schemaProperties)).toBeNull();
    });

    it('returns null when the property key does not exist', () => {
        expect(getTitleFromSchema('missing', schemaProperties)).toBeNull();
    });
});

describe('getLinkTextFromSchema', () => {
    it('returns the _text value when both schema and value define it', () => {
        const schemaProperties = {
            url: { type: 'string', format: 'uri' },
            url_text: { type: 'string' },
        };
        const value = {
            url: 'https://example.com',
            url_text: 'Example Site',
        };

        expect(getLinkTextFromSchema('url', value, schemaProperties)).toBe(
            'Example Site',
        );
    });

    it('falls back to the property value when _text is not in the schema', () => {
        const schemaProperties = {
            url: { type: 'string', format: 'uri' },
        };
        const value = { url: 'https://example.com' };

        expect(getLinkTextFromSchema('url', value, schemaProperties, value.url)).toBe(
            'https://example.com',
        );
    });

    it('falls back to the property value when _text is in the schema but not in the value', () => {
        const schemaProperties = {
            url: { type: 'string', format: 'uri' },
            url_text: { type: 'string' },
        };
        const value = { url: 'https://example.com' };

        expect(getLinkTextFromSchema('url', value, schemaProperties, value.url)).toBe(
            'https://example.com',
        );
    });

    it('falls back to the property value when schemaProperties is null', () => {
        const value = { url: 'https://example.com' };

        expect(getLinkTextFromSchema('url', value, null, value.url)).toBe(
            'https://example.com',
        );
    });

    it('returns schemaProperty.text when _text key is not in schema', () => {
        const schemaProperties = {
            url: { type: 'string', format: 'uri', text: 'Click here' },
        };
        const value = { url: 'https://example.com' };

        expect(
            getLinkTextFromSchema('url', value, schemaProperties, value.url),
        ).toBe('Click here');
    });
});

describe('getFormattedDateValue', () => {
    it('formats a date using the default "LL" format', () => {
        const value = { created_at: '2024-06-15' };
        const expected = moment('2024-06-15').format('LL');

        expect(getFormattedDateValue('created_at', value)).toBe(expected);
    });

    it('formats a date using a custom format', () => {
        const value = { created_at: '2024-06-15' };

        expect(getFormattedDateValue('created_at', value, 'YYYY-MM-DD')).toBe(
            '2024-06-15',
        );
    });

    it('returns an empty string when the property value is missing', () => {
        expect(getFormattedDateValue('created_at', {})).toBe('');
    });

    it('returns an empty string when the property value is null', () => {
        expect(getFormattedDateValue('created_at', { created_at: null })).toBe(
            '',
        );
    });
});
