import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { MuiThemeProvider, createMuiTheme } from '@material-ui/core/styles';

import DataCenterFields from '../../components/Contribute/DataCenterFields/DataCenterFields';
import {
    DATA_CENTER_FORM_SECTIONS,
    DATA_CENTER_FORM_INITIAL_VALUES,
} from '../../components/Contribute/DataCenterFields/constants';

const theme = createMuiTheme();

const makeContributionForm = (overrides = {}) => ({
    values: { ...DATA_CENTER_FORM_INITIAL_VALUES },
    touched: {},
    errors: {},
    setFieldValue: jest.fn(),
    setFieldTouched: jest.fn(),
    ...overrides,
});

const renderDataCenterFields = contributionForm =>
    render(
        <MuiThemeProvider theme={theme}>
            <DataCenterFields contributionForm={contributionForm} />
        </MuiThemeProvider>,
    );

describe('DataCenterFields', () => {
    test('renders all schema sections, collapsed by default', () => {
        renderDataCenterFields(makeContributionForm());

        expect(screen.getByTestId('data-center-fields')).toBeInTheDocument();
        DATA_CENTER_FORM_SECTIONS.forEach(section => {
            const header = screen.getByTestId(
                `data-center-section-${section.label}`,
            );
            expect(header).toBeInTheDocument();
            expect(header).toHaveAttribute('aria-expanded', 'false');
        });
    });

    test('includes a provenance section', () => {
        renderDataCenterFields(makeContributionForm());

        expect(
            screen.getByTestId('data-center-section-Source details'),
        ).toBeInTheDocument();
    });

    test('expanding a section reveals its inputs', () => {
        renderDataCenterFields(makeContributionForm());
        const header = screen.getByTestId('data-center-section-Utility Usage');

        fireEvent.click(header);

        expect(header).toHaveAttribute('aria-expanded', 'true');
        expect(
            screen.getByLabelText('Power Usage Effectiveness (PUE)'),
        ).toBeInTheDocument();
    });

    test('shows a short description under each field label', () => {
        renderDataCenterFields(makeContributionForm());
        fireEvent.click(screen.getByTestId('data-center-section-Utility Usage'));

        expect(
            screen.getByText(
                'Enter the Power Usage Effectiveness: the ratio of total ' +
                    'energy used to energy delivered to computing equipment. ' +
                    'For example: 1.25.',
            ),
        ).toBeInTheDocument();
    });

    test('measures with units render a value and a units input', () => {
        renderDataCenterFields(makeContributionForm());
        fireEvent.click(screen.getByTestId('data-center-section-Utility Usage'));

        expect(screen.getByLabelText('Capacity')).toBeInTheDocument();
        expect(screen.getByLabelText('Capacity units')).toBeInTheDocument();
    });

    test('typing in an input updates the Formik field', () => {
        const contributionForm = makeContributionForm();
        renderDataCenterFields(contributionForm);
        fireEvent.click(screen.getByTestId('data-center-section-Utility Usage'));

        fireEvent.change(screen.getByLabelText('Capacity'), {
            target: { value: '20' },
        });

        expect(contributionForm.setFieldValue).toHaveBeenCalledWith(
            'capacity',
            '20',
        );
        expect(contributionForm.setFieldTouched).toHaveBeenCalledWith(
            'capacity',
            true,
            false,
        );
    });

    test('shows a validation error for a touched invalid field', () => {
        const contributionForm = makeContributionForm({
            touched: { dateOfSource: true },
            errors: {
                dateOfSource:
                    'Date of source must be a date in YYYY, YYYY-MM, or YYYY-MM-DD format.',
            },
        });
        renderDataCenterFields(contributionForm);
        fireEvent.click(
            screen.getByTestId('data-center-section-Source details'),
        );

        expect(
            screen.getByText(
                'Date of source must be a date in YYYY, YYYY-MM, or YYYY-MM-DD format.',
            ),
        ).toBeInTheDocument();
    });

    test('sections toggle closed again on second click', () => {
        renderDataCenterFields(makeContributionForm());
        const header = screen.getByTestId(
            'data-center-section-Named Entities',
        );

        fireEvent.click(header);
        expect(header).toHaveAttribute('aria-expanded', 'true');

        fireEvent.click(header);
        expect(header).toHaveAttribute('aria-expanded', 'false');
    });
});
