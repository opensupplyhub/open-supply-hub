import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import ListCleaningTour from '../../components/ListCleaningTour';

const Page = ({ onDone }) => (
    <div>
        <div data-tour="intro">tracker</div>
        <div data-tour="automatic">automatic</div>
        <div data-tour="chips">chips</div>
        <ListCleaningTour onDone={onDone} />
    </div>
);

describe('ListCleaningTour', () => {
    test('walks through the steps whose targets are on the page', () => {
        const onDone = jest.fn();
        render(<Page onDone={onDone} />);
        expect(screen.getByText('Where you are in the upload')).toBeInTheDocument();
        expect(screen.getByText('1 of 3')).toBeInTheDocument();
        fireEvent.click(screen.getByRole('button', { name: 'Next' }));
        expect(screen.getByText('Automatic fixes')).toBeInTheDocument();
        fireEvent.click(screen.getByRole('button', { name: 'Back' }));
        expect(screen.getByText('Where you are in the upload')).toBeInTheDocument();
        fireEvent.click(screen.getByRole('button', { name: 'Next' }));
        fireEvent.click(screen.getByRole('button', { name: 'Next' }));
        expect(screen.getByText('Required fixes first, then recommended')).toBeInTheDocument();
        fireEvent.click(screen.getByRole('button', { name: 'Got it' }));
        expect(onDone).toHaveBeenCalledTimes(1);
    });

    test('skip and Escape both end the tour', () => {
        const onDone = jest.fn();
        render(<Page onDone={onDone} />);
        fireEvent.click(screen.getByRole('button', { name: 'Skip tour' }));
        expect(onDone).toHaveBeenCalledTimes(1);
        act(() => {
            window.dispatchEvent(new window.KeyboardEvent('keydown', { key: 'Escape' }));
        });
        expect(onDone).toHaveBeenCalledTimes(2);
    });

    test('renders nothing when no target is on the page', () => {
        const { container } = render(<ListCleaningTour onDone={() => {}} />);
        expect(container).toBeEmptyDOMElement();
    });
});
