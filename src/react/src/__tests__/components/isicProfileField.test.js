import { render } from '@testing-library/react';

import getIsicDataPointProps, {
    describeMappedSource,
    stripIsicCode,
} from '../../components/ProductionLocation/ProductionLocationDetailsGeneralFields/isicField';
import {
    STATUS_CLAIMED,
    STATUS_CROWDSOURCED,
    STATUS_MAPPED,
} from '../../components/ProductionLocation/DataPoint/constants';

const APPAREL = {
    section: 'C - Manufacturing',
    division: '14 - Manufacture of wearing apparel',
    group: '141 - Manufacture of wearing apparel, except fur apparel',
    class: '1410 - Manufacture of wearing apparel, except fur apparel',
};
const APPAREL_TITLES = [
    'Manufacturing',
    'Manufacture of wearing apparel',
    'Manufacture of wearing apparel, except fur apparel',
    'Manufacture of wearing apparel, except fur apparel',
];

const submitted = (rawValue, overrides = {}) => ({
    value: { raw_value: rawValue },
    contributor_name: 'Contributor A',
    contributor_id: 7,
    created_at: '2026-01-02T00:00:00Z',
    is_from_claim: false,
    ...overrides,
});

const mapped = (processingType, titles) => ({
    facility_type: 'Final Product Assembly',
    processing_type: processingType,
    path: titles.map((title, i) => ({
        level: ['section', 'division', 'group', 'class'][i],
        title,
    })),
});

const props = ({ isic4 = [], isic4Mapped = [] } = {}) =>
    getIsicDataPointProps({
        properties: {
            extended_fields: { isic_4: isic4 },
            isic_4_mapped: isic4Mapped,
        },
    });

const text = node => render(node).getByTestId('isic-value-text').textContent;

describe('ISIC profile field', () => {
    test('strips codes from submitted values', () => {
        expect(stripIsicCode('C - Manufacturing')).toBe('Manufacturing');
        expect(stripIsicCode('1410 - Apparel')).toBe('Apparel');
        expect(stripIsicCode('Manufacturing')).toBe('Manufacturing');
        expect(stripIsicCode(undefined)).toBe('');
    });

    test('names the Location Type or Processing Type a value came from', () => {
        expect(describeMappedSource(mapped('Sewing', []))).toBe(
            'From Processing Type \u201DSewing\u201C',
        );
        expect(
            describeMappedSource({
                facility_type: 'Data Center',
                processing_type: '',
            }),
        ).toBe('From Location Type \u201DData Center\u201C');
        expect(
            describeMappedSource({
                facility_type: 'Office / HQ',
                processing_type: 'Office / HQ',
            }),
        ).toBe('From Location Type \u201DOffice / HQ\u201C');
    });

    test('no ISIC data, no field', () => {
        expect(props()).toBeNull();
        expect(getIsicDataPointProps(null)).toBeNull();
    });

    test('AC1/AC2: profile shows the most specific title and scheme, never a code', () => {
        const field = props({ isic4: [submitted([APPAREL])] });
        const { getByTestId, container } = render(field.value);

        expect(field.label).toBe(
            'International Standard Industrial Classification (ISIC)',
        );
        expect(getByTestId('isic-value-text')).toHaveTextContent(
            /^Manufacture of wearing apparel, except fur apparel$/,
        );
        expect(getByTestId('isic-scheme-tag')).toHaveTextContent('ISIC 4');
        expect(container).not.toHaveTextContent(/1410|C -/);
        expect(field.statusLabel).toBe(STATUS_CROWDSOURCED);
        expect(field.contributorName).toBe('Contributor A');
    });

    test('AC4: side panel shows the full path, a repeated title once', () => {
        const field = props({ isic4: [submitted([APPAREL])] });

        expect(text(field.drawerData.promotedContribution.value)).toBe(
            'Manufacturing › Manufacture of wearing apparel › Manufacture of wearing apparel, except fur apparel',
        );
    });

    test('AC3: keeps the level that was submitted', () => {
        const field = props({
            isic4: [submitted({ section: 'C - Manufacturing' })],
        });

        expect(text(field.value)).toBe('Manufacturing');
    });

    test('a single value still has a data source to open', () => {
        const field = props({ isic4: [submitted([APPAREL])] });

        expect(field.drawerData.promotedContribution).toBeTruthy();
        expect(field.drawerData.contributions).toEqual([]);
    });

    test('keeps the claimed status of a claimed value', () => {
        const field = props({
            isic4: [submitted([APPAREL], { is_from_claim: true })],
        });

        expect(field.statusLabel).toBe(STATUS_CLAIMED);
    });

    test('two organizations with the same value each get a card', () => {
        const field = props({
            isic4: [
                submitted([APPAREL]),
                submitted([APPAREL], { contributor_name: 'Contributor B' }),
            ],
        });

        expect(field.drawerData.contributions).toHaveLength(1);
        expect(field.drawerData.contributions[0].sourceName).toBe(
            'Contributor B',
        );
    });

    test('a contribution repeating a value or with an empty one adds no card', () => {
        const field = props({ isic4: [submitted([APPAREL, APPAREL, {}])] });

        expect(field.drawerData.contributions).toEqual([]);
    });

    test('AC5: a mapped value alone is shown, marked as mapped', () => {
        const field = props({
            isic4Mapped: [mapped('Sewing', ['Manufacturing'])],
        });

        expect(text(field.value)).toBe('Manufacturing');
        expect(field.statusLabel).toBe(STATUS_MAPPED);
        expect(field.contributorName).toBe('From Processing Type \u201DSewing\u201C');
        expect(field.userId).toBeUndefined();
        expect(field.date).toBeNull();
        expect(
            render(field.drawerData.promotedContribution.value).getByTestId(
                'isic-mapped-badge',
            ),
        ).toBeInTheDocument();
        expect(field.drawerData.promotedContribution.isMapped).toBe(true);
    });

    test('AC5: mapped values never come ahead of submitted ones', () => {
        const field = props({
            isic4: [submitted([APPAREL])],
            isic4Mapped: [mapped('Sewing', ['Manufacturing'])],
        });

        expect(field.statusLabel).toBe(STATUS_CROWDSOURCED);
        expect(
            render(field.value).queryByTestId('isic-mapped-badge'),
        ).not.toBeInTheDocument();
        const [card] = field.drawerData.contributions;
        expect(card.sourceName).toBe('From Processing Type \u201DSewing\u201C');
        expect(card.isMapped).toBe(true);
    });

    test('a mapped value repeating a submitted or mapped path adds no card', () => {
        const field = props({
            isic4: [submitted([APPAREL])],
            isic4Mapped: [
                mapped('Cut & Sew', APPAREL_TITLES),
                mapped('Sewing', ['Manufacturing']),
                mapped('Stitching', ['Manufacturing']),
            ],
        });

        expect(
            field.drawerData.contributions.map(card => card.sourceName),
        ).toEqual(['From Processing Type \u201DSewing\u201C']);
    });
});
