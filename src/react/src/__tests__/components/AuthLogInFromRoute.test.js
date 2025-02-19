import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import AuthLogInFromRoute from '../../components/AuthLogInFromRoute';
import renderWithProviders from '../../util/testUtils/renderWithProviders';

import {
    LOG_IN_TITLE,
} from '../../util/constants';

describe('AuthLogInFromRoute component', () => {
    const renderComponent = (preloadedState = {},initialEntries = ['/']) =>
        renderWithProviders(
            <MemoryRouter initialEntries={initialEntries}>
                 <AuthLogInFromRoute {...preloadedState}/>,
            </MemoryRouter>
        );

    beforeEach(() => {
        jest.clearAllMocks();
    });

    test("renders component with default params", () => {
        const defaultTitle = " ";
        const defaultText = LOG_IN_TITLE;

        const { getByText, getByRole } = renderComponent();
        const titleEl = getByRole("heading", { level: 2 });
        const titleText = titleEl.textContent;

        expect(titleEl).toBeInTheDocument();
        expect(defaultTitle).toBe(titleText);
        expect(getByText(defaultText)).toBeInTheDocument();
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
