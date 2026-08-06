import React from 'react';
import { fireEvent } from '@testing-library/react';

import RejectModerationEventDialog from '../../components/Dashboard/RejectModerationEventDialog';
import { MODERATION_STATUSES_ENUM } from '../../util/constants';
import renderWithProviders from '../../util/testUtils/renderWithProviders';

const mockUpdateModerationEvent = jest.fn();
const mockCloseDialog = jest.fn();

jest.mock('react-quill-new', () => ({ value, onChange }) => (
    <textarea
        data-testid="fake-editor"
        value={value.replace(/<\/?p>/g, '').replace(/&nbsp;/g, ' ')}
        onChange={(e) => {
            const text = e.target.value;
            // Mimic Quill's getSemanticHTML(), which encodes every
            // space as &nbsp; in the emitted HTML.
            const html = `<p>${text.replace(/ /g, '&nbsp;')}</p>`;
            onChange(html, null, 'user', {
                getText: () => `${text}\n`,
            });
        }}
    />
));

jest.mock('@material-ui/core/Tooltip', () => ({ children, title, open, onOpen, onClose }) => (
    <div
        data-testid="tooltip-wrapper"
        onMouseOver={onOpen}
        onFocus={onOpen}
        onMouseOut={onClose}
        onBlur={onClose}
    >
        {children}
        {open && <div data-testid="tooltip">{title}</div>}
    </div>
));

describe('RejectModerationEventDialog component', () => {
    const defaultProps = {
        updateModerationEvent: mockUpdateModerationEvent,
        isOpenDialog: true,
        closeDialog: mockCloseDialog,
    };

    afterEach(() => {
        jest.clearAllMocks();
    });

    test('renders the dialog with the correct title and buttons', () => {
        const { getByText, getByRole } = renderWithProviders(
            <RejectModerationEventDialog {...defaultProps} />,
        );

        expect(getByText("Reject this Moderation Event?")).toBeInTheDocument();
        expect(getByText('Keep the instructions brief and action orientated. (Suggested opening, "Just a few fixes are needed.")')).toBeInTheDocument();
        expect(getByRole('button', {name: /Cancel/i})).toBeInTheDocument();
        expect(getByRole('button', {name: /Reject/i})).toBeInTheDocument();
    });

    test('calls closeDialog when "Cancel" button is clicked', () => {
        const { getByRole } = renderWithProviders(<RejectModerationEventDialog {...defaultProps} />);
        const cancelButton = getByRole('button', {name: /Cancel/i});

        fireEvent.click(cancelButton);
        expect(mockCloseDialog).toHaveBeenCalledTimes(1);
    });

    test('reject button is disabled if editor text is less than 30 characters', () => {
        const { getByRole } = renderWithProviders(
            <RejectModerationEventDialog {...defaultProps} />
        );
        const rejectButton = getByRole('button', {name: /Reject/i});

        expect(rejectButton).toBeDisabled();
      });

    test('reject button is enabled when editor text is at least 30 characters and calls updateModerationEvent and closeDialog on click', async () => {
        const { getByRole, getByTestId } = renderWithProviders(
            <RejectModerationEventDialog {...defaultProps} />
        );
        const rejectButton = getByRole('button', {name: /Reject/i});

        expect(rejectButton).toBeDisabled();

        const fakeEditor = getByTestId('fake-editor');
        const validText = 'a'.repeat(30);

        fireEvent.change(fakeEditor, { target: { value: validText } });

        expect(rejectButton).toBeEnabled();

        fireEvent.click(rejectButton);

        expect(mockUpdateModerationEvent).toHaveBeenCalledTimes(1);
        expect(mockUpdateModerationEvent).toHaveBeenCalledWith(
            MODERATION_STATUSES_ENUM.REJECTED,
            validText,
            `<p>${validText}</p>`,
        );
        expect(mockCloseDialog).toHaveBeenCalledTimes(1);
    });

    test('decodes quill &nbsp; space encoding in the submitted HTML', () => {
        const { getByRole, getByTestId } = renderWithProviders(
            <RejectModerationEventDialog {...defaultProps} />
        );
        const fakeEditor = getByTestId('fake-editor');
        const textWithSpaces = 'just a few fixes are needed before we accept';

        fireEvent.change(fakeEditor, { target: { value: textWithSpaces } });

        // Typing spaces must not be swallowed by the value round-trip.
        expect(fakeEditor).toHaveValue(textWithSpaces);

        fireEvent.click(getByRole('button', { name: /Reject/i }));

        // The submitted HTML uses regular spaces, not &nbsp;.
        expect(mockUpdateModerationEvent).toHaveBeenCalledWith(
            MODERATION_STATUSES_ENUM.REJECTED,
            textWithSpaces,
            `<p>${textWithSpaces}</p>`,
        );
    });

    test('displays tooltip on hover when reject button is disabled', () => {
        const { getByRole, queryByText } = renderWithProviders(
            <RejectModerationEventDialog {...defaultProps} />
        );
        const tooltipText = 'Please provide a message with at least 30 characters.';

        expect(queryByText(tooltipText)).not.toBeInTheDocument();

        const rejectButton = getByRole('button', { name: /Reject/i });
        expect(rejectButton).toBeDisabled();

        fireEvent.mouseOver(rejectButton);

        expect(queryByText(tooltipText)).toBeInTheDocument();

        fireEvent.mouseOut(rejectButton);

        expect(queryByText(tooltipText)).not.toBeInTheDocument()
    });

    test('does not display tooltip when reject button is enabled', () => {
        const { getByRole, queryByText, getByTestId } = renderWithProviders(
            <RejectModerationEventDialog {...defaultProps} />
        );
        const rejectButton = getByRole('button', { name: /Reject/i });
        const fakeEditor = getByTestId('fake-editor');
        const validText = 'a'.repeat(30);

        fireEvent.change(fakeEditor, { target: { value: validText } });

        expect(rejectButton).toBeEnabled();

        fireEvent.mouseOver(rejectButton);
        expect(queryByText('Please provide a message with at least 30 characters.')).not.toBeInTheDocument();
    });
});
