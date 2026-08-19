import {
    filterRowsByExpandedState,
    getAncestorNodeIds,
    getExpandedNodeIdsForRows,
    getIsic4ParentNodeId,
    makeSelectOption,
    splitLabelForHighlight,
} from '../../components/Filters/HierarchicalTaxonomySearch/utils';

/*
The helpers left in HierarchicalTaxonomySearch/utils.js are the ones the ISIC
control shares, so the nodes here follow the shape isic4SearchIndex builds.
*/
const SECTION = Object.freeze({
    id: 'section:A',
    parentId: null,
    displayLabel: 'A - Agriculture',
});

const DIVISION = Object.freeze({
    id: 'division:01',
    parentId: SECTION.id,
    displayLabel: '01 - Crop and animal production',
});

const GROUP = Object.freeze({
    id: 'group:011',
    parentId: DIVISION.id,
    displayLabel: '011 - Growing of non-perennial crops',
});

const nodeById = new Map(
    [SECTION, DIVISION, GROUP].map(node => [node.id, node]),
);

const getNodeKey = node => node.id;

describe('shared taxonomy search utils', () => {
    test('makeSelectOption uses the value as its own label', () => {
        expect(makeSelectOption('Dyeing')).toEqual({
            value: 'Dyeing',
            label: 'Dyeing',
        });
    });

    describe('splitLabelForHighlight', () => {
        test('splits a label around a case-insensitive match', () => {
            expect(
                splitLabelForHighlight('Growing of crops', 'OF'),
            ).toEqual([
                { text: 'Growing ', highlighted: false },
                { text: 'of', highlighted: true },
                { text: ' crops', highlighted: false },
            ]);
        });

        test('drops the empty parts of a match at the start', () => {
            expect(splitLabelForHighlight('Dyeing', 'dye')).toEqual([
                { text: 'Dye', highlighted: true },
                { text: 'ing', highlighted: false },
            ]);
        });

        test('returns the whole label when there is nothing to highlight', () => {
            expect(splitLabelForHighlight('Dyeing', '')).toEqual([
                { text: 'Dyeing', highlighted: false },
            ]);
            expect(splitLabelForHighlight('Dyeing', 'knitting')).toEqual([
                { text: 'Dyeing', highlighted: false },
            ]);
        });
    });

    test('getAncestorNodeIds walks up to the root', () => {
        expect(
            getAncestorNodeIds(GROUP, getIsic4ParentNodeId, nodeById),
        ).toEqual([DIVISION.id, SECTION.id]);
        expect(
            getAncestorNodeIds(SECTION, getIsic4ParentNodeId, nodeById),
        ).toEqual([]);
    });

    test('getExpandedNodeIdsForRows expands matches and their ancestors', () => {
        const rows = [
            { node: DIVISION, depth: 1, isParent: true },
            { node: GROUP, depth: 2, isParent: false },
        ];

        expect(
            getExpandedNodeIdsForRows(
                rows,
                getNodeKey,
                getIsic4ParentNodeId,
                nodeById,
            ),
        ).toEqual(new Set([DIVISION.id, SECTION.id]));
    });

    describe('filterRowsByExpandedState', () => {
        const rows = Object.freeze([
            { node: SECTION, depth: 0 },
            { node: DIVISION, depth: 1 },
            { node: GROUP, depth: 2 },
        ]);

        test('hides the descendants of a collapsed node', () => {
            expect(
                filterRowsByExpandedState(
                    rows,
                    new Set([SECTION.id]),
                    getIsic4ParentNodeId,
                    nodeById,
                    false,
                ),
            ).toEqual([rows[0], rows[1]]);
        });

        test('keeps a row whose whole ancestry is expanded', () => {
            expect(
                filterRowsByExpandedState(
                    rows,
                    new Set([SECTION.id, DIVISION.id]),
                    getIsic4ParentNodeId,
                    nodeById,
                    false,
                ),
            ).toEqual(rows);
        });

        test('keeps every row while all rows are shown', () => {
            expect(
                filterRowsByExpandedState(
                    rows,
                    new Set(),
                    getIsic4ParentNodeId,
                    nodeById,
                    true,
                ),
            ).toBe(rows);
        });
    });
});
