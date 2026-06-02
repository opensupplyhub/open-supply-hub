import React from 'react';
import { fireEvent } from '@testing-library/react';

import ModerationMatchConfirmButton from '../../components/Dashboard/ModerationMatchConfirmButton';
import { MODERATION_STATUSES_ENUM } from '../../util/constants';
import renderWithProviders from '../../util/testUtils/renderWithProviders';

jest.mock('../../components/Contribute/DialogTooltip', () => ({ text, childComponent }) => (
    <div>
        <div data-testid="dialog-tooltip-text">{text}</div>
        {childComponent}
    </div>
));

describe('ModerationMatchConfirmButton component', () => {
    const mockConfirmPotentialMatch = jest.fn();

    const defaultProps = {
        classes: {
            confirmButtonStyles: 'confirm-button-styles',
            claimTooltipWrapper: 'claim-tooltip-wrapper',
        },
        match: {
            matchOsId: 'US2020123ABC',
            eventOsId: 'US2020456DEF',
        },
        moderation: {
            status: MODERATION_STATUSES_ENUM.PENDING,
            fetching: false,
        },
        actions: {
            confirmPotentialMatch: mockConfirmPotentialMatch,
        },
        isDisabled: false,
        ariaLabel: 'Confirm potential match button tooltip',
    };

    const renderComponent = (props = {}) =>
        renderWithProviders(
            <ModerationMatchConfirmButton {...defaultProps} {...props} />,
        );

    beforeEach(() => {
        jest.clearAllMocks();
    });

    test('renders enabled confirm button and calls confirm handler with matchOsId', () => {
        const { getByTestId, queryByTestId } = renderComponent();
        const button = getByTestId('moderation-match-confirm-button');

        expect(button).toBeEnabled();
        expect(button).toHaveTextContent('Confirm');
        expect(queryByTestId('dialog-tooltip-text')).not.toBeInTheDocument();

        fireEvent.click(button);
        expect(mockConfirmPotentialMatch).toHaveBeenCalledTimes(1);

        const { matchOsId } = defaultProps.match;
        expect(mockConfirmPotentialMatch).toHaveBeenCalledWith(matchOsId);
    });

    test('disables confirm button when moderation fetching is true and does not call handler', () => {
        const { getByTestId } = renderComponent({
            moderation: {
                status: MODERATION_STATUSES_ENUM.PENDING,
                fetching: true,
            },
        });
        const button = getByTestId('moderation-match-confirm-button');

        expect(button).toBeDisabled();
        expect(button).toHaveTextContent('Confirm');

        fireEvent.click(button);
        expect(mockConfirmPotentialMatch).not.toHaveBeenCalled();
    });

    test('renders matched disabled button and matched tooltip text when approved and os ids match', () => {
        const { getByTestId } = renderComponent({
            isDisabled: true,
            match: {
                matchOsId: 'US2020123ABC',
                eventOsId: 'US2020123ABC',
            },
            moderation: {
                status: MODERATION_STATUSES_ENUM.APPROVED,
                fetching: false,
            },
        });
        const button = getByTestId('moderation-match-confirm-button');

        expect(button).toBeDisabled();
        expect(button).toHaveTextContent('Matched');
        expect(getByTestId('dialog-tooltip-text')).toHaveTextContent(
            'Moderation event data has been already matched to this production location.',
        );

        fireEvent.click(button);
        expect(mockConfirmPotentialMatch).not.toHaveBeenCalled();
    });

    test('renders disabled confirm button and rejected tooltip text when disabled and not matched', () => {
        const { getByTestId } = renderComponent({
            isDisabled: true,
            moderation: {
                status: MODERATION_STATUSES_ENUM.REJECTED,
                fetching: false,
            },
        });
        const button = getByTestId('moderation-match-confirm-button');

        expect(button).toBeDisabled();
        expect(button).toHaveTextContent('Confirm');
        expect(getByTestId('dialog-tooltip-text')).toHaveTextContent(
            "You can't confirm the match when moderation event is rejected.",
        );
    });

    test('renders approved status tooltip text when disabled and approved but ids differ', () => {
        const { getByTestId } = renderComponent({
            isDisabled: true,
            match: {
                matchOsId: 'US2020123ABC',
                eventOsId: 'US2020456DEF',
            },
            moderation: {
                status: MODERATION_STATUSES_ENUM.APPROVED,
                fetching: false,
            },
        });
        const button = getByTestId('moderation-match-confirm-button');

        expect(button).toBeDisabled();
        expect(button).toHaveTextContent('Confirm');
        expect(getByTestId('dialog-tooltip-text')).toHaveTextContent(
            "You can't confirm the match when moderation event is approved.",
        );
    });
});
