import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import SelfServiceDromoUploader from '../../components/SelfServiceDromoUploader';
import { processDromoResults } from '../../util/util';

jest.mock('dromo-uploader-react', () => function MockDromoUploader({ open, onCancel, onResults }) {
    return (
        <div data-testid="dromo-uploader" data-open={open ? 'true' : 'false'}>
            <button
                type='button'
                data-testid="dromo-cancel-button"
                onClick={onCancel}
            >
                Cancel
            </button>
            {onResults && (
                <button
                    type='button'
                    data-testid="dromo-results-button"
                    onClick={() => onResults([{ foo: 'bar' }], { filename: 'test.csv' })}
                >
                    Simulate Results
                </button>
            )}
        </div>
    );
});

jest.mock('@material-ui/core/Button', () => (props) => (
    <button type='button' {...props}>{props.children}</button>
));

jest.mock('../../util/util', () => ({
    processDromoResults: jest.fn(),
}));


describe('SelfServiceDromoUploader component', () => {
    const fileInput = {};
    const updateFileName = jest.fn();

    beforeEach(() => {
        jest.clearAllMocks();
    });

    it('renders the upload button', () => {
        const { getByText } = render(<SelfServiceDromoUploader fileInput={fileInput} updateFileName={updateFileName} />);

        expect(getByText('SMART UPLOAD (BETA)')).toBeInTheDocument();
    });

    it('opens the uploader when button is clicked', () => {
        const { getByText, getByTestId } = render(
            <SelfServiceDromoUploader fileInput={fileInput} updateFileName={updateFileName} />
        );

        fireEvent.click(getByText('SMART UPLOAD (BETA)'));

        expect(getByTestId('dromo-uploader')).toHaveAttribute('data-open', 'true');
    });

    it('calls onCancel and closes uploader', () => {
        const { getByText, getByTestId } = render(
            <SelfServiceDromoUploader fileInput={fileInput} updateFileName={updateFileName} />
        );
        
        fireEvent.click(getByText('SMART UPLOAD (BETA)'));
        fireEvent.click(getByTestId('dromo-cancel-button'));

        expect(getByTestId('dromo-uploader')).toHaveAttribute('data-open', 'false');
    });

    it('handles Dromo results and calls processDromoResults', () => {
        const { getByText, getByTestId } = render(
            <SelfServiceDromoUploader fileInput={fileInput} updateFileName={updateFileName} />
        );
        
        fireEvent.click(getByText('SMART UPLOAD (BETA)'));
        fireEvent.click(getByTestId('dromo-results-button'));

        expect(processDromoResults).toHaveBeenCalledWith(
            [{ foo: 'bar' }],
            'test.csv',
            fileInput,
            updateFileName
        );

        expect(getByTestId('dromo-uploader')).toHaveAttribute('data-open', 'false');
    });
});
