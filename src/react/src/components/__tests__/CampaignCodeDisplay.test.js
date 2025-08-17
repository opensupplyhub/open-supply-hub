import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import CampaignCodeDisplay from '../CampaignCodeDisplay';

// Mock the react-copy-to-clipboard component
jest.mock('react-copy-to-clipboard', () => ({
    CopyToClipboard: ({ children, onCopy }) => (
        <div onClick={onCopy} data-testid="copy-trigger">
            {children}
        </div>
    ),
}));

// Mock react-toastify
jest.mock('react-toastify', () => ({
    toast: jest.fn(),
}));

describe('CampaignCodeDisplay', () => {
    const defaultProps = {
        campaignCode: 'CC00011',
        isValid: true,
        showDescription: true,
    };

    it('renders campaign code correctly', () => {
        render(<CampaignCodeDisplay {...defaultProps} />);
        
        expect(screen.getByText('Campaign Code')).toBeInTheDocument();
        expect(screen.getByText('CC00011')).toBeInTheDocument();
        expect(screen.getByText('Valid')).toBeInTheDocument();
    });

    it('does not render when campaign code is null', () => {
        const { container } = render(
            <CampaignCodeDisplay 
                campaignCode={null}
                isValid={false}
                showDescription={true}
            />
        );
        
        expect(container.firstChild).toBeNull();
    });

    it('shows description when showDescription is true', () => {
        render(<CampaignCodeDisplay {...defaultProps} />);
        
        expect(screen.getByText(/Use this code to track supplier engagement/)).toBeInTheDocument();
        expect(screen.getByText(/Contact OS Hub staff/)).toBeInTheDocument();
    });

    it('hides description when showDescription is false', () => {
        render(
            <CampaignCodeDisplay 
                {...defaultProps}
                showDescription={false}
            />
        );
        
        expect(screen.queryByText(/Use this code to track supplier engagement/)).not.toBeInTheDocument();
        expect(screen.queryByText(/Contact OS Hub staff/)).not.toBeInTheDocument();
    });

    it('does not show valid badge when isValid is false', () => {
        render(
            <CampaignCodeDisplay 
                {...defaultProps}
                isValid={false}
            />
        );
        
        expect(screen.queryByText('Valid')).not.toBeInTheDocument();
    });

    it('handles copy button click', () => {
        const { toast } = require('react-toastify');
        render(<CampaignCodeDisplay {...defaultProps} />);
        
        const copyTrigger = screen.getByTestId('copy-trigger');
        fireEvent.click(copyTrigger);
        
        expect(toast).toHaveBeenCalledWith('Campaign code copied to clipboard!');
    });

    it('shows copied state after clicking copy', () => {
        render(<CampaignCodeDisplay {...defaultProps} />);
        
        const copyTrigger = screen.getByTestId('copy-trigger');
        fireEvent.click(copyTrigger);
        
        expect(screen.getByText('Copied!')).toBeInTheDocument();
    });

    it('applies correct styling for code display', () => {
        render(<CampaignCodeDisplay {...defaultProps} />);
        
        const codeElement = screen.getByText('CC00011');
        const styles = window.getComputedStyle(codeElement.parentElement);
        
        // Check that monospace font family is applied
        expect(styles.fontFamily).toContain('Monaco');
    });
});