import React from 'react';

import FilterSidebarHeader from '../../components/FilterSidebarHeader';
import renderWithProviders from '../../util/testUtils/renderWithProviders';

// Mock the ResultsSortDropdown component.
jest.mock('../../components/ResultsSortDropdown', () => () => (
    <div>Mocked ResultsSortDropdown</div>
));

// Mock the DownloadLimitInfo component.
jest.mock('../../components/DownloadLimitInfo', () => () => (
    <div data-testid="mock-download-limit-info">Mocked DownloadLimitInfo</div>
));

describe('FilterSidebarHeader component', () => {
    const renderComponent = ({ preloadedState = {}, props = {} } = {}) =>
        renderWithProviders(<FilterSidebarHeader {...props} />, {
            preloadedState,
        });

    test('renders component with set params', () => {
        const { getByText } = renderComponent({
            preloadedState: {
                facilities: {
                    facilities: { data: { count: 10 } },
                },
                auth: {
                    user: {
                        user: {
                            isAnon: false,
                            allowed_records_number: 5000,
                        },
                    },
                },
                embeddedMap: {
                    embed: false,
                },
            },
            props: {
                multiLine: false,
            },
        });
        expect(getByText('10 results')).toBeInTheDocument();
    });

    describe('DownloadLimitInfo display logic', () => {
        test('displays DownloadLimitInfo when user is logged in and locations count exceeds limit', () => {
            const { getByTestId } = renderComponent({
                preloadedState: {
                    facilities: {
                        facilities: { data: { count: 6000 } }, // Exceeds 5000 limit.
                    },
                    auth: {
                        user: {
                            user: {
                                isAnon: false,
                                allowed_records_number: 5000,
                            },
                        },
                    },
                    embeddedMap: {
                        embed: false,
                    },
                },
                props: {
                    multiLine: false,
                },
            });
            expect(getByTestId('mock-download-limit-info')).toBeInTheDocument();
        });

        test('does not display DownloadLimitInfo when user is anonymous', () => {
            const { queryByTestId } = renderComponent({
                preloadedState: {
                    facilities: {
                        facilities: { data: { count: 6000 } }, // Exceeds limit.
                    },
                    auth: {
                        user: {
                            user: {
                                isAnon: true, // Anonymous user.
                                allowed_records_number: 5000,
                            },
                        },
                    },
                    embeddedMap: {
                        embed: false,
                    },
                },
                props: {
                    multiLine: false,
                },
            });
            expect(queryByTestId('mock-download-limit-info')).not.toBeInTheDocument();
        });

        test('does not display DownloadLimitInfo when locations count is within limit', () => {
            const { queryByTestId } = renderComponent({
                preloadedState: {
                    facilities: {
                        facilities: { data: { count: 3000 } }, // Within 5000 limit.
                    },
                    auth: {
                        user: {
                            user: {
                                isAnon: false,
                                allowed_records_number: 5000,
                            },
                        },
                    },
                    embeddedMap: {
                        embed: false,
                    },
                },
                props: {
                    multiLine: false,
                },
            });
            expect(queryByTestId('mock-download-limit-info')).not.toBeInTheDocument();
        });

        test('does not display DownloadLimitInfo when in embed mode', () => {
            const { queryByTestId } = renderComponent({
                preloadedState: {
                    facilities: {
                        facilities: { data: { count: 6000 } }, // Exceeds limit.
                    },
                    auth: {
                        user: {
                            user: {
                                isAnon: false,
                                allowed_records_number: 5000,
                            },
                        },
                    },
                    embeddedMap: {
                        embed: true, // Embed mode.
                    },
                },
                props: {
                    multiLine: false,
                },
            });
            expect(queryByTestId('mock-download-limit-info')).not.toBeInTheDocument();
        });

        test('does not display DownloadLimitInfo when user has higher download limit', () => {
            const { queryByTestId } = renderComponent({
                preloadedState: {
                    facilities: {
                        facilities: { data: { count: 6000 } },
                    },
                    auth: {
                        user: {
                            user: {
                                isAnon: false,
                                allowed_records_number: 10000, // Higher limit.
                            },
                        },
                    },
                    embeddedMap: {
                        embed: false,
                    },
                },
                props: {
                    multiLine: false,
                },
            });
            expect(queryByTestId('mock-download-limit-info')).not.toBeInTheDocument();
        });

        test('does not display DownloadLimitInfo when private_instance flag is active', () => {
            const { queryByTestId } = renderComponent({
                preloadedState: {
                    facilities: {
                        facilities: { data: { count: 6000 } }, // Exceeds limit.
                    },
                    auth: {
                        user: {
                            user: {
                                isAnon: false,
                                allowed_records_number: 5000,
                            },
                        },
                    },
                    embeddedMap: {
                        embed: false,
                    },
                    featureFlags: {
                        flags: {
                            private_instance: true, // Private instance flag active.
                        },
                    },
                },
                props: {
                    multiLine: false,
                },
            });
            expect(queryByTestId('mock-download-limit-info')).not.toBeInTheDocument();
        });

        test('displays DownloadLimitInfo when private_instance flag is not active', () => {
            const { getByTestId } = renderComponent({
                preloadedState: {
                    facilities: {
                        facilities: { data: { count: 6000 } }, // Exceeds limit.
                    },
                    auth: {
                        user: {
                            user: {
                                isAnon: false,
                                allowed_records_number: 5000,
                            },
                        },
                    },
                    embeddedMap: {
                        embed: false,
                    },
                    featureFlags: {
                        flags: {
                            private_instance: false, // Private instance flag not active.
                        },
                    },
                },
                props: {
                    multiLine: false,
                },
            });
            expect(getByTestId('mock-download-limit-info')).toBeInTheDocument();
        });
    });
});

