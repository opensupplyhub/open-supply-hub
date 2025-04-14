import React from 'react';
import { render, fireEvent, screen } from '@testing-library/react';
import DownloadMenu from '../../components/DownloadMenu';

jest.mock('@material-ui/core/Menu', () =>  ({ children, open, anchorEl, onClose, ...rest }) => {
    if (!open) return null;
    return (
      <div role="menu" data-testid="mock-menu" {...rest}>
        {children}
        <button type="button" onClick={onClose} data-testid="menu-close-button">Close Menu</button>
      </div>
    );
  }
);

jest.mock('@material-ui/core/MenuItem', () => ({ onClick, ...props }) => (
    <button
     type="button"
      role="menuitem"
      onClick={onClick}
      onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && onClick?.(e)}
      tabIndex={0}
      {...props}
    />
  )
);

describe('DownloadMenu component', () => {
  const onClose = jest.fn();
  const onSelectFormat = jest.fn();
  const anchorEl = document.createElement('div');

  const renderComponent = () =>
    render(
      <DownloadMenu
        anchorEl={anchorEl}
        onClose={onClose}
        onSelectFormat={onSelectFormat}
      />
    );

  test('should show menuitems CSV and Excel when open', () => {
    renderComponent();

    expect(screen.getByRole('menu')).toBeInTheDocument();
    expect(screen.getByRole('menuitem', { name: /csv/i })).toBeInTheDocument();
    expect(screen.getByRole('menuitem', { name: /excel/i })).toBeInTheDocument();
  });

  test('clicking on CSV should call onSelectFormat with "csv"', () => {
    renderComponent();

    fireEvent.click(screen.getByRole('menuitem', { name: /csv/i }));
    expect(onSelectFormat).toHaveBeenCalledWith('csv');
  });

  test('clicking on Excel should call onSelectFormat with "xlsx"', () => {
    renderComponent();

    fireEvent.click(screen.getByRole('menuitem', { name: /excel/i }));
    expect(onSelectFormat).toHaveBeenCalledWith('xlsx');
  });

  test('calls onClose when menu is closed', () => {
    const mockOnClose = jest.fn();

    render(
      <DownloadMenu
        anchorEl={document.createElement('div')}
        onClose={mockOnClose}
        onSelectFormat={jest.fn()}
      />
    );

    const closeBtn = screen.getByTestId('menu-close-button');
    fireEvent.click(closeBtn);

    expect(mockOnClose).toHaveBeenCalled();
  });

});
