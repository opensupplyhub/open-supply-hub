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
  'Downloads are supported for searches resulting in 5000 production locations or less.';
  const handleDownload = jest.fn();
  const defaultProps = {
    disabled: false,
    upgrade: false,
    setLoginRequiredDialogIsOpen: false,
    isEmbedded: true,
    handleDownload,
    userAllowedRecords: 5000,
  };

  const createMockStore = (customState = {}) => {
    const initialState = {
      auth: {
        user: {
          user: {
            isAnon: false,
          },
        },
      },
      logDownload: { error: null },
      embeddedMap: { embed: true },
      downloadLimit: {
        checkout: { checkoutUrl: "test", error: null },
      },
      ...customState,
    };
    return createStore(() => initialState);
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

  test('should show tooltip', async () => {
    const { getByRole } = renderComponent();
    const button = getByRole('button', { name: 'Download' });

    expect(button).toBeEnabled();

    fireEvent.mouseOver(button);

    await waitFor(() =>
      expect(screen.getByText(expectedTooltipText)).toBeInTheDocument()
    );
  });

  test('should show default userAllowedRecords in the tooltip when button is disabled', async () => {
    const { getByRole } = renderComponent({ disabled: true});

    const button = getByRole('button', { name: 'Download' });
    expect(button).toBeDisabled();

    fireEvent.mouseOver(button);

    await waitFor(() =>
      expect(screen.getByText(expectedTooltipText)).toBeInTheDocument()
    );
  });

  test('should show correct tooltip in case has available downloads', async () => {
    const props = {
      disabled: true,
      userAllowedRecords: 1000,
    };
    const customState = {
      auth: {
        user: {
          user: {
            isAnon: true,
          },
        },
      },
    };
    const { getByRole } = renderComponent(props, customState);
    const expectedText =
    `Registered users can download up to ${FACILITIES_DOWNLOAD_LIMIT} production
                locations annually for free. This account has ${userAllowedRecords} production locations
                available to download. Additional downloads are available for purchase.`;

    const button = getByRole('button', { name: 'Download' });
    expect(button).toBeDisabled();

    fireEvent.mouseOver(button);

    await waitFor(() =>
      expect(screen.getByText(expectedText)).toBeInTheDocument()
    );
  });
  test('should show correct tooltip in case a user is out of downloads', async () => {
    const props = {
      disabled: true,
      userAllowedRecords: 0,
    };
    const customState = {
      auth: {
        user: {
          user: {
            isAnon: true,
          },
        },
      },
    };
    const { getByRole } = renderComponent(props, customState);
    const expectedText =
     "You've reached your annual download limit. Purchase additional downloads for immediate access.";

    const button = getByRole('button', { name: 'Download' });
    expect(button).toBeDisabled();

    fireEvent.mouseOver(button);

    await waitFor(() =>
      expect(screen.getByText(expectedText)).toBeInTheDocument()
    );
  });
  test('should show correct tooltip in case user’s account has not met it’s limit but the result searches yield more records than available', async () => {
    const props = {
      disabled: true,
      userAllowedRecords: 1000,
    };
    const customState = {
      auth: {
        user: {
          user: {
            isAnon: false,
          },
        },
      },
    };
    const { getByRole } = renderComponent(props, customState);
    const expectedText =
    `Registered users can download up to 5000
                production locations annually for free. This account has 1000 production
                locations available to download. Purchase additional downloads for immediate access.`;

    const button = getByRole('button', { name: 'Download' });
    expect(button).toBeDisabled();

    fireEvent.mouseOver(button);

    await waitFor(() =>
      expect(screen.getByText(expectedText)).toBeInTheDocument()
    );
  });
});
