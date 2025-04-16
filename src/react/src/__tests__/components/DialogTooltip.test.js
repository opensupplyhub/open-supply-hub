import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import DialogTooltip from '../../components/Contribute/DialogTooltip';

global.cancelAnimationFrame = jest.fn();

jest.mock('@popperjs/core', () => ({
    __esModule: true,
    default: jest.fn(() => ({
        destroy: jest.fn(),
        update: jest.fn(),
        scheduleUpdate: jest.fn(),
        enableEventListeners: jest.fn(),
        disableEventListeners: jest.fn(),
        setOptions: jest.fn(),
    })),
}));

beforeAll(() => {
    global.Node = global.Node || {};
});

describe('DialogTooltip Component', () => {
    test('renders tooltip on hover', async () => {
        const mockChildComponent = <span>Hover over this element</span>;
        const mockText = "You'll be able to claim the location after the moderation is done";

        render(
            <DialogTooltip text={mockText} childComponent={mockChildComponent} classes={{}} />
        );

        expect(screen.queryByText(mockText)).not.toBeInTheDocument();

        fireEvent.mouseEnter(screen.getByText('Hover over this element'));
        await waitFor(() => {
            expect(screen.getByText(mockText)).toBeInTheDocument();
        });
    });

    test('hides tooltip on mouse leave', async () => {
        const mockChildComponent = <span>Hover over this element</span>;
        const mockText = "Test tooltip";

        render(
            <DialogTooltip text={mockText} childComponent={mockChildComponent} classes={{}} />
        );

        const element = screen.getByText('Hover over this element');

        fireEvent.mouseEnter(element);
        await waitFor(() => {
            expect(screen.getByText(mockText)).toBeInTheDocument();
        });

        fireEvent.mouseLeave(element);
        await waitFor(() => {
            expect(screen.queryByText(mockText)).not.toBeInTheDocument();
        });
    });
});
