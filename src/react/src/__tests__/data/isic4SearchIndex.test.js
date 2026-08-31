import {
    buildIsic4SearchIndex,
    getIsic4VisibleRows,
} from '../../data/isic4SearchIndex';

const TAXONOMY = Object.freeze({
    sections: [
        {
            code: 'A',
            label: 'Agriculture, forestry and fishing',
            displayLabel: 'A - Agriculture, forestry and fishing',
            kind: 'section',
            divisions: [
                {
                    code: '01',
                    label:
                        'Crop and animal production, hunting and related service activities',
                    displayLabel:
                        '01 - Crop and animal production, hunting and related service activities',
                    kind: 'division',
                    groups: [
                        {
                            code: '011',
                            label: 'Growing of non-perennial crops',
                            displayLabel:
                                '011 - Growing of non-perennial crops',
                            kind: 'group',
                            classes: [
                                {
                                    code: '0111',
                                    label: 'Growing of cereals',
                                    displayLabel:
                                        '0111 - Growing of cereals',
                                    kind: 'class',
                                },
                            ],
                        },
                    ],
                },
            ],
        },
        {
            code: 'C',
            label: 'Manufacturing',
            displayLabel: 'C - Manufacturing',
            kind: 'section',
            divisions: [
                {
                    code: '14',
                    label: 'Manufacture of wearing apparel',
                    displayLabel: '14 - Manufacture of wearing apparel',
                    kind: 'division',
                    groups: [],
                },
                {
                    code: '18',
                    label: 'Printing and related activities',
                    displayLabel: '18 - Printing and related activities',
                    kind: 'division',
                    groups: [],
                },
            ],
        },
        {
            code: 'J',
            label: 'Information and communication',
            displayLabel: 'J - Information and communication',
            kind: 'section',
            divisions: [
                {
                    code: '62',
                    label:
                        'Computer programming, consultancy and related activities',
                    displayLabel:
                        '62 - Computer programming, consultancy and related activities',
                    kind: 'division',
                    groups: [],
                },
            ],
        },
    ],
});

const COUNTS = Object.freeze({
    'section:A': 1,
    'section:C': 3,
    'section:J': 2,
    'division:01': 1,
    'division:14': 2,
    'division:18': 0,
    'division:62': 2,
});

const displayLabels = rows => rows.map(row => row.node.displayLabel);

describe('getIsic4VisibleRows', () => {
    const { flatNodes } = buildIsic4SearchIndex(TAXONOMY);

    test('ranks type-ahead matches by location count', () => {
        const { rows } = getIsic4VisibleRows(flatNodes, 'activities', COUNTS);
        const sectionLabels = displayLabels(rows).filter(label =>
            ['A - ', 'C - ', 'J - '].some(prefix => label.startsWith(prefix)),
        );

        expect(sectionLabels).toEqual([
            'C - Manufacturing',
            'J - Information and communication',
            'A - Agriculture, forestry and fishing',
        ]);
    });

    test('ranks siblings under a matching parent by location count', () => {
        const { rows } = getIsic4VisibleRows(
            flatNodes,
            'manufactur',
            COUNTS,
        );
        const labels = displayLabels(rows);

        expect(labels).toEqual([
            'C - Manufacturing',
            '14 - Manufacture of wearing apparel',
            '18 - Printing and related activities',
        ]);
    });

    test('keeps official taxonomy order when counts are not loaded', () => {
        const { rows } = getIsic4VisibleRows(flatNodes, 'i');
        const labels = displayLabels(rows);

        expect(labels.indexOf('A - Agriculture, forestry and fishing')).toBeLessThan(
            labels.indexOf('C - Manufacturing'),
        );
        expect(labels.indexOf('C - Manufacturing')).toBeLessThan(
            labels.indexOf('J - Information and communication'),
        );
    });

    test('keeps official taxonomy order for an empty query', () => {
        const { rows } = getIsic4VisibleRows(flatNodes, '', COUNTS);

        expect(displayLabels(rows)).toEqual([
            'A - Agriculture, forestry and fishing',
            'C - Manufacturing',
            'J - Information and communication',
        ]);
    });
});
