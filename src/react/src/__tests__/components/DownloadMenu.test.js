import React from 'react';
import { render, fireEvent, screen } from '@testing-library/react';
import DownloadMenu from '../../components/DownloadMenu';

jest.mock('@material-ui/core/Menu', () => {
  return ({ children, open, anchorEl, ...rest }) => {
    if (!open) return null;
    return (
      <div role="menu" data-testid="mock-menu" {...rest}>
        {children}
      </div>
    );
  };
});

jest.mock('@material-ui/core/MenuItem', () => {
  return ({ children, onClick, ...props }) => (
    <div
      role="menuitem"
      onClick={onClick}
      tabIndex={0}
      {...props}
    >
      {children}
    </div>
  );
});

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
});
