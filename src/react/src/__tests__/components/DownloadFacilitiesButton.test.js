import React from 'react';
import { render, fireEvent, waitFor, screen } from '@testing-library/react';
import { MuiThemeProvider, createMuiTheme } from '@material-ui/core/styles';
import { Provider } from 'react-redux';
import { createStore } from 'redux';
import DownloadFacilitiesButton from '../../components/DownloadFacilitiesButton';


jest.mock('../../components/DownloadIcon', () => () => <svg data-testid="download-icon" />);
jest.mock('@material-ui/core/Popper', () => (props) => {
  if (typeof props.children === 'function') {
    return props.children({
      placement: 'bottom',
      open: true,
      TransitionProps: { timeout: 0 },
      popperRef: { current: null },
    });
  }
  return props.children;
});
jest.mock('../../components/DownloadMenu', () => () => <div data-testid="mock-download-menu" />);
jest.mock('@material-ui/core/Portal', () => ({ children }) => children);


describe('DownloadFacilitiesButton component', () => {
  const expectedTooltipText =
  'Downloads are supported for searches resulting in 1000 production locations or less. Log in to download this dataset.';
  const handleDownload = jest.fn();
  const defaultProps = {
    disabled: false,
    setLoginRequiredDialogIsOpen: false,
    allowLargeDownloads: false,
    isEmbedded: true,
    handleDownload: handleDownload,
  };

  const createMockStore = (customState = {}) => {
    const initialState = {
      auth: {
        user: {
          user: {
            allowed_records_number: 1000,
            isAnon: false,
          },
        },
      },
      logDownload: { error: null },
      embeddedMap: { embed: true },
      ...customState,
    };
    return createStore((_) => initialState);
  };

  const theme = createMuiTheme({
    palette: {
          action: {
            main: 'rgb(255, 207, 63)',
            dark: 'rgb(178, 144, 44)',
          },
          getContrastText: jest.fn(() => 'rgb(255, 207, 63)'),
      },
    });


  const renderComponent = (props = {}, customState = {}) => {
    const container = document.createElement('div');
    document.body.appendChild(container);

    const result = render(
      <MuiThemeProvider theme={theme}>
        <Provider store={createMockStore(customState)}>
          <DownloadFacilitiesButton {...defaultProps} {...props} />
        </Provider>,
      </MuiThemeProvider>,
      { container }
    );

    return {
      ...result,
      cleanup: () => document.body.removeChild(container),
    };
  };

  beforeEach(() => jest.clearAllMocks());

  test('should render the DownloadFacilitiesButton', () => {
    const { getByText, getByTestId } = renderComponent();

    expect(getByTestId('download-icon')).toBeInTheDocument();
    expect(getByText('Download')).toBeInTheDocument();
  });

  test('the menu should appear when button is clicked', async() => {
    const { getByRole, getByTestId } = renderComponent();
    const button = getByRole('button', { name: 'Download' });

    fireEvent.click(button);

    expect(await getByTestId("mock-download-menu")).toBeInTheDocument();
  });

  test('should show tooltip if allowLargeDownloads is false', async () => {
    const { getByRole } = renderComponent({ allowLargeDownloads: false });
    const button = getByRole('button', { name: 'Download' });

    expect(button).toBeEnabled();

    fireEvent.mouseOver(button);

    await waitFor(() =>
      expect(screen.getByText(expectedTooltipText)).toBeInTheDocument()
    );
  });

  test('should not show tooltip if allowLargeDownloads is true', async () => {
    const { getByRole } = renderComponent({ allowLargeDownloads: true });
    const button = getByRole('button', { name: 'Download' });

    expect(button).toBeEnabled();

    fireEvent.mouseOver(button);

    await waitFor(() =>
      expect(screen.queryByText(expectedTooltipText)).not.toBeInTheDocument()
    );
  });

  test('should show default allowed_records_number in the tooltip when button is disabled', async () => {
    const { getByRole } = renderComponent({ allowLargeDownloads: false, disabled: true});

    const button = getByRole('button', { name: 'Download' });
    expect(button).toBeDisabled();

    fireEvent.mouseOver(button);

    await waitFor(() =>
      expect(screen.getByText(expectedTooltipText)).toBeInTheDocument()
    );
  });

  test('should show correct text with custom allowed_records_number in the tooltip', async () => {
    const props = {
      allowLargeDownloads: false,
      disabled: true ,
    };
    const customState = {
      auth: {
        user: {
          user: {
            allowed_records_number: 555,
            isAnon: true,
          },
        },
      },
    };
    const { getByRole } = renderComponent(props, customState);
    const expectedText =
    'Downloads are supported for searches resulting in 555 production locations or less. Log in to download this dataset.';

    const button = getByRole('button', { name: 'Download' });
    expect(button).toBeDisabled();

    fireEvent.mouseOver(button);

    await waitFor(() =>
      expect(screen.getByText(expectedText)).toBeInTheDocument()
    );
  });
});
