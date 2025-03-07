import React from 'react';
import { MuiThemeProvider, createMuiTheme } from '@material-ui/core/styles';
import { MemoryRouter } from 'react-router-dom';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import AddLocationData from '../../components/AddLocationData';
import { multipleLocationRoute, contributeProductionLocationRoute } from '../../util/constants';

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

    const renderComponent = (preloadedState = {}) => {
        const theme = createMuiTheme({
            palette: {
                action: { main: '#000', dark: '#333' }, // Define a valid palette
                getContrastText: jest.fn(() => '#fff'), // Mock the method to return a contrast color
            },
        });
        return renderWithProviders(
            <MuiThemeProvider theme={theme}>
                <MemoryRouter>
                    <AddLocationData />
                </MemoryRouter>
            </MuiThemeProvider>,
            { preloadedState }
        );
    };

    beforeEach(() => {
        jest.clearAllMocks();
    });

    it('renders for the authorized user', () => {
        const { getByText } = renderComponent(mockAuthorizedState);
        expect(getByText('Add production location data to OS Hub')).toBeInTheDocument();
    });

    it('renders for the unauthorized user', () => {
        const { getByText } = renderComponent(mockNotAuthorizedState);
        expect(getByText('Log in to contribute to Open Supply Hub')).toBeInTheDocument();
    });

    it('Upload Multiple Locations button should be enabled', () => {
        const { getByRole } = renderComponent(mockAuthorizedState);
        const uploadMultipleLocationsButton = getByRole('button', { name: /Upload Multiple Locations/i });
        expect(uploadMultipleLocationsButton).toBeEnabled();
        expect(uploadMultipleLocationsButton).toHaveAttribute('href', multipleLocationRoute);
    });

    it('Add a Single Location button should be enabled', () => {
        const { getByRole } = renderComponent(mockAuthorizedState);
        const addSingleLocationButton = getByRole('button', { name: /Add a Single Location/i });
        expect(addSingleLocationButton).toBeEnabled();
        expect(addSingleLocationButton).toHaveAttribute('href', contributeProductionLocationRoute);
    });
});
