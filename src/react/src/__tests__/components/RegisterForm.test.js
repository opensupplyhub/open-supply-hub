import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import { screen, waitFor } from '@testing-library/react';

import RegisterForm from '../../components/RegisterForm/RegisterForm';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import {
    startSubmitSignUpForm,
    completeSubmitSignUpForm,
    failSubmitSignUpForm,
} from '../../actions/auth';

const makeAuthState = (overrides = {}) => ({
    auth: {
        fetching: false,
        error: null,
        session: { fetching: false },
        signup: {
            form: {
                email: '',
                name: '',
                description: '',
                website: '',
                contributorType: '',
                otherContributorType: '',
                password: '',
                confirmPassword: '',
                newsletter: false,
                tos: false,
            },
        },
        ...overrides,
    },
});

const renderComponent = (stateOverrides = {}) =>
    renderWithProviders(
        <MemoryRouter>
            <RegisterForm />
        </MemoryRouter>,
        { preloadedState: makeAuthState(stateOverrides) },
    );

describe('RegisterForm', () => {
    test('renders the registration form', () => {
        renderComponent();
        expect(
            screen.getByRole('heading', { name: 'Register' }),
        ).toBeInTheDocument();
        expect(
            screen.getByRole('button', { name: 'Register' }),
        ).toBeInTheDocument();
        expect(screen.getByText('Log In')).toBeInTheDocument();
    });

    test('renders nothing while session is loading', () => {
        const { container } = renderComponent({
            session: { fetching: true },
        });
        expect(container.firstChild).toBeNull();
    });

    test('shows success view after form submission completes', async () => {
        const { reduxStore } = renderComponent();

        reduxStore.dispatch(startSubmitSignUpForm());

        await waitFor(() => {
            expect(
                screen.queryByRole('button', { name: 'Register' }),
            ).toBeInTheDocument();
        });

        reduxStore.dispatch(completeSubmitSignUpForm({}));

        await waitFor(() => {
            expect(
                screen.getByText('Registration was successful!'),
            ).toBeInTheDocument();
        });

        expect(
            screen.getByText(
                'Check your email for instructions about how to verify your account.',
            ),
        ).toBeInTheDocument();
        expect(
            screen.getByText(
                "If you haven't received the email after 24 hours, please follow these steps:",
            ),
        ).toBeInTheDocument();
    });

    test('does not show success view when submission fails', async () => {
        const { reduxStore } = renderComponent();

        reduxStore.dispatch(startSubmitSignUpForm());
        reduxStore.dispatch(failSubmitSignUpForm(['Email already exists.']));

        await waitFor(() => {
            expect(
                screen.queryByText('Registration was successful!'),
            ).not.toBeInTheDocument();
        });

        expect(
            screen.getByRole('heading', { name: 'Register' }),
        ).toBeInTheDocument();
    });

    test('success banner contains all three guidance steps', async () => {
        const { reduxStore } = renderComponent();

        reduxStore.dispatch(startSubmitSignUpForm());
        reduxStore.dispatch(completeSubmitSignUpForm({}));

        await waitFor(() => {
            expect(
                screen.getByText('Registration was successful!'),
            ).toBeInTheDocument();
        });

        expect(
            screen.getByText('Check your spam folder:'),
        ).toBeInTheDocument();
        expect(
            screen.getByText('Allowlist our domain:'),
        ).toBeInTheDocument();
        expect(
            screen.getByText('Contact your email provider or IT department:'),
        ).toBeInTheDocument();
    });
});
