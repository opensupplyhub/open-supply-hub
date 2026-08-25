import { resolveIsic4FilterLabels } from '../../components/Filters/HierarchicalTaxonomySearch/isicUtils';

const flatNodes = Object.freeze([
    Object.freeze({
        id: 'section:A',
        kind: 'section',
        code: 'A',
        label: 'Agriculture',
        displayLabel: 'A - Agriculture',
        depth: 0,
        parentId: null,
        countKey: 'section:A',
    }),
    Object.freeze({
        id: 'section:B',
        kind: 'section',
        code: 'B',
        label: 'Mining',
        displayLabel: 'B - Mining and quarrying',
        depth: 0,
        parentId: null,
        countKey: 'section:B',
    }),
]);

describe('resolveIsic4FilterLabels', () => {
    test('replaces URL-parsed labels with taxonomy display labels', () => {
        const isic4 = Object.freeze([
            { value: 'section:A', label: 'section:A' },
            { value: 'section:B', label: 'section:B' },
        ]);

        expect(resolveIsic4FilterLabels(isic4, flatNodes)).toEqual([
            { value: 'section:A', label: 'A - Agriculture' },
            { value: 'section:B', label: 'B - Mining and quarrying' },
        ]);
    });

    test('leaves selections unchanged when labels already match', () => {
        const isic4 = Object.freeze([
            { value: 'section:A', label: 'A - Agriculture' },
        ]);

        expect(resolveIsic4FilterLabels(isic4, flatNodes)).toBe(isic4);
    });

    test('keeps unknown values when they are not in the taxonomy', () => {
        const isic4 = Object.freeze([
            { value: 'section:Z', label: 'section:Z' },
        ]);

        expect(resolveIsic4FilterLabels(isic4, flatNodes)).toBe(isic4);
    });
});
