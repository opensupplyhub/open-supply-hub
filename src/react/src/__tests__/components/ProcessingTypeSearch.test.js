import React, { createRef } from 'react';
import { act, fireEvent, render } from '@testing-library/react';

import ProcessingTypeSearch from '../../components/Filters/ProcessingTypeSearch';

jest.mock('../../components/SearchIcon', () => () => (
    <span data-testid="search-icon" />
));

const SUGGESTION_DEBOUNCE_MS = 250;

const DYEING = Object.freeze({
    value: 'Dyeing',
    count: 1204,
    in_taxonomy: true,
    facility_types: ['Printing, Product Dyeing and Laundering'],
    dim: false,
});

const EMBROIDERY = Object.freeze({
    value: 'Embroidery',
    count: 310,
    in_taxonomy: true,
    facility_types: [
        'Final Product Assembly',
        'Textile or Material Production',
    ],
    dim: false,
});

const YARN_DYEING = Object.freeze({
    value: 'yarn dyeing services',
    count: 37,
    in_taxonomy: false,
    facility_types: [],
    dim: false,
});

const makeSuggestions = (data, overrides = {}) => ({
    query: 'dyeing',
    data,
    fetching: false,
    error: null,
    ...overrides,
});

describe('ProcessingTypeSearch component', () => {
    /*
    The results panel only opens once the field is focused, so every test
    starts from a focused input the way a user reaching the filter does.
    */
    const renderComponent = (props = {}) => {
        const onProcessingTypeChange = jest.fn();
        const onFetchSuggestions = jest.fn();
        const utils = render(
            <ProcessingTypeSearch
                onProcessingTypeChange={onProcessingTypeChange}
                onFetchSuggestions={onFetchSuggestions}
                {...props}
            />,
        );

        const input = utils.getByRole('combobox');
        fireEvent.focus(input);

        return { ...utils, input, onProcessingTypeChange, onFetchSuggestions };
    };

    const getRowLabels = container =>
        Array.from(
            container.querySelectorAll('#processing-type-suggestions > li'),
        ).map(element => element.textContent);

    const getRowButtons = container =>
        Array.from(
            container.querySelectorAll(
                '#processing-type-suggestions > li > button',
            ),
        );

    beforeEach(() => {
        jest.useFakeTimers();
    });

    afterEach(() => {
        jest.useRealTimers();
    });

    test('splits suggestions into taxonomy and contributor groups', () => {
        const { container } = renderComponent({
            suggestions: makeSuggestions([DYEING, YARN_DYEING, EMBROIDERY]),
        });

        const rows = getRowLabels(container);

        expect(rows[0]).toBe('Standard types');
        expect(rows[1]).toContain('Dyeing');
        expect(rows[2]).toContain('Embroidery');
        expect(rows[3]).toBe('Contributor values');
        expect(rows[4]).toContain('yarn dyeing services');
    });

    test('shows the parent facility types of a taxonomy value', () => {
        const { getByText } = renderComponent({
            suggestions: makeSuggestions([DYEING]),
        });

        expect(
            getByText('Printing, Product Dyeing and Laundering'),
        ).toBeInTheDocument();
    });

    test('shows both parents of a multi-parent value', () => {
        const { getByText } = renderComponent({
            suggestions: makeSuggestions([EMBROIDERY]),
        });

        expect(
            getByText(
                'Final Product Assembly \u00b7 Textile or Material Production',
            ),
        ).toBeInTheDocument();
        expect(getByText('2 parents')).toBeInTheDocument();
    });

    test('badges a contributor value as not in the taxonomy', () => {
        const { getByText, queryByText } = renderComponent({
            suggestions: makeSuggestions([YARN_DYEING]),
        });

        expect(getByText('Not in taxonomy')).toBeInTheDocument();
        expect(queryByText('1 parents')).not.toBeInTheDocument();
    });

    test('shows how many locations carry each value', () => {
        const { getByText } = renderComponent({
            suggestions: makeSuggestions([DYEING, YARN_DYEING]),
        });

        expect(getByText((1204).toLocaleString())).toBeInTheDocument();
        expect(getByText('37')).toBeInTheDocument();
    });

    test('highlights the part of the value that matched the query', () => {
        const { container } = renderComponent({
            suggestions: makeSuggestions([YARN_DYEING], { query: 'dyeing' }),
        });

        const highlighted = Array.from(
            container.querySelectorAll('span[class*="highlight"]'),
        ).map(element => element.textContent);

        expect(highlighted).toEqual(['dyeing']);
    });

    test('dims values outside the selected facility types without hiding them', () => {
        const { container, onProcessingTypeChange } = renderComponent({
            facilityType: [
                {
                    value: 'Final Product Assembly',
                    label: 'Final Product Assembly',
                },
            ],
            suggestions: makeSuggestions([
                EMBROIDERY,
                { ...DYEING, dim: true },
            ]),
        });

        const [embroideryRow, dyeingRow] = getRowButtons(container);

        expect(embroideryRow.className).not.toMatch(/resultRowDim/);
        expect(dyeingRow.className).toMatch(/resultRowDim/);

        fireEvent.click(dyeingRow);

        expect(onProcessingTypeChange).toHaveBeenCalledWith([
            { value: 'Dyeing', label: 'Dyeing', isExact: true },
        ]);
    });

    test('fetches suggestions for the query and the selected facility types', () => {
        const { input, onFetchSuggestions } = renderComponent({
            facilityType: [
                {
                    value: 'Final Product Assembly',
                    label: 'Final Product Assembly',
                },
            ],
        });

        fireEvent.change(input, { target: { value: 'dyeing' } });

        expect(onFetchSuggestions).not.toHaveBeenCalled();

        act(() => {
            jest.advanceTimersByTime(SUGGESTION_DEBOUNCE_MS);
        });

        expect(onFetchSuggestions).toHaveBeenCalledTimes(1);
        expect(onFetchSuggestions).toHaveBeenCalledWith('dyeing', [
            'Final Product Assembly',
        ]);
    });

    test('debounces a burst of keystrokes into a single request', () => {
        const { input, onFetchSuggestions } = renderComponent();

        ['dye', 'dyei', 'dyein', 'dyeing'].forEach(value => {
            fireEvent.change(input, { target: { value } });
            act(() => {
                jest.advanceTimersByTime(SUGGESTION_DEBOUNCE_MS / 2);
            });
        });

        act(() => {
            jest.advanceTimersByTime(SUGGESTION_DEBOUNCE_MS);
        });

        expect(onFetchSuggestions).toHaveBeenCalledTimes(1);
        expect(onFetchSuggestions).toHaveBeenCalledWith('dyeing', []);
    });

    test('fetches the most common values when the panel opens empty', () => {
        const { onFetchSuggestions } = renderComponent();

        act(() => {
            jest.advanceTimersByTime(SUGGESTION_DEBOUNCE_MS);
        });

        expect(onFetchSuggestions).toHaveBeenCalledWith('', []);
    });

    test('rejects queries shorter than three characters', () => {
        const ref = createRef();
        const {
            input,
            getByText,
            onFetchSuggestions,
            onProcessingTypeChange,
        } = renderComponent({ processingTypeSearchRef: ref });

        fireEvent.change(input, { target: { value: 'dy' } });
        act(() => {
            jest.advanceTimersByTime(SUGGESTION_DEBOUNCE_MS);
        });

        expect(
            getByText('Enter at least 3 characters to search processing types'),
        ).toBeInTheDocument();
        expect(input).toHaveAttribute('aria-invalid', 'true');
        expect(onFetchSuggestions).not.toHaveBeenCalled();

        let committed;
        act(() => {
            committed = ref.current.commitPendingQuery();
        });

        expect(committed).toBe(false);
        expect(onProcessingTypeChange).not.toHaveBeenCalled();
        expect(input).toHaveValue('dy');
    });

    test('commitPendingQuery turns pending text into a free-text selection', () => {
        const ref = createRef();
        const { input, onProcessingTypeChange } = renderComponent({
            processingTypeSearchRef: ref,
        });

        fireEvent.change(input, { target: { value: 'cement mixing' } });

        let committed;
        act(() => {
            committed = ref.current.commitPendingQuery();
        });

        expect(committed).toBe(true);
        expect(onProcessingTypeChange).toHaveBeenCalledWith([
            { value: 'cement mixing', label: 'cement mixing' },
        ]);
        expect(input).toHaveValue('');
    });

    test('keyboard navigation walks both groups as one list', () => {
        const { input, onProcessingTypeChange } = renderComponent({
            suggestions: makeSuggestions([DYEING, YARN_DYEING]),
        });

        fireEvent.keyDown(input, { key: 'ArrowDown' });
        fireEvent.keyDown(input, { key: 'ArrowDown' });
        fireEvent.keyDown(input, { key: 'Enter' });

        expect(onProcessingTypeChange).toHaveBeenCalledWith([
            {
                value: 'yarn dyeing services',
                label: 'yarn dyeing services',
                isExact: true,
            },
        ]);
    });

    test('displays and selects the concrete taxonomy value', () => {
        const concreteDyeing = {
            ...DYEING,
            value: 'DYEING',
            label: 'DYEING',
        };
        const { container, getByText, onProcessingTypeChange } =
            renderComponent({
                suggestions: makeSuggestions([concreteDyeing]),
            });

        expect(getByText('DYEING')).toBeInTheDocument();
        fireEvent.click(getRowButtons(container)[0]);

        expect(onProcessingTypeChange).toHaveBeenCalledWith([
            { value: 'DYEING', label: 'DYEING', isExact: true },
        ]);
    });

    test('toggles a selected value using case-only identity', () => {
        const selected = {
            value: 'DYEING',
            label: 'DYEING',
            isExact: true,
        };
        const { container, onProcessingTypeChange } = renderComponent({
            processingType: [selected],
            suggestions: makeSuggestions([DYEING]),
        });

        fireEvent.click(getRowButtons(container)[0]);

        expect(onProcessingTypeChange).toHaveBeenCalledWith([]);
    });

    test('pending text does not duplicate a case-only identity', () => {
        const ref = createRef();
        const { input, onProcessingTypeChange } = renderComponent({
            processingType: [
                { value: 'Dyeing', label: 'Dyeing', isExact: true },
            ],
            processingTypeSearchRef: ref,
        });

        fireEvent.change(input, { target: { value: 'DYEING' } });
        act(() => {
            ref.current.commitPendingQuery();
        });

        expect(onProcessingTypeChange).not.toHaveBeenCalled();
    });

    test('punctuation variants remain separately selectable', () => {
        const suggestion = {
            ...YARN_DYEING,
            value: 'Warehousing / Distribution',
            label: 'Warehousing / Distribution',
        };
        const selected = {
            value: 'Warehousing Distribution',
            label: 'Warehousing Distribution',
            isExact: true,
        };
        const { container, onProcessingTypeChange } = renderComponent({
            processingType: [selected],
            suggestions: makeSuggestions([suggestion]),
        });

        fireEvent.click(getRowButtons(container)[0]);

        expect(onProcessingTypeChange).toHaveBeenCalledWith([
            selected,
            {
                value: 'Warehousing / Distribution',
                label: 'Warehousing / Distribution',
                isExact: true,
            },
        ]);
    });

    test('selecting a suggestion clears the query', () => {
        const { container, input } = renderComponent({
            suggestions: makeSuggestions([DYEING]),
        });

        fireEvent.change(input, { target: { value: 'dyeing' } });
        fireEvent.click(getRowButtons(container)[0]);

        expect(input).toHaveValue('');
    });

    test('removing a chip drops that processing type', () => {
        const { getByLabelText, onProcessingTypeChange } = renderComponent({
            processingType: [
                { value: 'Dyeing', label: 'Dyeing' },
                { value: 'Knitting', label: 'Knitting' },
            ],
        });

        fireEvent.click(getByLabelText('Remove Dyeing'));

        expect(onProcessingTypeChange).toHaveBeenCalledWith([
            { value: 'Knitting', label: 'Knitting' },
        ]);
    });

    test('backspace on an empty input removes the last chip', () => {
        const { input, onProcessingTypeChange } = renderComponent({
            processingType: [
                { value: 'Dyeing', label: 'Dyeing' },
                { value: 'Knitting', label: 'Knitting' },
            ],
        });

        fireEvent.keyDown(input, { key: 'Backspace' });

        expect(onProcessingTypeChange).toHaveBeenCalledWith([
            { value: 'Dyeing', label: 'Dyeing' },
        ]);
    });

    test('clicking a selected value deselects it', () => {
        const { container, onProcessingTypeChange } = renderComponent({
            processingType: [{ value: 'Dyeing', label: 'Dyeing' }],
            suggestions: makeSuggestions([DYEING]),
        });

        fireEvent.click(getRowButtons(container)[0]);

        expect(onProcessingTypeChange).toHaveBeenCalledWith([]);
    });

    test('reports the loading, error and empty states', () => {
        const { getByRole, getByText, queryByText, rerender } =
            renderComponent({
                suggestions: makeSuggestions(null, { fetching: true }),
            });

        expect(getByText(/Loading processing types/)).toBeInTheDocument();

        rerender(
            <ProcessingTypeSearch
                onProcessingTypeChange={jest.fn()}
                suggestions={makeSuggestions([], {
                    error: ['Something went wrong'],
                })}
            />,
        );
        expect(getByRole('alert')).toHaveTextContent(
            'Unable to load processing type suggestions',
        );

        rerender(
            <ProcessingTypeSearch
                onProcessingTypeChange={jest.fn()}
                suggestions={makeSuggestions([])}
            />,
        );
        expect(getByText(/No matching processing types/)).toBeInTheDocument();
        expect(queryByText(/Loading processing types/)).not.toBeInTheDocument();
    });
});
