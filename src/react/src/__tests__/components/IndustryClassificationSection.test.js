import React from 'react';
import { fireEvent, screen, within } from '@testing-library/react';

import renderWithProviders from '../../util/testUtils/renderWithProviders';
import IndustryClassificationSection from '../../components/ProductionLocation/IndustryClassificationSection/IndustryClassificationSection';
import getIndustryClassificationFields, {
    formatPath,
    parseIsicLevel,
} from '../../components/ProductionLocation/IndustryClassificationSection/utils';
import {
    STATUS_CLAIMED,
    STATUS_CROWDSOURCED,
} from '../../components/ProductionLocation/DataPoint/constants';

const KNITTED = {
    section: 'C - Manufacturing',
    division: '14 - Manufacture of wearing apparel',
    group: '143 - Manufacture of knitted and crocheted apparel',
    class: '1430 - Manufacture of knitted and crocheted apparel',
};

const submitted = (rawValue, overrides = {}) => ({
    value: { raw_value: rawValue },
    contributor_name: 'Contributor A',
    contributor_id: 7,
    created_at: '2026-01-02T00:00:00Z',
    is_from_claim: false,
    ...overrides,
});

const MAPPED_APPAREL = {
    facility_type: 'Final Product Assembly',
    processing_type: 'Cut & Sew',
    path: [
        { level: 'section', code: 'C', title: 'Manufacturing' },
        { level: 'division', code: '14', title: 'Manufacture of wearing apparel' },
    ],
};

const data = ({ isic4 = [], isic5 = [], mapped = [], types = [] } = {}) => ({
    properties: {
        extended_fields: { isic_4: isic4, isic_5: isic5, processing_type: types },
        isic_4_mapped: mapped,
    },
});

const fieldsByLabel = input =>
    Object.fromEntries(
        getIndustryClassificationFields(input).map(field => [field.label, field]),
    );

describe('Industry Classification fields', () => {
    test('read the code and title of each level', () => {
        expect(parseIsicLevel('1430 - Knitted apparel')).toEqual({
            code: '1430',
            title: 'Knitted apparel',
        });
        expect(parseIsicLevel('c - Manufacturing').code).toBe('C');
        expect(parseIsicLevel(undefined)).toBeNull();
    });

    test('the profile shows the code and title of the level reported, the panel the full path', () => {
        const isic4 = fieldsByLabel(data({ isic4: [submitted([KNITTED])] }))[
            'ISIC Rev. 4'
        ];

        expect(isic4.value).toBe(
            '1430 · Manufacture of knitted and crocheted apparel',
        );
        expect(isic4.drawerData.promotedContribution.value).toBe(
            'C · Manufacturing › 14 · Manufacture of wearing apparel › ' +
                '143 · Manufacture of knitted and crocheted apparel › ' +
                '1430 · Manufacture of knitted and crocheted apparel',
        );
        expect(isic4.statusLabel).toBe(STATUS_CROWDSOURCED);
        expect(isic4.contributorName).toBe('Contributor A');
    });

    test('a division-level value shows the division', () => {
        const isic4 = fieldsByLabel(
            data({
                isic4: [
                    submitted({
                        section: 'C - Manufacturing',
                        division: '14 - Manufacture of wearing apparel',
                    }),
                ],
            }),
        )['ISIC Rev. 4'];

        expect(isic4.value).toBe('14 · Manufacture of wearing apparel');
    });

    test('one field per revision, each only with data, values kept in their revision', () => {
        const malt = {
            section: 'C - Manufacturing',
            class: '1104 - Manufacture of malt',
        };

        expect(Object.keys(fieldsByLabel(data({ isic5: [submitted(malt)] })))).toEqual(
            ['ISIC Rev. 5'],
        );
        expect(getIndustryClassificationFields(data())).toEqual([]);
        expect(getIndustryClassificationFields(null)).toEqual([]);
    });

    test('Open Supply Hub is a contributor of ISIC 4 values, ranked after organizations', () => {
        const isic4 = fieldsByLabel(
            data({
                isic4: [submitted([KNITTED], { is_from_claim: true })],
                mapped: [MAPPED_APPAREL],
                types: [{ created_at: '2026-07-09T00:00:00Z' }],
            }),
        )['ISIC Rev. 4'];

        expect(isic4.statusLabel).toBe(STATUS_CLAIMED);
        const [osHub] = isic4.drawerData.contributions;
        expect(osHub).toEqual({
            value: 'C · Manufacturing › 14 · Manufacture of wearing apparel',
            sourceName: 'Open Supply Hub',
            date: '2026-07-09T00:00:00Z',
            userId: undefined,
            provenance: null,
        });
    });

    test('a location with only Open Supply Hub values shows them like any value', () => {
        const isic4 = fieldsByLabel(data({ mapped: [MAPPED_APPAREL, MAPPED_APPAREL] }))[
            'ISIC Rev. 4'
        ];

        expect(isic4.value).toBe('14 · Manufacture of wearing apparel');
        expect(isic4.contributorName).toBe('Open Supply Hub');
        expect(isic4.drawerData.contributions).toEqual([]);
    });

    test('a path joins codes and titles with ›', () => {
        expect(formatPath([{ code: 'C', title: 'Manufacturing' }])).toBe(
            'C · Manufacturing',
        );
    });
});

describe('IndustryClassificationSection', () => {
    const render = ({ isicSwitch = true, input = data({ mapped: [MAPPED_APPAREL] }) } = {}) =>
        renderWithProviders(<IndustryClassificationSection data={input} />, {
            preloadedState: {
                featureFlags: { flags: { enable_isic_taxonomy: isicSwitch } },
                sectionNavigation: { openSectionIds: {}, scrollTargetId: null },
            },
        });

    test('opens and closes like Operational Details', () => {
        render();
        const section = screen.getByTestId('industry-classification-section');

        expect(within(section).getByText('Industry Classification')).toBeTruthy();
        expect(within(section).getByText('Open')).toBeTruthy();
        fireEvent.click(within(section).getByText('Industry Classification'));
        expect(within(section).getByText('Close')).toBeTruthy();
        expect(within(section).getByText('ISIC Rev. 4')).toBeTruthy();
        expect(section.textContent).toContain(
            '14 · Manufacture of wearing apparel',
        );
        expect(section.textContent).toContain('Open Supply Hub');
        expect(section.textContent).not.toMatch(/Mapped from|From Processing Type/);
    });

    test('the side panel counts Open Supply Hub as an organization', () => {
        render();
        const section = screen.getByTestId('industry-classification-section');
        fireEvent.click(within(section).getByText('Industry Classification'));
        fireEvent.click(within(section).getByTestId('data-point-sources-button'));

        expect(
            screen.getByTestId('contributions-drawer-subtitle').textContent,
        ).toBe('1 organization has contributed data for ISIC Rev. 4');
    });

    test('is hidden while the ISIC switch is off', () => {
        render({ isicSwitch: false });
        expect(screen.queryByTestId('industry-classification-section')).toBeNull();
    });

    test('is hidden without ISIC data', () => {
        render({ input: data() });
        expect(screen.queryByTestId('industry-classification-section')).toBeNull();
    });
});
