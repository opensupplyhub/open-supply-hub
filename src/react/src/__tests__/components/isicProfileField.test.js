import { render, within } from '@testing-library/react';

import getIndustryClassificationGroup, {
    describeMappedSource,
    stripIsicCode,
} from '../../components/ProductionLocation/ProductionLocationDetailsGeneralFields/isicField';
import {
    STATUS_CLAIMED,
    STATUS_CROWDSOURCED,
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

const group = ({ isic4 = [], isic4Mapped = [] } = {}) =>
    getIndustryClassificationGroup({
        properties: {
            extended_fields: { isic_4: isic4 },
            isic_4_mapped: isic4Mapped,
        },
    });
const field = (key, data) =>
    group(data)?.fields.find(item => item.key === key) ?? null;
const props = data => field('isic_4', data);
const mappedProps = data => field('isic_4_mapped', data);

const text = node => render(node).getByTestId('isic-value-text').textContent;

describe('Industry Classification section', () => {
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

    test('no ISIC data, no section', () => {
        expect(group()).toBeNull();
        expect(getIndustryClassificationGroup(null)).toBeNull();
    });

    test('one field per scheme, mapped values last', () => {
        const section = group({
            isic4: [submitted([APPAREL])],
            isic4Mapped: [mapped('Sewing', ['Manufacturing'])],
        });

        expect(section.label).toBe('Industry Classification');
        expect(section.fields.map(item => item.label)).toEqual([
            'ISIC Rev. 4',
            'Mapped from OS Hub (ISIC Rev. 4)',
        ]);
    });

    test('AC1/AC2: profile shows the most specific title, never a code', () => {
        const isic = props({ isic4: [submitted([APPAREL])] });
        const { getByTestId, container } = render(isic.value);

        expect(getByTestId('isic-value-text')).toHaveTextContent(
            /^Manufacture of wearing apparel, except fur apparel$/,
        );
        expect(container).not.toHaveTextContent(/1410|C -/);
        expect(isic.statusLabel).toBe(STATUS_CROWDSOURCED);
        expect(isic.contributorName).toBe('Contributor A');
    });

    test('AC4: side panel shows the full path, a repeated title once', () => {
        const isic = props({ isic4: [submitted([APPAREL])] });

        expect(text(isic.drawerData.promotedContribution.value)).toBe(
            'Manufacturing › Manufacture of wearing apparel › Manufacture of wearing apparel, except fur apparel',
        );
    });

    test('AC3: keeps the level that was submitted', () => {
        const isic = props({
            isic4: [submitted({ section: 'C - Manufacturing' })],
        });

        expect(text(isic.value)).toBe('Manufacturing');
    });

    test('a single value still has a data source to open', () => {
        const isic = props({ isic4: [submitted([APPAREL])] });

        expect(isic.drawerData.promotedContribution).toBeTruthy();
        expect(isic.drawerData.contributions).toEqual([]);
    });

    test('keeps the claimed status of a claimed value', () => {
        const isic = props({
            isic4: [submitted([APPAREL], { is_from_claim: true })],
        });

        expect(isic.statusLabel).toBe(STATUS_CLAIMED);
    });

    test('two organizations with the same value each get a card', () => {
        const isic = props({
            isic4: [
                submitted([APPAREL]),
                submitted([APPAREL], { contributor_name: 'Contributor B' }),
            ],
        });

        expect(isic.drawerData.contributions).toHaveLength(1);
        expect(isic.drawerData.contributions[0].sourceName).toBe(
            'Contributor B',
        );
    });

    test('a contribution repeating a value or with an empty one adds no card', () => {
        const isic = props({ isic4: [submitted([APPAREL, APPAREL, {}])] });

        expect(isic.drawerData.contributions).toEqual([]);
    });

    test('AC5: mapped values have their own field, never mixed with submitted ones', () => {
        const data = {
            isic4: [submitted([APPAREL])],
            isic4Mapped: [mapped('Sewing', ['Manufacturing'])],
        };

        expect(props(data).drawerData.contributions).toEqual([]);
        const isicMapped = mappedProps(data);
        expect(text(isicMapped.value)).toBe('Manufacturing');
        expect(
            within(render(isicMapped.value).container).getByTestId(
                'isic-mapped-source',
            ),
        ).toHaveTextContent('From Processing Type \u201DSewing\u201C');
        expect(isicMapped.statusLabel).toBeUndefined();
        expect(isicMapped.contributorName).toBeNull();
        expect(isicMapped.drawerFieldName).toBe('ISIC Rev. 4');
    });

    test('AC5: a mapped value alone is shown, marked as mapped in the side panel', () => {
        const isicMapped = mappedProps({
            isic4Mapped: [mapped('Sewing', ['Manufacturing'])],
        });

        expect(mappedProps({ isic4Mapped: [mapped('Sewing', [])] })).toBeNull();
        expect(
            render(isicMapped.drawerData.promotedContribution.value).getByTestId(
                'isic-mapped-badge',
            ),
        ).toBeInTheDocument();
        expect(isicMapped.drawerData.promotedContribution.isMapped).toBe(true);
    });

    test('a mapped value repeating a mapped path adds no card', () => {
        const isicMapped = mappedProps({
            isic4Mapped: [
                mapped('Sewing', ['Manufacturing']),
                mapped('Stitching', ['Manufacturing']),
                mapped('Cut & Sew', APPAREL_TITLES),
            ],
        });

        expect(
            isicMapped.drawerData.contributions.map(card => card.sourceName),
        ).toEqual(['From Processing Type \u201DCut & Sew\u201C']);
    });
});
