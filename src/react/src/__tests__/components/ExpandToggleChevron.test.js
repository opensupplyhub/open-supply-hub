import React from 'react';
import { render, screen, cleanup } from '@testing-library/react';
import ExpandToggleChevron from '../../components/Shared/ExpandToggleChevron/ExpandToggleChevron';

const defaultProps = {
    isExpanded: false,
    className: 'chevron-class',
    expandLessTestId: 'expand-less-test-id',
    expandMoreTestId: 'expand-more-test-id',
};

describe('ExpandToggleChevron', () => {
    beforeEach(() => {
        cleanup();
    });

    test('renders ExpandMore with expandMoreTestId when isExpanded is false', () => {
        const { getByTestId } = render(<ExpandToggleChevron {...defaultProps} isExpanded={false} />);

        expect(getByTestId('expand-more-test-id')).toBeInTheDocument();
        expect(
            screen.queryByTestId('expand-less-test-id'),
        ).not.toBeInTheDocument();
    });

    test('renders ExpandLess with expandLessTestId when isExpanded is true', () => {
        const { getByTestId } = render(<ExpandToggleChevron {...defaultProps} isExpanded />);

        expect(getByTestId('expand-less-test-id')).toBeInTheDocument();
        expect(
            screen.queryByTestId('expand-more-test-id'),
        ).not.toBeInTheDocument();
    });

    test('forwards className to the visible icon', () => {
        const { getByTestId } = render(
            <ExpandToggleChevron {...defaultProps} isExpanded={false} />,
        );

        expect(getByTestId('expand-more-test-id')).toHaveClass(
            'chevron-class',
        );
    });
});
