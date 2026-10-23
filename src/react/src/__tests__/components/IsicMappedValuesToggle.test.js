import React from 'react';
import { render, fireEvent } from '@testing-library/react';

import {
    IsicMappedValuesToggle,
    ISIC4_MAPPED_TOGGLE_LABEL,
} from '../../components/Filters/HierarchicalTaxonomySearch/IsicMappedValuesToggle';

const renderToggle = props => {
    const onToggle = jest.fn();
    const fetchExtraCount = jest.fn();
    const utils = render(
        <IsicMappedValuesToggle
            onToggle={onToggle}
            fetchExtraCount={fetchExtraCount}
            {...props}
        />,
    );
    return { ...utils, onToggle, fetchExtraCount };
};

describe('IsicMappedValuesToggle', () => {
    test('is off by default so only contributor-reported values match', () => {
        const { getByTestId, getByText } = renderToggle();

        expect(getByTestId('isic4-include-mapped')).not.toBeChecked();
        expect(getByText(ISIC4_MAPPED_TOGGLE_LABEL)).toBeInTheDocument();
    });

    test('reports the new state when ticked', () => {
        const { getByTestId, onToggle } = renderToggle();

        fireEvent.click(getByTestId('isic4-include-mapped'));

        expect(onToggle).toHaveBeenCalledWith(true);
    });

    test('reflects an opt-in restored from the URL', () => {
        const { getByTestId } = renderToggle({ includeMapped: true });

        expect(getByTestId('isic4-include-mapped')).toBeChecked();
    });

    test('does not fetch the extra count without a selection', () => {
        const { fetchExtraCount } = renderToggle();

        expect(fetchExtraCount).not.toHaveBeenCalled();
    });

    test('fetches the extra count for the selection and shows it', () => {
        const isic4 = [{ value: 'division:14', label: 'division:14' }];
        const { fetchExtraCount, getByText } = renderToggle({
            isic4,
            extraCount: 1234,
        });

        expect(fetchExtraCount).toHaveBeenCalledWith(isic4);
        expect(
            getByText(`${ISIC4_MAPPED_TOGGLE_LABEL} (+1,234)`),
        ).toBeInTheDocument();
    });

    test('refetches the extra count when the selection changes', () => {
        const first = [{ value: 'section:C', label: 'section:C' }];
        const second = [{ value: 'class:1410', label: 'class:1410' }];
        const { fetchExtraCount, rerender, onToggle } = renderToggle({
            isic4: first,
        });

        rerender(
            <IsicMappedValuesToggle
                onToggle={onToggle}
                fetchExtraCount={fetchExtraCount}
                isic4={second}
            />,
        );

        expect(fetchExtraCount).toHaveBeenNthCalledWith(1, first);
        expect(fetchExtraCount).toHaveBeenNthCalledWith(2, second);
    });

    test('hides a stale count once the selection is cleared', () => {
        const { queryByText } = renderToggle({ isic4: [], extraCount: 5 });

        expect(
            queryByText(`${ISIC4_MAPPED_TOGGLE_LABEL} (+5)`),
        ).not.toBeInTheDocument();
    });
});
