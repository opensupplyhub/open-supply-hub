import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '@material-ui/core';
import Tooltip from '@material-ui/core/Tooltip';
import { withStyles } from '@material-ui/core/styles';

jest.mock('@material-ui/core/Popper', () => {
  return ({ children }) => children;
});

jest.mock('@material-ui/core/Portal', () => {
  return ({ children }) => children;
});

afterEach(() => {
  jest.resetAllMocks();
});

const StyledTooltip = withStyles({
  tooltip: {
    color: 'rgba(0, 0, 0, 0.8)',
    fontSize: '0.875rem',
    backgroundColor: 'white',
    border: 'solid rgba(0, 0, 0, 0.25)',
    borderRadius: '10px',
    padding: '10px',
    lineHeight: '1',
  },
})(Tooltip);

const TestComponent = () => (
  <StyledTooltip
    title="Test"
    placement="right"
    id="submit_tooltip"
  >
    <div style={{ display: 'inline-block' }}>
      <Button
        disabled
        text="SUBMIT"
        variant="contained"
        disableRipple
        onClick={() => {}}
      >
        SUBMIT
      </Button>
    </div>
  </StyledTooltip>
);

test('shows tooltip on hover', async () => {
  const {getByRole} = render(<TestComponent />);
  const button = getByRole('button', { name:'SUBMIT' });

  expect(button).toHaveTextContent('SUBMIT');
  expect(button).toBeDisabled();

  const noTooltipElement = document.querySelector('[title="Test"]');

  expect(noTooltipElement).toBeInTheDocument();
  fireEvent.mouseOver(button);

  const tooltip = document.querySelector('[aria-describedby="submit_tooltip"]');

  expect(tooltip).toBeInTheDocument();
  fireEvent.mouseOut(button);

  const noTooltipElementAfter = document.querySelector('[title="Test"]');

  expect(noTooltipElementAfter).toBeInTheDocument();
});
