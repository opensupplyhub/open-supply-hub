import React from 'react';
import { render, fireEvent, waitFor, screen } from '@testing-library/react';
import DownloadFacilitiesButton from '../../components/DownloadFacilitiesButton';
import { Provider } from 'react-redux';
import { createStore } from 'redux';

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
jest.mock('@material-ui/core/Menu', () => {
  return ({ children, anchorEl, open, onClose, ...props }) => (
    <div role="menu" {...props}>
      {children}
    </div>
  );
});
jest.mock('@material-ui/core/MenuItem', () => {
  return ({ children, onClick, anchorEl, ...props }) => {
    const handleKeyDown = (event) => {
      if (event.key === 'Enter' || event.key === ' ') {
        onClick && onClick(event);
      }
    };

    return (
      <div
        role="menuitem"
        onClick={onClick}
        onKeyDown={handleKeyDown}
        tabIndex={0}
        {...props}
      >
        {children}
      </div>
    );
  };
});
jest.mock('@material-ui/core/Portal', () => ({ children }) => children);


describe('DownloadFacilitiesButton component', () => {
  const handleDownload = jest.fn();
  const defaultProps = {
    disabled: false,
    setLoginRequiredDialogIsOpen: false,
    allowLargeDownloads: true,
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
    return createStore((state) => initialState);
  };

  const renderComponent = (props = {}, customState = {}) => {
    const container = document.createElement('div');
    document.body.appendChild(container);

    const result = render(
      <Provider store={createMockStore(customState)}>
        <DownloadFacilitiesButton {...defaultProps} {...props} />
      </Provider>,
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
    const { getByRole } = renderComponent();
    const button = getByRole('button', { name: 'Download' });

    fireEvent.click(button);

    expect(await screen.findByRole('menu')).toBeInTheDocument();
  });

  test('should show menuitems CSV and Excel', async () => {
    const { getByRole } = renderComponent();
    const button = getByRole('button', { name: 'Download' });

    fireEvent.click(button);

    expect(await screen.findByRole('menuitem', { name: /csv/i })).toBeInTheDocument();
    expect(await screen.findByRole('menuitem', { name: /excel/i })).toBeInTheDocument();
  });

  test('should disable button when allowLargeDownloads is false', () => {
    const { getByRole } = renderComponent({ allowLargeDownloads: false });
    const button = getByRole('button', { name: 'Download' });

    expect(button).toBeEnabled();
  });

  test('should show default allowed_records_number in the tooltip when button is disabled', async () => {
    const { getByRole } = renderComponent({ allowLargeDownloads: false, disabled: true});
    const expectedText =
    'Downloads are supported for searches resulting in 1000 production locations or less. Log in to download this dataset.';

    const button = getByRole('button', { name: 'Download' });
    expect(button).toBeDisabled();

    fireEvent.mouseOver(button);

    await waitFor(() =>
      expect(screen.getByText(expectedText)).toBeInTheDocument()
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
