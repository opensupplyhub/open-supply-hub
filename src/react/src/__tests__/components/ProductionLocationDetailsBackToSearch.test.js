import React from 'react';
import { fireEvent } from '@testing-library/react';
import ProductionLocationDetailsBackToSearch from '../../components/ProductionLocation/Sidebar/BackToSearch/BackToSearch';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import { setupStore } from '../../configureStore';

describe('ProductionLocationDetailsBackToSearch component', () => {
  const mockGoBack = jest.fn();
  const mockPush = jest.fn();

  const createHistory = (length = 2) => ({
    goBack: mockGoBack,
    push: mockPush,
    length,
  });

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders the back to search link and arrow icon', () => {
    const { getByTestId, getByText } = renderWithProviders(
      <ProductionLocationDetailsBackToSearch history={createHistory()} />,
    );

    const text = getByTestId('back-to-search-text');
    expect(text).toBeInTheDocument();
    expect(getByText('Back to search results')).toBeInTheDocument();

    const svg = getByTestId('back-to-search-arrow');
    expect(svg).toBeInTheDocument();

  });

  it('calls history.goBack when history has previous entries', () => {
    const { getByTestId } = renderWithProviders(
      <ProductionLocationDetailsBackToSearch history={createHistory(2)} />,
    );

    const button = getByTestId('back-to-search-button');
    fireEvent.click(button);

    expect(mockGoBack).toHaveBeenCalled();
    expect(mockPush).not.toHaveBeenCalled();
  });

  it('calls history.push with facilitiesRoute when there is no history', () => {
    const { getByTestId } = renderWithProviders(
      <ProductionLocationDetailsBackToSearch history={createHistory(1)} />,
    );

    const button = getByTestId('back-to-search-button');
    fireEvent.click(button);

    expect(mockPush).toHaveBeenCalledWith('/facilities');
    expect(mockGoBack).not.toHaveBeenCalled();
  });

  it('dispatches resetSingleFacility when clicked', () => {
    const reduxStore = setupStore({});
    const dispatchSpy = jest.spyOn(reduxStore, 'dispatch');

    const { getByTestId } = renderWithProviders(
      <ProductionLocationDetailsBackToSearch history={createHistory()} />,
      { reduxStore },
    );

    const button = getByTestId('back-to-search-button');
    fireEvent.click(button);

    expect(dispatchSpy).toHaveBeenCalledWith(
      expect.objectContaining({ type: 'RESET_SINGLE_FACILITY' }),
    );
  });
});
