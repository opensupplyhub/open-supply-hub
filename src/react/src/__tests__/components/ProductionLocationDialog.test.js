import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter as Router, useHistory } from 'react-router-dom';
import UserEvent from "user-event";
import ProductionLocationDialog from '../../components/Contribute/ProductionLocationDialog';

jest.mock('react-router-dom', () => ({
    ...jest.requireActual('react-router-dom'),
    useHistory: jest.fn(),
}));

const mockHistoryPush = jest.fn();

beforeEach(() => {
    useHistory.mockReturnValue({
        push: mockHistoryPush,
    });
});

test('renders dialog content', () => {
    render(
        <Router>
            <ProductionLocationDialog classes={{}} />
        </Router>
    );

    expect(screen.getByText(/Thanks for adding data for this production location!/i)).toBeInTheDocument();
    expect(screen.getByText(/Facility name/i)).toBeInTheDocument();
    expect(screen.getByText(/OS ID/i)).toBeInTheDocument();
    expect(screen.getByText(/Pending/i)).toBeInTheDocument();
});

test('should render multiple instances of text element', () => {
    const text = "Unifill Composite Dyeing Mills Ltd.";
    
    render(
        <Router>
            <ProductionLocationDialog classes={{}} />
        </Router>
    );

    const elements = screen.getAllByText(new RegExp(text, 'i'));

    expect(elements).toHaveLength(2);
});

test('navigates when "Search OS Hub" button is clicked', () => {
    render(
        <Router>
            <ProductionLocationDialog classes={{}} />
        </Router>
    );

    const button = screen.getByText(/Search OS Hub/i);
    UserEvent.click(button);

    expect(mockHistoryPush).toHaveBeenCalledWith('/');
});

test('calls console log when "Submit another Location" button is clicked', () => {
    const consoleLogSpy = jest.spyOn(console, 'log').mockImplementation();

    render(
        <Router>
            <ProductionLocationDialog classes={{}} />
        </Router>
    );

    const button = screen.getByText(/Submit another Location/i);
    UserEvent.click(button);

    expect(consoleLogSpy).toHaveBeenCalledWith('submit another location');
    consoleLogSpy.mockRestore();
});
