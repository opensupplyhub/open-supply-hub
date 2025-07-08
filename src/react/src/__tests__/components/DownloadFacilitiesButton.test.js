import React from 'react';
import { render, fireEvent, waitFor, screen } from '@testing-library/react';
import { MuiThemeProvider, createMuiTheme } from '@material-ui/core/styles';
import { Provider } from 'react-redux';
import { createStore } from 'redux';
import DownloadFacilitiesButton from '../../components/DownloadFacilitiesButton';
import {
    PRIVATE_INSTANCE,
} from '../../util/constants';


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
  const handleDownload = jest.fn();
  const defaultProps = {
    disabled: false,
    upgrade: false,
    setLoginRequiredDialogIsOpen: false,
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
      embeddedMap: { embed: false },
      downloadLimit: {
        checkout: { checkoutUrl: "test", error: null },
      },
      featureFlags: { flags: [] },
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

  test('should show tooltip when embed mode is enabled', async () => {
    const expectedTooltipText = "Downloads are supported for searches resulting in 10000 production locations or less.";
    const props = {
      disabled: false,
      userAllowedRecords: 5000,
    };
    const customState = {
      auth: {
        user: {
          user: {
            isAnon: false,
          },
        },
      },
      embeddedMap: { embed: true },
    };
    const { getByRole } = renderComponent(props, customState);
    const button = getByRole('button', { name: 'Download' });

    expect(button).toBeEnabled();
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
            isAnon: false,
          },
        },
      },
      embeddedMap: { embed: false },
    };
    const expectedTooltipText = "Registered users can download up to 5000 production locations annually for free. This account has 1000 production locations available to download. Additional downloads are available for purchase.";

    const { getByRole } = renderComponent(props, customState);

    const button = getByRole('button', { name: 'Download' });
    expect(button).toBeDisabled();

    fireEvent.mouseOver(button);

    await waitFor(() =>
      expect(screen.getByText(expectedTooltipText)).toBeInTheDocument()
    );
  });

  test('should show correct tooltip in case a user is out of downloads', async () => {
    const props = {
      disabled: false,
      userAllowedRecords: 0,
      upgrade: true,
    };
    const customState = {
      auth: {
        user: {
          user: {
            isAnon: false,
            allowed_records_number: 0
          },
        },
      },
      embeddedMap: { embed: false },
    };
    const expectedTooltipText = "You've reached your annual download limit. Purchase additional downloads for immediate access.";

    const { getByRole } = renderComponent(props, customState);

    const button = getByRole('button', { name: 'Purchase More Downloads' });
    fireEvent.mouseOver(button);

    await waitFor(() =>
      expect(screen.getByText(expectedTooltipText)).toBeInTheDocument()
    );
  });

  test('show correct tooltip when user is within limit but search results exceed available records', async () => {
    const props = {
      disabled: true,
      userAllowedRecords: 1000,
      upgrade: true,
      isEmbedded: false,
    };
    const customState = {
      auth: {
        user: {
          user: {
            isAnon: false,
            allowed_records_number: 1000,
          },
        },
      },
      embeddedMap: { embed: false },
    };
    const expectedTooltipText = "Registered users can download up to 5000 production locations annually for free. This account has 1000 production locations available to download. Purchase additional downloads for immediate access.";
    const { getByRole } = renderComponent(props, customState);

    const button = getByRole('button', { name: 'Purchase More Downloads' });
    expect(button).toBeDisabled();

    fireEvent.mouseOver(button);

    await waitFor(() =>
      expect(screen.getByText(expectedTooltipText)).toBeInTheDocument()
    );
  });

  test('show correct tooltip when user is non-registered', async () => {
    const props = {
      disabled: true,
      userAllowedRecords: 1000,
      upgrade: true,
      isEmbedded: false,
    };
    const customState = {
      auth: {
        user: {
          user: {
            isAnon: true,
            allowed_records_number: 1000,
          },
        },
      },
      embeddedMap: { embed: false },
    };
    const expectedTooltipText = "Log in or sign up to download this dataset.";
    const { getByRole } = renderComponent(props, customState);

    const button = getByRole('button', { name: 'Download' });
    expect(button).toBeDisabled();

    fireEvent.mouseOver(button);

    await waitFor(() =>
      expect(screen.getByText(expectedTooltipText)).toBeInTheDocument()
    );
  });

  test('show correct tooltip when turned on PRIVATE_INSTANCE switch', async () => {
    const props = {
      disabled: true,
      userAllowedRecords: 10000,
      upgrade: true,
      isEmbedded: false,
    };
    const customState = {
      auth: {
        user: {
          user: {
            isAnon: true,
            allowed_records_number: 10000,
          },
        },
      },
      embeddedMap: { embed: false },
      featureFlags:  { flags:
          {
            "block_location_downloads": false,
            "claim_a_facility": true,
            "disable_list_uploading": false,
            "embedded_map": true,
            "extended_profile": true,
            "private_instance": true,
            "report_a_facility": true,
            "show_additional_identifiers": false,
            "vector_tile": true,
          },
        },
    };
    const expectedTooltipText = `Downloads are supported for searches resulting in 10000 production locations or less. Log in or sign up to download this dataset.`;
    const { getByRole } = renderComponent(props, customState);

    const button = getByRole('button', { name: 'Download' });
    expect(button).toBeDisabled();

    fireEvent.mouseOver(button);

    await waitFor(() =>
      expect(screen.getByText(expectedTooltipText)).toBeInTheDocument()
    );
  });
});
