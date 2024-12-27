import React from 'react';
import { render } from '@testing-library/react';
import configureMockStore from 'redux-mock-store';
import { Provider } from 'react-redux';
import { MuiThemeProvider, createMuiTheme } from '@material-ui/core/styles';
import { MemoryRouter } from 'react-router-dom';
import AddLocationData from '../../components/AddLocationData';

const mockStore = configureMockStore();

describe('AddLocationData component', () => {
    const mockAuthorizedState = {
        auth: {
            user: { user: { isAnon: false } },
            session: { fetching: false },
        },
    };

    const mockNotAuthorizedState = {
        auth: {
            user: { user: { isAnon: true } },
            session: { fetching: false },
        },
    };

    const renderComponent = (state = {}) => {
        const store = mockStore(state);
        const theme = createMuiTheme({
            palette: {
                action: { main: '#000', dark: '#333' }, // Define a valid palette
                getContrastText: jest.fn(() => '#fff'), // Mock the method to return a contrast color
            },
        });
        return render(
            <Provider store={store}>
                <MuiThemeProvider theme={theme}>
                    <MemoryRouter>
                        <AddLocationData />
                    </MemoryRouter>
                </MuiThemeProvider>
            </Provider>
        );
    };

    beforeEach(() => {
        jest.clearAllMocks();
    });

    it('renders with the authorized user', () => {
        const { getByText } = renderComponent(mockAuthorizedState);
        expect(getByText('Add production location data to OS Hub')).toBeInTheDocument();
    });

    it('renders with the not authorized user', () => {
        const { getByText } = renderComponent(mockNotAuthorizedState);
        expect(getByText('Log in to contribute to Open Supply Hub')).toBeInTheDocument();
    });
});