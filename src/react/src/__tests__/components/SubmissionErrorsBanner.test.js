import React from 'react';
import { screen } from '@testing-library/react';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import SubmissionErrorsBanner from '../../components/InitialClaimFlow/ClaimForm/SubmissionErrorsBanner/SubmissionErrorsBanner';

const FIELD_ERROR =
    'facility_product_types: Ensure this field has no more than 50 characters.';
const FORMATTED_FIELD_ERROR =
    'Product Types: Ensure this field has no more than 50 characters.';
const BARE_ERROR = 'There is already a pending claim on this facility.';
const MULTIPLE_ERRORS_INTRO =
    'Please fix the following validation errors:';

const renderBanner = (errors = null) =>
    renderWithProviders(<SubmissionErrorsBanner errors={errors} />);

describe('SubmissionErrorsBanner', () => {
    test('renders nothing when errors is null', () => {
        const { container } = renderBanner();

        expect(container).toBeEmptyDOMElement();
    });

    test('renders nothing when errors is an empty array', () => {
        const { container } = renderBanner([]);

        expect(container).toBeEmptyDOMElement();
    });

    test('renders a single field error inline with formatted label', () => {
        renderBanner([FIELD_ERROR]);

        expect(screen.getByText('ERROR!')).toBeInTheDocument();
        expect(screen.getByText(FORMATTED_FIELD_ERROR)).toBeInTheDocument();
        expect(
            screen.queryByText(MULTIPLE_ERRORS_INTRO),
        ).not.toBeInTheDocument();
        expect(screen.queryByRole('list')).not.toBeInTheDocument();
    });

    test('renders a single bare API error without field formatting', () => {
        renderBanner([BARE_ERROR]);

        expect(screen.getByText(BARE_ERROR)).toBeInTheDocument();
        expect(screen.queryByRole('list')).not.toBeInTheDocument();
    });

    test('renders multiple errors as a formatted list', () => {
        renderBanner([
            FIELD_ERROR,
            'business_website: Ensure this field has no more than 200 characters.',
        ]);

        expect(screen.getByText(MULTIPLE_ERRORS_INTRO)).toBeInTheDocument();

        const listItems = screen.getAllByRole('listitem');
        expect(listItems).toHaveLength(2);
        expect(listItems[0]).toHaveTextContent(FORMATTED_FIELD_ERROR);
        expect(listItems[1]).toHaveTextContent(
            'Company Website: Ensure this field has no more than 200 characters.',
        );
    });

    test('deduplicates identical error messages', () => {
        renderBanner([FIELD_ERROR, FIELD_ERROR, BARE_ERROR]);

        const listItems = screen.getAllByRole('listitem');
        expect(listItems).toHaveLength(2);
        expect(listItems[0]).toHaveTextContent(FORMATTED_FIELD_ERROR);
        expect(listItems[1]).toHaveTextContent(BARE_ERROR);
    });
});
