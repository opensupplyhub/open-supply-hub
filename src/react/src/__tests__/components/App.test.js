import React from 'react';
import { waitFor, render } from '@testing-library/react';

import renderWithProviders from '../../util/testUtils/renderWithProviders';
import { USER_DEFAULT_STATE } from '../../util/constants';

// Keep App's other internals minimal by mocking heavy children/dependencies.
jest.mock('../../Routes', () => {
    const React = require('react');
    return function Routes() {
        return React.createElement('div', { 'data-testid': 'routes' });
    };
});

// Mock the embedded map action to assert it is called when embed + contributor present.
const mockFetchEmbedConfig = jest.fn(() => () => ({}));
jest.mock('../../actions/embeddedMap', () => ({
    fetchEmbedConfig: (...args) => mockFetchEmbedConfig(...args),
}));

describe('App component', () => {
    let addEventListenerSpy;
    let listeners;

    beforeEach(() => {
        listeners = {};
        const originalAddEventListener = window.addEventListener.bind(window);
        addEventListenerSpy = jest
            .spyOn(window, 'addEventListener')
            .mockImplementation((type, cb, options) => {
                listeners[type] = cb;
                return originalAddEventListener(type, cb, options);
            });
        mockFetchEmbedConfig.mockClear();
    });

    afterEach(() => {
        if (addEventListenerSpy) addEventListenerSpy.mockRestore();
        delete window.Rollbar;
        // Do not reset modules here to avoid multiple React instances across tests.
    });

    test('registers global error handler and calls logErrorToRollbar', async () => {
        const utilModule = require('../../util/util');
        const logSpy = jest
            .spyOn(utilModule, 'logErrorToRollbar')
            .mockImplementation(() => {});

        const { UnconnectedApp } = require('../../App.jsx');

        const props = {
            embed: false,
            contributor: null,
            getEmbedConfig: jest.fn(),
            config: { color: '', font: 'Darker Grotesque' },
            embedError: null,
            embedLoading: false,
            user: { ...USER_DEFAULT_STATE, isAnon: false, id: 5 },
        };

        render(<UnconnectedApp {...props} />);

        await waitFor(() => {
            expect(typeof listeners.error).toBe('function');
        });

        const err = new Error('Third-party lib failure');
        listeners.error({
            message: err.message,
            filename: 'leaflet.js',
            lineno: 1,
            colno: 1,
            error: err,
        });

        await waitFor(() => {
            expect(logSpy).toHaveBeenCalled();
        });
    });

    test('dispatches fetchEmbedConfig when embed is true and contributor exists', async () => {
        const contributorId = 1705;

        const { UnconnectedApp } = require('../../App.jsx');

        const props = {
            embed: true,
            contributor: { value: contributorId, label: 'Contributor' },
            getEmbedConfig: mockFetchEmbedConfig,
            config: { color: '', font: 'Darker Grotesque' },
            embedError: null,
            embedLoading: false,
            user: USER_DEFAULT_STATE,
        };

        render(<UnconnectedApp {...props} />);

        await waitFor(() => {
            expect(mockFetchEmbedConfig).toHaveBeenCalledWith(contributorId);
        });
    });
});


