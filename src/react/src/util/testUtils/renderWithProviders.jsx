import React from 'react';
import { render } from '@testing-library/react';
import { Provider } from 'react-redux';
import { setupStore } from '../../configureStore';

const renderWithProviders = (
    ui,
    {
        preloadedState = {},
        reduxStore = setupStore(preloadedState),
        ...renderOptions
    } = {},
) => {
    const Wrapper = ({ children }) => (
        <Provider store={reduxStore}>{children}</Provider>
    );

    return {
        reduxStore,
        ...render(ui, { wrapper: Wrapper, ...renderOptions }),
    };
};

export default renderWithProviders;
