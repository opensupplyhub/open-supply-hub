import React from 'react';
import { fireEvent } from '@testing-library/react';
import DownloadExcelButton from '../../components/Dashboard/DownloadExcelButton';
import renderWithProviders from '../../util/testUtils/renderWithProviders';

jest.mock('../../components/DownloadIcon', () => () => <svg data-testid="download-icon" />);

describe('DownloadExcelButton component', () => {
  const mockHandleDownload = jest.fn();
  const defaultProps = {
    fetching: false,
    handleDownload: mockHandleDownload,
  };

  const renderComponent = (props = {}) => renderWithProviders(
    <DownloadExcelButton {...defaultProps} {...props} />
  );
  

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('should render the DownloadExcelButton', () => {
    const { getByText, getByTestId } = renderComponent();
    
    expect(getByTestId('download-icon')).toBeInTheDocument();
    expect(getByText('Download Excel')).toBeInTheDocument();
  });

  test('should call handleDownload when button is clicked', () => {
    const { getByRole } = renderComponent();
    const button = getByRole('button', { name: 'Download Excel' });
    fireEvent.click(button);

    expect(mockHandleDownload).toHaveBeenCalledTimes(1);
  });

  test('should disable button when fetching is true', () => {
    const { getByRole } = renderComponent({ fetching: true });
    const button = getByRole('button', { name: 'Download Excel' });

    expect(button).toBeDisabled();
  });

  test('should enable button when fetching is false', () => {
    const { getByRole } = renderComponent({ fetching: false });
    const button = getByRole('button', { name: 'Download Excel' });

    expect(button).toBeEnabled();
  });
});
