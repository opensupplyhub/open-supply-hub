import React from 'react';
import { fireEvent } from '@testing-library/react';

import HierarchicalTaxonomySearch from '../../components/Filters/HierarchicalTaxonomySearch';
import renderWithProviders from '../../util/testUtils/renderWithProviders';

jest.mock('../../components/SearchIcon', () => () => (
    <span data-testid="search-icon" />
));

const getRowSelectButtons = getAllByRole =>
    getAllByRole('button').filter(
        button =>
            !/(Expand|Collapse)/.test(button.getAttribute('aria-label') || ''),
    );

describe('HierarchicalTaxonomySearch component', () => {
    const defaultProps = {
        label: 'Facility type & processing type',
        placeholder: 'Search facility or processing types',
        counts: {
            'Raw Material Processing or Production': 42,
            'Material Creation': 7,
        },
        facilityType: [],
        processingType: [],
        onFacilityTypeChange: jest.fn(),
        onProcessingTypeChange: jest.fn(),
    };

    const renderComponent = (props = {}) =>
        renderWithProviders(
            <HierarchicalTaxonomySearch {...defaultProps} {...props} />,
        );

    beforeEach(() => {
        jest.clearAllMocks();
    });

    test('typing "material" shows parent and nested processing matches', () => {
        const { getAllByRole, getByRole } = renderComponent();

        fireEvent.focus(getByRole('combobox'));
        fireEvent.change(getByRole('combobox'), {
            target: { value: 'material' },
        });

        const options = getRowSelectButtons(getAllByRole);
        const optionText = options.map(option => option.textContent);

        expect(
            optionText.some(text =>
                /Raw Material Processing or Production/.test(text),
            ),
        ).toBe(true);
        expect(optionText.some(text => /Material Creation/.test(text))).toBe(
            true,
        );
        expect(optionText.some(text => /Material Production/.test(text))).toBe(
            true,
        );
    });

    test('removing a chip clears the selected processing type', () => {
        const onProcessingTypeChange = jest.fn();
        const { getByLabelText } = renderComponent({
            processingType: [{ value: 'Material Creation', label: 'Material Creation' }],
            onProcessingTypeChange,
        });

        fireEvent.click(getByLabelText('Remove Material Creation'));

        expect(onProcessingTypeChange).toHaveBeenCalledWith([]);
    });

    test('selecting an option clears the search input', () => {
        const { getAllByRole, getByRole } = renderComponent();

        fireEvent.focus(getByRole('combobox'));
        fireEvent.change(getByRole('combobox'), {
            target: { value: 'material' },
        });

        fireEvent.click(getRowSelectButtons(getAllByRole)[0]);

        expect(getByRole('combobox')).toHaveValue('');
    });

    test('deselecting a facility type chip clears its processing-type children', () => {
        const onFacilityTypeChange = jest.fn();
        const onProcessingTypeChange = jest.fn();
        const { getByLabelText } = renderComponent({
            facilityType: [
                {
                    value: 'Textile or Material Production',
                    label: 'Textile or Material Production',
                },
            ],
            processingType: [
                { value: 'Material Creation', label: 'Material Creation' },
                { value: 'Material Production', label: 'Material Production' },
            ],
            onFacilityTypeChange,
            onProcessingTypeChange,
        });

        fireEvent.click(
            getByLabelText('Remove Textile or Material Production'),
        );

        expect(onFacilityTypeChange).toHaveBeenCalledWith([]);
        expect(onProcessingTypeChange).toHaveBeenCalledWith([]);
    });
});
