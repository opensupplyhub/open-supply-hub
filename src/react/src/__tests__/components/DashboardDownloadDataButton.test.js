import React from 'react';
import { fireEvent } from '@testing-library/react';
import DashboardDownloadDataButton from '../../components/Dashboard/DashboardDownloadDataButton';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import { toast } from 'react-toastify';

jest.mock('react-toastify', () => ({
  toast: jest.fn(),
}));

jest.mock('../../components/Dashboard/DownloadExcelButton', () => (props) => (
  <button type="button" onClick={props.handleDownload}>Download Excel Button</button>
));

describe('DashboardDownloadDataButton component', () => {
  const mockDownloadData = jest.fn();
  const defaultProps = {
    fetching: false,
    downloadPayload: [
      {
        moderation_id: 1,
        created_at: '2024-10-23T12:34:56Z',
        name: 'Generic Soft Inc',
        country: {
          name: 'USA',
          alpha_2: 'US',
          alpha_3: 'USA',
          numeric: '840',
        },
        contributor_name: 'Contributor 1',
        source: 'API',
        moderation_status: 'PENDING',
        moderation_decision_date: null,
        updated_at: '2024-10-23T12:34:56Z',
      },
    ],
    downloadData: mockDownloadData,
    downloadError: null,
  };

  const renderComponent = (props = {}) => {
    return renderWithProviders(<DashboardDownloadDataButton {...defaultProps} {...props} />);
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('should render the DownloadExcelButton', () => {
    const { getByText } = renderComponent();
    expect(getByText('Download Excel Button')).toBeInTheDocument();
  });

  test('should call downloadData with downloadPayload when handleDownload is triggered', () => {
    const { getByText } = renderComponent();
    const downloadButton = getByText('Download Excel Button');
    fireEvent.click(downloadButton);

    expect(mockDownloadData).toHaveBeenCalledTimes(1);
    expect(mockDownloadData).toHaveBeenCalledWith(defaultProps.downloadPayload);
  });

  test('should show toast error message when downloadError is present', () => {
    renderComponent({ downloadError: ['Error message'] });

    expect(toast).toHaveBeenCalledTimes(1);
    expect(toast).toHaveBeenCalledWith('A problem prevented downloading the data');
  });

  test('should not call toast when there is no downloadError', () => {
    renderComponent();

    expect(toast).not.toHaveBeenCalled();
  });
});
