import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter as Router, useHistory } from 'react-router-dom';
import ProductionLocationDialog from '../../components/Contribute/ProductionLocationDialog';

jest.mock('react-router-dom', () => ({
    ...jest.requireActual('react-router-dom'),
    useHistory: jest.fn(),
}));

const mockHistoryPush = jest.fn();

describe('ProductionLocationDialog', () => {
    const defaultProps = {
        osID: 'US2021250D1DTN7',
        moderationStatus: 'PENDING',
        data: {
            raw_json: {
                name: 'Production Location Name',
                address: '1234 Production Location St, City, State, 12345',
            },
            fields: {
            }
        }
    }

    beforeEach(() => {
        useHistory.mockReturnValue({
            push: mockHistoryPush,
        });
    });

    test('renders dialog content', () => {
        render(
            <Router>
                <ProductionLocationDialog 
                    classes={{}} 
                    data={defaultProps.data}
                    osID={defaultProps.osID}
                    moderationStatus={defaultProps.moderationStatus}
                />
            </Router>
        );

        expect(screen.getByText(/Thanks for adding data for this production location!/i)).toBeInTheDocument();
        expect(screen.getByText(/Facility name/i)).toBeInTheDocument();
        expect(screen.getByText(/OS ID/i)).toBeInTheDocument();
        expect(screen.getByText(/Pending/i)).toBeInTheDocument();
    });
});
