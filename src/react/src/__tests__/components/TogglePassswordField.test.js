import React from 'react';
import { screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import TogglePassswordField from '../../components/TogglePassswordField';
import renderWithProviders from '../../util/testUtils/renderWithProviders';

// Mock the styles and icons
jest.mock('@material-ui/icons', () => ({
    Visibility: () => <div>Visibility</div>,
    VisibilityOff: () => <div>VisibilityOff</div>,
}));

describe('TogglePasswordField', () => {
    let preloadedState;
    const defaultProps = {
        classes: {},
        password: '',
        updatePassword: jest.fn(),
        submitFormOnEnterKeyPress: jest.fn(),
    };
    beforeEach(() => {
        preloadedState = {
            auth: {
                login: {
                    form: {
                        password: '',
                    },
                },
            },
        };
    });

    test('renders password field', () => {
        renderWithProviders(<TogglePassswordField {...defaultProps} />, {
            preloadedState,
        });

        const passwordInput = screen.getByLabelText('Password');

        expect(passwordInput).toBeInTheDocument();
    });

    test('renders input with type "password"', () => {
        renderWithProviders(<TogglePassswordField {...defaultProps} />, {
            preloadedState,
        });

        const passwordInput = screen.getByLabelText('Password');

        expect(passwordInput).toHaveAttribute('type', 'password');
    });

    test('toggles password visibility', () => {
        renderWithProviders(<TogglePassswordField {...defaultProps} />, {
            preloadedState,
        });

        const toggleButton = screen.getByLabelText(
            'toggle password visibility',
        );
        const passwordInput = screen.getByLabelText('Password');

        expect(passwordInput).toHaveAttribute('type', 'password');

        fireEvent.click(toggleButton);
        expect(passwordInput).toHaveAttribute('type', 'text');

        fireEvent.click(toggleButton);
        expect(passwordInput).toHaveAttribute('type', 'password');
    });

    test('updates password value', async () => {
        const user = userEvent.setup()

        renderWithProviders(<TogglePassswordField {...defaultProps} />, {
            preloadedState,
        });

        const passwordInput = screen.getByLabelText('Password');
        await user.type(passwordInput, "newPassword")

        expect(passwordInput).toHaveValue('newPassword')
    });
});
