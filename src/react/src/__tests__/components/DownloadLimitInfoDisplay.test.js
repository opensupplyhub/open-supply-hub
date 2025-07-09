import React from 'react';
import { Router } from 'react-router-dom';
import { screen } from '@testing-library/react';

import FilterSidebar from '../../components/FilterSidebar';
import renderWithProviders from '../../util/testUtils/renderWithProviders';

describe('DownloadLimitInfo display logic', () => {
    const renderComponent = (props) => {
        // const preloadedState = {
        //     claimFacilityDashboard: {
        //         detail: {
        //             data: null,
        //             fetching: false,
        //             error: null,
        //             ...detailOverride,
        //         },
        //         note: {
        //             note: '',
        //             fetching: false,
        //             error: null,
        //         },
        //         statusControls: {
        //             fetching: false,
        //             error: null,
        //         },
        //     },
        // };

        return renderWithProviders(
            <Router>
                <FilterSidebar {...props}/>
            </Router>,
            // { preloadedState }
        );
    };

        test('should show DownloadLimitInfo when user is not anonymous and facilities count exceeds allowed records', () => {
          const props = {
            user: {
              isAnon: false,
              allowed_records_number: 500,
            },
            facilitiesCount: 1000,
          };
    
          renderComponent(props);
    
          expect(screen.getByTestId('download-limit-info')).toBeInTheDocument();
        });
    
        // test('should not show DownloadLimitInfo when user is anonymous', () => {
        //   const props = {
        //     user: {
        //       isAnon: true,
        //       allowed_records_number: 500,
        //     },
        //     facilitiesCount: 1000,
        //   };
    
        //   renderComponent(props);
    
        //   expect(screen.queryByTestId('download-limit-info')).not.toBeInTheDocument();
        // });
    
        // test('should not show DownloadLimitInfo when facilities count is within allowed records', () => {
        //   const props = {
        //     user: {
        //       isAnon: false,
        //       allowed_records_number: 1000,
        //     },
        //     facilitiesCount: 500,
        //   };
    
        //   renderComponent(props);
    
        //   expect(screen.queryByTestId('download-limit-info')).not.toBeInTheDocument();
        // });
    
        // test('should not show DownloadLimitInfo when facilities count equals allowed records', () => {
        //   const props = {
        //     user: {
        //       isAnon: false,
        //       allowed_records_number: 1000,
        //     },
        //     facilitiesCount: 1000,
        //   };
    
        //   renderComponent(props);
    
        //   expect(screen.queryByTestId('download-limit-info')).not.toBeInTheDocument();
        // });
    
        // test('should not show DownloadLimitInfo when facilities count is 0', () => {
        //   const props = {
        //     user: {
        //       isAnon: false,
        //       allowed_records_number: 500,
        //     },
        //     facilitiesCount: 0,
        //   };
    
        //   renderComponent(props);
    
        //   expect(screen.queryByTestId('download-limit-info')).not.toBeInTheDocument();
        // });
    
        // test('should show DownloadLimitInfo when user is not anonymous, facilities count exceeds allowed records, and user has very low allowed records', () => {
        //   const props = {
        //     user: {
        //       isAnon: false,
        //       allowed_records_number: 10,
        //     },
        //     facilitiesCount: 100,
        //   };
    
        //   renderComponent(props);
    
        //   expect(screen.getByTestId('download-limit-info')).toBeInTheDocument();
        // });
    
        // test('should show DownloadLimitInfo when user is not anonymous, facilities count exceeds allowed records, and user has high allowed records', () => {
        //   const props = {
        //     user: {
        //       isAnon: false,
        //       allowed_records_number: 10000,
        //     },
        //     facilitiesCount: 15000,
        //   };
    
        //   renderComponent(props);
    
        //   expect(screen.getByTestId('download-limit-info')).toBeInTheDocument();
        // });
    
    //   describe('ShowOnly component integration', () => {
    //     test('should render ShowOnly with correct when condition', () => {
    //       const props = {
    //         user: {
    //           isAnon: false,
    //           allowed_records_number: 500,
    //         },
    //         facilitiesCount: 1000,
    //       };
    
    //       renderComponent(props);
    
    //       // The ShowOnly component should render its children when the condition is true
    //       expect(screen.getByTestId('download-limit-info')).toBeInTheDocument();
    //     });
    
    //     test('should not render ShowOnly children when condition is false', () => {
    //       const props = {
    //         user: {
    //           isAnon: true,
    //           allowed_records_number: 500,
    //         },
    //         facilitiesCount: 1000,
    //       };
    
    //       renderComponent(props);
    
    //       // The ShowOnly component should not render its children when the condition is false
    //       expect(screen.queryByTestId('download-limit-info')).not.toBeInTheDocument();
    //     });
    //   });
    
    //   describe('FeatureFlag component integration', () => {
    //     test('should render alternative component when PRIVATE_INSTANCE flag is active', () => {
    //       const props = {
    //         user: {
    //           isAnon: false,
    //           allowed_records_number: 500,
    //         },
    //         facilitiesCount: 1000,
    //       };
    
    //       renderComponent(props);
    
    //       // The FeatureFlag component should render the alternative (DownloadLimitInfo) 
    //       // when the PRIVATE_INSTANCE flag is active
    //       expect(screen.getByTestId('download-limit-info')).toBeInTheDocument();
    //     });
    //   });
});

