import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter as Router } from 'react-router-dom';
import { Provider } from 'react-redux';
import configureStore from 'redux-mock-store';
import GDPRNotification from './../../components/GDPRNotification';

test('GDPR Notification component', () => {
    const mockStore = configureStore();

    const initialState = {
        ui: {
            // Force GDPR notification component to be opened
            gdprOpen: true,
        },
    };

    const store = mockStore(initialState);

    render (
        <Provider store={store}>
            <Router>
                <GDPRNotification />
            </Router>
        </Provider>
    );

    // Check component presence on the page
    const GDPRNotificationElem = screen.getByTestId('gdpr-notification');
    expect(GDPRNotificationElem).toBeInTheDocument();

    // Check if the SET_GDPR_OPEN action was dispatched when the component is mounted
    const actions = store.getActions();
    expect(actions).toContainEqual({ type: 'SET_GDPR_OPEN', payload: true, error: false });
})
