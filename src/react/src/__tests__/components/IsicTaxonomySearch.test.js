import React from 'react';
import {
    fireEvent,
    screen,
    waitFor,
    within,
} from '@testing-library/react';

import IsicTaxonomySearch from '../../components/Filters/HierarchicalTaxonomySearch/IsicTaxonomySearch';
import renderWithProviders from '../../util/testUtils/renderWithProviders';

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
                    label: 'Crop and animal production',
                    displayLabel: '01 - Crop and animal production',
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
            divisions: [],
        },
    ],
});

const COUNTS = Object.freeze({
    'section:A': 1234,
    'division:01': 456,
    'group:011': 78,
    'class:0111': 9,
    'section:C': 321,
});

const createPreloadedState = () => ({
    filterOptions: {
        isic4Taxonomy: {
            config: {
                enabled: true,
                version: 1,
                taxonomyUrl: '/api/taxonomy/isic4/?v=1',
            },
            data: TAXONOMY,
            fetching: false,
            error: null,
        },
    },
});

const renderControl = (props = {}) => {
    const onIsic4Change = jest.fn();
    const onRequestCounts = jest.fn();
    const result = renderWithProviders(
        <IsicTaxonomySearch
            counts={COUNTS}
            isic4={[]}
            onIsic4Change={onIsic4Change}
            onRequestCounts={onRequestCounts}
            {...props}
        />,
        { preloadedState: createPreloadedState() },
    );

    return { ...result, onIsic4Change, onRequestCounts };
};

const getResultRow = label =>
    screen.getByRole('button', { name: label }).closest('li');

describe('IsicTaxonomySearch', () => {
    test('opens the required ISIC explanation on hover', async () => {
        renderControl();
        const infoButton = screen.getByRole('button', {
            name: 'What is ISIC?',
        });

        fireEvent.mouseEnter(infoButton);

        const tooltip = screen.getByRole('dialog', { name: 'What is ISIC?' });
        expect(infoButton).toHaveAttribute('aria-controls', tooltip.id);
        expect(
            within(tooltip).getByText('What is ISIC?'),
        ).toBeInTheDocument();
        expect(tooltip).toHaveTextContent(
            "The International Standard Industrial Classification (ISIC) is the United Nations' system",
        );
        expect(tooltip).toHaveTextContent(
            'C Manufacturing → 14 Manufacture of wearing apparel → 1410',
        );
        expect(within(tooltip).getByRole('link', { name: 'Learn more' }))
            .toHaveAttribute(
                'href',
                'https://unstats.un.org/unsd/classifications/Econ/isic',
            );

        fireEvent.mouseLeave(infoButton);
        fireEvent.mouseEnter(tooltip);
        await new Promise(resolve => setTimeout(resolve, 150));
        expect(tooltip).toBeInTheDocument();

        fireEvent.mouseLeave(tooltip);

        await waitFor(() => {
            expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
        });
    });

    test('browses, counts, and selects every hierarchy level', () => {
        const { onIsic4Change, onRequestCounts } = renderControl();
        const input = screen.getByRole('combobox');

        fireEvent.focus(input);
        expect(onRequestCounts).toHaveBeenCalledTimes(1);
        expect(
            within(
                getResultRow('A - Agriculture, forestry and fishing'),
            ).getByText('1,234'),
        ).toBeInTheDocument();

        fireEvent.click(
            within(
                getResultRow('A - Agriculture, forestry and fishing'),
            ).getByRole('button', { name: 'Expand' }),
        );
        expect(
            within(
                getResultRow('01 - Crop and animal production'),
            ).getByText('456'),
        ).toBeInTheDocument();

        fireEvent.click(
            within(
                getResultRow('01 - Crop and animal production'),
            ).getByRole('button', { name: 'Expand' }),
        );
        expect(
            within(
                getResultRow('011 - Growing of non-perennial crops'),
            ).getByText('78'),
        ).toBeInTheDocument();

        fireEvent.click(
            within(
                getResultRow('011 - Growing of non-perennial crops'),
            ).getByRole('button', { name: 'Expand' }),
        );
        expect(
            within(getResultRow('0111 - Growing of cereals')).getByText('9'),
        ).toBeInTheDocument();

        [
            ['A - Agriculture, forestry and fishing', 'section:A'],
            ['01 - Crop and animal production', 'division:01'],
            ['011 - Growing of non-perennial crops', 'group:011'],
            ['0111 - Growing of cereals', 'class:0111'],
        ].forEach(([label, value]) => {
            fireEvent.click(screen.getByRole('button', { name: label }));
            expect(onIsic4Change).toHaveBeenLastCalledWith([
                { label, value },
            ]);
        });
    });

    test('finds descendant text and visibly reports no matches', () => {
        renderControl();
        const input = screen.getByRole('combobox');

        fireEvent.change(input, { target: { value: 'cereals' } });

        expect(
            screen.getByRole('button', {
                name: 'A - Agriculture, forestry and fishing',
            }),
        ).toBeInTheDocument();
        expect(
            screen.getByRole('button', { name: '0111 - Growing of cereals' }),
        ).toBeInTheDocument();
        expect(screen.getByText('1 matching ISIC category')).toBeInTheDocument();

        fireEvent.change(input, { target: { value: 'dressing' } });

        expect(
            screen.getAllByText('No matching ISIC categories'),
        ).toHaveLength(2);
        expect(screen.queryAllByRole('option')).toHaveLength(0);
    });

    test('removes selected chips', () => {
        const selected = [
            {
                value: 'section:A',
                label: 'A - Agriculture, forestry and fishing',
            },
        ];
        const { onIsic4Change } = renderControl({ isic4: selected });

        fireEvent.click(
            screen.getByRole('button', {
                name: 'Remove A - Agriculture, forestry and fishing',
            }),
        );
        expect(onIsic4Change).toHaveBeenLastCalledWith([]);
    });

    test('supports keyboard selection', () => {
        const { onIsic4Change } = renderControl();
        const input = screen.getByRole('combobox');

        fireEvent.change(input, { target: { value: 'cereals' } });
        for (let index = 0; index < 4; index += 1) {
            fireEvent.keyDown(input, { key: 'ArrowDown' });
        }
        fireEvent.keyDown(input, { key: 'Enter' });

        expect(onIsic4Change).toHaveBeenLastCalledWith([
            {
                value: 'class:0111',
                label: '0111 - Growing of cereals',
            },
        ]);
    });
});
