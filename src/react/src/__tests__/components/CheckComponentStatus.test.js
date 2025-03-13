import React from 'react';
import { render } from '@testing-library/react';
import { BrowserRouter as Router } from 'react-router-dom';

import {
  LoadingIndicator,
  AuthNotice,
  ErrorsList,} from '../../components/CheckComponentStatus';

describe('CheckComponentStatus components', () => {
  const expectedTitle = 'Expected title';

    it('renders LoadingIndicator with title', () => {
        const { getByText } = render(<LoadingIndicator title={expectedTitle} />);

        expect(getByText(expectedTitle)).toBeInTheDocument();
    });

    it('renders AuthNotice with title and text', () => {
      const text = 'Sign in to view your Open Supply Hub facility claims.';
      const { getByText } = render(
          <Router>
             <AuthNotice title={expectedTitle} />
          </Router>
      )
      expect(getByText(expectedTitle)).toBeInTheDocument();
      expect(getByText(text)).toBeInTheDocument();
    });

    it('renders ErrorsList with title and errors', () => {
      const errors =  [
       'This field is required!','The right must be greater than left.',
      ] ;
      const { getByText } = render(<ErrorsList title={expectedTitle} errors={errors}/>);

      expect(getByText(expectedTitle)).toBeInTheDocument();
      expect(getByText(errors[0])).toBeInTheDocument();
      expect(getByText(errors[1])).toBeInTheDocument();
    });

});
