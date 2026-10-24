import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';

import { IsicValuePicker } from '../../components/Filters/IsicSearch/IsicValuePicker';
import {
    EMPTY_ISIC,
    findByCode,
    isicFilterValues,
    isicObjects,
    isicOptions,
} from '../../components/Filters/IsicSearch/utils';
import { parseContribData } from '../../util/util';
import claimedFacilityDetailsReducer from '../../reducers/ClaimedFacilityDetailsReducer';
import { updateClaimedIsic } from '../../actions/claimedFacilityDetails';

const APPAREL = Object.freeze({
    id: '4:1410',
    title: 'Manufacture of wearing apparel, except fur apparel',
    level: 'class',
    codes: { 4: '1410' },
    trail: 'Manufacturing',
});
const TEXTILES = Object.freeze({
    id: '4:13',
    title: 'Manufacture of textiles',
    level: 'division',
    codes: { 4: '13', 5: '13' },
    trail: 'Manufacturing',
});
const COMPUTING = Object.freeze({
    id: '5:631',
    title: 'Computing infrastructure, data processing, hosting and related activities',
    level: 'group',
    codes: { 5: '631' },
    trail: 'Telecommunications and information services',
});
const ENTRIES = [APPAREL, TEXTILES, COMPUTING];

const APPAREL_OPTION = Object.freeze({
    value: 'class:1410',
    label: APPAREL.title,
});

const renderPicker = value => {
    const onChange = jest.fn();
    const onLoad = jest.fn();
    render(
        <IsicValuePicker
            entries={ENTRIES}
            value={value || EMPTY_ISIC}
            onLoad={onLoad}
            onChange={onChange}
            classes={{}}
        />,
    );
    const input = screen.getByRole('combobox');
    const type = text => {
        fireEvent.focus(input);
        fireEvent.change(input, { target: { value: text } });
    };
    return { input, type, onChange, onLoad };
};

describe('IsicValuePicker', () => {
    test('loads the taxonomy on focus and adds a category found by title', () => {
        const { input, type, onChange, onLoad } = renderPicker();

        fireEvent.focus(input);
        expect(onLoad).toHaveBeenCalled();
        type('apparel');
        fireEvent.click(screen.getByRole('option'));

        expect(onChange).toHaveBeenCalledWith({ 4: [APPAREL_OPTION], 5: [] });
    });

    test('finds a category by its code in the chosen revision only', () => {
        const { type, onChange } = renderPicker();

        type('631');
        expect(screen.queryByRole('option')).toBeNull();

        fireEvent.click(screen.getByRole('button', { name: 'ISIC 5' }));
        type('631');
        fireEvent.click(screen.getByRole('option'));

        expect(onChange).toHaveBeenCalledWith({
            4: [],
            5: [{ value: 'group:631', label: COMPUTING.title }],
        });
    });

    test('shows chips with revision and code, and removes one', () => {
        const { onChange } = renderPicker({ 4: [APPAREL_OPTION], 5: [] });

        expect(
            screen.getByText(`ISIC 4 · 1410 · ${APPAREL.title}`),
        ).toBeTruthy();
        fireEvent.click(screen.getByRole('button', { name: /remove/i }));

        expect(onChange).toHaveBeenCalledWith({ 4: [], 5: [] });
    });

    test('does not add a category twice', () => {
        const { type, onChange } = renderPicker({ 4: [APPAREL_OPTION], 5: [] });

        type('1410');
        fireEvent.click(screen.getByRole('option'));

        expect(onChange).not.toHaveBeenCalled();
    });
});

describe('ISIC form values', () => {
    test('finds an entry by exact code, case-insensitively', () => {
        expect(findByCode(ENTRIES, '4', ' 1410 ')).toBe(APPAREL);
        expect(findByCode(ENTRIES, '5', '1410')).toBeNull();
    });

    test('convert to what the claim API and the v1 API take', () => {
        const value = { 4: [APPAREL_OPTION], 5: [] };

        expect(isicFilterValues(value)).toEqual({
            isic_4: ['class:1410'],
            isic_5: [],
        });
        expect(isicObjects(value[4])).toEqual([
            { class: `1410 - ${APPAREL.title}` },
        ]);
    });

    test('read stored entries back by their most specific level', () => {
        const stored = [
            {
                section: 'C - Manufacturing',
                division: '14 - Manufacture of wearing apparel',
                group: '141 - Manufacture of wearing apparel, except fur apparel',
                class: `1410 - ${APPAREL.title}`,
            },
        ];

        expect(isicOptions(stored)).toEqual([APPAREL_OPTION]);
        expect(isicOptions(isicObjects([APPAREL_OPTION]))).toEqual([
            APPAREL_OPTION,
        ]);
        expect(isicOptions('')).toEqual([]);
        expect(isicOptions([{ class: 'not a code' }])).toEqual([]);
    });

    test('the single-location form sends only non-empty revisions', () => {
        const base = { name: 'Factory', country: { value: 'BD' } };

        expect(
            parseContribData({
                ...base,
                isic: { 4: [APPAREL_OPTION], 5: [] },
            }),
        ).toEqual({
            name: 'Factory',
            country: 'BD',
            isic_4: [{ class: `1410 - ${APPAREL.title}` }],
            source: 'SLC',
        });
        expect(parseContribData({ ...base, isic: EMPTY_ISIC })).not.toHaveProperty(
            'isic_4',
        );
    });

    test('the claimed-location editor stores edits in the shape it saves', () => {
        const loaded = {
            ...claimedFacilityDetailsReducer(undefined, { type: '@@INIT' }),
            data: { isic_4: '', isic_5: '' },
        };
        const state = claimedFacilityDetailsReducer(
            loaded,
            updateClaimedIsic({ 4: [], 5: [APPAREL_OPTION] }),
        );

        expect(state.data.isic_4).toEqual([]);
        expect(state.data.isic_5).toEqual([
            { class: `1410 - ${APPAREL.title}` },
        ]);
    });
});
