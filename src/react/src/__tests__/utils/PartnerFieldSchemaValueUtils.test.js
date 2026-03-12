import React from 'react';
import {
    isValidValue,
    getSchemaProperties,
    renderProperties,
    shouldSkipProperty,
} from '../../components/PartnerFields/PartnerFieldSchemaValue/utils';

describe('isValidValue', () => {
    it('returns true for a plain object with a schema', () => {
        expect(isValidValue({ a: 1 }, { properties: {} })).toBe(true);
    });

    it('returns false when value is null', () => {
        expect(isValidValue(null, { properties: {} })).toBe(false);
    });

    it('returns false when jsonSchema is null', () => {
        expect(isValidValue({ a: 1 }, null)).toBe(false);
    });

    it('returns false for an array value', () => {
        expect(isValidValue([1, 2], { properties: {} })).toBe(false);
    });

    it('returns false for a string value', () => {
        expect(isValidValue('hello', { properties: {} })).toBe(false);
    });
});

describe('getSchemaProperties', () => {
    it('returns properties from the schema', () => {
        const schema = { properties: { name: { type: 'string' } } };
        expect(getSchemaProperties(schema)).toEqual({
            name: { type: 'string' },
        });
    });

    it('returns empty object when schema is null', () => {
        expect(getSchemaProperties(null)).toEqual({});
    });

    it('returns empty object when properties key is missing', () => {
        expect(getSchemaProperties({ type: 'object' })).toEqual({});
    });
});

describe('shouldSkipProperty', () => {
    it('returns true when propertyKey is not in schemaProperties', () => {
        expect(shouldSkipProperty('missing', { name: {} })).toBe(true);
    });

    it('returns false for a regular key present in schema', () => {
        expect(shouldSkipProperty('name', { name: { type: 'string' } })).toBe(
            false,
        );
    });

    it('returns true for _text key when base property has uri format', () => {
        const schema = {
            url: { type: 'string', format: 'uri' },
            url_text: { type: 'string' },
        };
        expect(shouldSkipProperty('url_text', schema)).toBe(true);
    });

    it('returns false for _text key when base property has non-uri format', () => {
        const schema = {
            label: { type: 'string', format: 'date' },
            label_text: { type: 'string' },
        };
        expect(shouldSkipProperty('label_text', schema)).toBe(false);
    });

    it('returns false for _text key when base property has no format', () => {
        const schema = {
            label: { type: 'string' },
            label_text: { type: 'string' },
        };
        expect(shouldSkipProperty('label_text', schema)).toBe(false);
    });

    it('returns false for _text key when base property does not exist', () => {
        const schema = { note_text: { type: 'string' } };
        expect(shouldSkipProperty('note_text', schema)).toBe(false);
    });
});

describe('renderProperties', () => {
    const schemaProperties = {
        name: { type: 'string', title: 'Name' },
        age: { type: 'integer', title: 'Age' },
    };

    it('renders a component for each matching property', () => {
        const value = { name: 'Alice', age: 30 };
        const result = renderProperties(value, schemaProperties, {});

        expect(result).toHaveLength(2);
        result.forEach(el => expect(React.isValidElement(el)).toBe(true));
    });

    it('skips properties not present in value', () => {
        const value = { name: 'Alice' };
        const result = renderProperties(value, schemaProperties, {});

        expect(result).toHaveLength(1);
    });

    it('returns empty array when value has no matching keys', () => {
        const result = renderProperties({ other: 'x' }, schemaProperties, {});
        expect(result).toEqual([]);
    });

    it('skips _text property when base property has uri format', () => {
        const schema = {
            url: { type: 'string', format: 'uri' },
            url_text: { type: 'string' },
        };
        const value = { url: 'https://example.com', url_text: 'Link' };
        const result = renderProperties(value, schema, {});

        expect(result).toHaveLength(1);
    });

    it('skips _text property when base property has url format', () => {
        const schema = {
            url: { type: 'string', format: 'url' },
            url_text: { type: 'string' },
        };
        const value = { url: 'https://example.com', url_text: 'Link' };
        const result = renderProperties(value, schema, {});
        expect(result).toHaveLength(1);
    });

    it('keeps _text property when base property is not uri', () => {
        const schema = {
            label: { type: 'string' },
            label_text: { type: 'string' },
        };
        const value = { label: 'foo', label_text: 'bar' };
        const result = renderProperties(value, schema, {});

        expect(result).toHaveLength(2);
    });
});
