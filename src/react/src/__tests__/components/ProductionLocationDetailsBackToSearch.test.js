import React from 'react';
import { fireEvent } from '@testing-library/react';
import ProductionLocationDetailsBackToSearch from '../../components/ProductionLocation/Sidebar/BackToSearch/BackToSearch';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import { setupStore } from '../../configureStore';

describe('ProductionLocationDetailsBackToSearch component', () => {
  const mockPush = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders the back to search link', () => {
    const { getByText } = renderWithProviders(
      <ProductionLocationDetailsBackToSearch
        history={{ push: mockPush }}
      />,
    );

    expect(getByText('Back to search results')).toBeInTheDocument();
  });

  it('renders a link pointing to the facilities route', () => {
    const { container } = renderWithProviders(
      <ProductionLocationDetailsBackToSearch
        history={{ push: mockPush }}
      />,
    );

    const link = container.querySelector('a');
    expect(link).toHaveAttribute('href', '/facilities');
  });

  it('renders the back arrow icon', () => {
    const { container } = renderWithProviders(
      <ProductionLocationDetailsBackToSearch
        history={{ push: mockPush }}
      />,
    );

    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();
  });

  it('dispatches resetSingleFacility when clicked', () => {
    const reduxStore = setupStore({});
    const dispatchSpy = jest.spyOn(reduxStore, 'dispatch');

    const { getByText } = renderWithProviders(
      <ProductionLocationDetailsBackToSearch
        history={{ push: mockPush }}
      />,
      { reduxStore },
    );

    fireEvent.click(getByText('Back to search results'));

    expect(dispatchSpy).toHaveBeenCalledWith(
      expect.objectContaining({ type: 'RESET_SINGLE_FACILITY' }),
    );
  });
});
