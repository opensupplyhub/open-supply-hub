import React from 'react';
import { Router } from "react-router-dom";
import { createMemoryHistory } from 'react-router-dom';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import { fireEvent } from '@testing-library/react';
import {
    authLoginFormRoute,
} from '../../util/constants';
import AuthLogInFromRoute from '../../components/AuthLogInFromRoute';

describe('AuthLogInFromRoute component', () => {
    const history = createMemoryHistory();
    const renderComponent = (preloadedState = {}) =>
        renderWithProviders(
            <Router history={history}>
               <AuthLogInFromRoute {...preloadedState}/>,
            </Router>
        );

    beforeEach(() => {
        jest.clearAllMocks();
    });

    test("renders component with default params", () => {
        const defaultTitle = 'Unauthorized Access';
        const defaultText = 'Log in to contribute to Open Supply Hub';

        const { getByText, getByRole } = renderComponent();
        const titleEl = getByRole("heading", { level: 2 });
        const titleText = titleEl.textContent.trim();
        const linkEl = getByRole("link", { name: defaultText });

        expect(titleEl).toBeInTheDocument();
        expect(defaultTitle).toBe(titleText);
        expect(getByText(defaultText)).toBeInTheDocument();

        fireEvent.click(linkEl);
        expect(history.location.pathname).toBe(authLoginFormRoute);
    });

    test("renders component with set params", () => {
        const expectedTitle = "Test title";
        const expectedText = "Test text";
        const preloadedState = {
            title: expectedTitle,
            text: expectedText,
        }
        const { getByText } = renderComponent(preloadedState);

        expect(getByText(expectedTitle)).toBeInTheDocument();
        expect(getByText(expectedText)).toBeInTheDocument();
    });
})
