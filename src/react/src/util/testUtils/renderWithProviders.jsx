import React from 'react';
import { render } from '@testing-library/react';
import { Provider } from 'react-redux';

import { store } from '../../configureStore';

const renderWithProviders = (
    ui,
    { reduxStore = store, ...renderOptions } = {},
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
