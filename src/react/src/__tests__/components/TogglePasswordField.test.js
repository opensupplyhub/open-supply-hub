import React from 'react';
import { screen, fireEvent } from '@testing-library/react';
import TogglePasswordField from '../../components/TogglePasswordField';
import renderWithProviders from '../../util/testUtils/renderWithProviders';

// Mock the styles and icons
jest.mock('@material-ui/icons', () => ({
    Visibility: () => <div>Visibility</div>,
    VisibilityOff: () => <div>VisibilityOff</div>,
}));

describe('TogglePasswordField', () => {
    const defaultProps = {
        id: 'password',
        value: '',
        label: 'Password',
        updatePassword: jest.fn(),
        submitFormOnEnterKeyPress: jest.fn(),
        classes: {},
    };

    test('renders password field', () => {
        renderWithProviders(<TogglePasswordField {...defaultProps} />);

        const passwordInput = screen.getByLabelText('Password');

        expect(passwordInput).toBeInTheDocument();
    });

    test('renders input with type "password"', () => {
        renderWithProviders(<TogglePasswordField {...defaultProps} />);

        const passwordInput = screen.getByLabelText('Password');

        expect(passwordInput).toHaveAttribute('type', 'password');
    });

    test('toggles password visibility', () => {
        renderWithProviders(<TogglePasswordField {...defaultProps} />);

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
        renderWithProviders(<TogglePasswordField {...defaultProps} value="newPassword" />);

        const passwordInput = screen.getByLabelText('Password');

        expect(passwordInput).toHaveValue('newPassword')
    });
});
