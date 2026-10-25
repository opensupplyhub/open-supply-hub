import React from 'react';
import { fireEvent, render, screen, within } from '@testing-library/react';

import { IsicSearch } from '../../components/Filters/IsicSearch/IsicSearch';
import {
    searchEntries,
    selectedEntries,
    withEntry,
} from '../../components/Filters/IsicSearch/utils';

const TEXTILES = Object.freeze({
    id: '4:13',
    title: 'Manufacture of textiles',
    level: 'division',
    codes: { 4: '13', 5: '13' },
    trail: 'Manufacturing',
});
const WEARING_APPAREL = Object.freeze({
    id: '4:14',
    title: 'Manufacture of wearing apparel',
    level: 'division',
    codes: { 4: '14', 5: '14' },
    trail: 'Manufacturing',
});
const COMPUTING = Object.freeze({
    id: '5:631',
    title: 'Computing infrastructure, data processing, hosting and related activities',
    level: 'group',
    codes: { 5: '631' },
    trail: 'Telecommunications and information services',
});
const ENTRIES = [TEXTILES, WEARING_APPAREL, COMPUTING];

const renderSearch = props => {
    const onChange = jest.fn();
    const onLoad = jest.fn();
    const utils = render(
        <IsicSearch
            entries={ENTRIES}
            fetching={false}
            counts={{ '4:13': 1240 }}
            isic4={[]}
            isic5={[]}
            onLoad={onLoad}
            onChange={onChange}
            classes={{}}
            {...props}
        />,
    );
    const input = screen.getByRole('combobox');
    const type = text => {
        fireEvent.focus(input);
        fireEvent.change(input, { target: { value: text } });
    };
    return { ...utils, input, type, onChange, onLoad };
};

describe('IsicSearch', () => {
    test('is labelled Industry Classification and loads on focus', () => {
        const { input, onLoad } = renderSearch();

        expect(screen.getByText('Industry Classification')).toBeTruthy();
        fireEvent.focus(input);
        expect(onLoad).toHaveBeenCalled();
    });

    test('suggests titles with revision tags, level, trail and count, never codes', () => {
        const { type } = renderSearch();

        type('textiles');
        const option = screen.getByRole('option');

        expect(option.textContent).toContain('Manufacture of textiles');
        expect(within(option).getByText('ISIC 4')).toBeTruthy();
        expect(within(option).getByText('ISIC 5')).toBeTruthy();
        expect(option.textContent).toContain('Division · in Manufacturing');
        expect(option.textContent).toContain('1,240');
        expect(option.textContent).not.toMatch(/\b13\b/);
    });

    test('a title only one revision has carries one tag', () => {
        const { type } = renderSearch();

        type('computing');
        const option = screen.getByRole('option');

        expect(within(option).getByText('ISIC 5')).toBeTruthy();
        expect(within(option).queryByText('ISIC 4')).toBeNull();
    });

    test('picking a category filters on its code in each revision', () => {
        const { type, onChange } = renderSearch();

        type('textiles');
        fireEvent.click(screen.getByRole('option'));

        expect(onChange).toHaveBeenCalledWith({
            4: [{ value: 'division:13', label: 'Manufacture of textiles' }],
            5: [{ value: 'division:13', label: 'Manufacture of textiles' }],
        });
    });

    test('a picked category shows by title and can be removed', () => {
        const picked = [
            { value: 'division:13', label: 'Manufacture of textiles' },
        ];
        const { onChange, container } = renderSearch({
            isic4: picked,
            isic5: picked,
        });

        expect(container.textContent).toContain('Manufacture of textiles');
        fireEvent.click(screen.getByRole('button'));
        expect(onChange).toHaveBeenCalledWith({ 4: [], 5: [] });
    });

    test('says when nothing matches', () => {
        const { type } = renderSearch();

        type('zzzz');

        expect(screen.getByRole('listbox').textContent).toContain(
            'No ISIC category matches',
        );
    });
});

describe('IsicSearch utils', () => {
    test('ranks matching titles by score, then level, then title, and skips picked ones', () => {
        expect(
            searchEntries(ENTRIES, 'manufacture', new Set()).map(e => e.id),
        ).toEqual(['4:13', '4:14']);
        expect(
            searchEntries(ENTRIES, 'manufacture', new Set(['4:13'])).map(
                e => e.id,
            ),
        ).toEqual(['4:14']);
        expect(searchEntries(ENTRIES, '  ', new Set())).toEqual([]);
    });

    test('reads picked entries back from either revision', () => {
        expect(
            selectedEntries(ENTRIES, {
                4: [],
                5: [{ value: 'group:631' }],
            }),
        ).toEqual([COMPUTING]);
    });

    test('adds and removes an entry only in revisions it exists in', () => {
        const added = withEntry({ 4: [], 5: [] }, COMPUTING, true);
        expect(added).toEqual({
            4: [],
            5: [{ value: 'group:631', label: COMPUTING.title }],
        });
        expect(withEntry(added, COMPUTING, false)).toEqual({ 4: [], 5: [] });
    });
});
