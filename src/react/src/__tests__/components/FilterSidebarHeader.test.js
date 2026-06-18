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

const createFacilitiesState = (
    count,
    hasAppliedFilters = false,
    excludedFromDownloadCount = 0,
) => ({
    facilities: {
        data: {
            count,
            excluded_from_download_count: excludedFromDownloadCount,
        },
        hasAppliedFilters,
    },
});

describe('FilterSidebarHeader component', () => {
    const renderComponent = ({ preloadedState = {}, props = {} } = {}) =>
        renderWithProviders(<FilterSidebarHeader {...props} />, {
            preloadedState,
        });

    test('renders component with set params', () => {
        const { getByText } = renderComponent({
            preloadedState: {
                facilities: {
                    ...createFacilitiesState(10),
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

    test('appends union-linked suffix when results include union data', () => {
        const { getByText } = renderComponent({
            preloadedState: {
                facilities: {
                    ...createFacilitiesState(16, false, 15),
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
        expect(
            getByText(
                /16 results \(including 15 union-linked locations\)/,
            ),
        ).toBeInTheDocument();
    });

    test('uses singular location when one union-linked result', () => {
        const { getByText } = renderComponent({
            preloadedState: {
                facilities: {
                    ...createFacilitiesState(2, false, 1),
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
        expect(
            getByText(/2 results \(including 1 union-linked location\)/),
        ).toBeInTheDocument();
    });

    test('does not append union-linked suffix when none are excluded', () => {
        const { getByText, queryByText } = renderComponent({
            preloadedState: {
                facilities: {
                    ...createFacilitiesState(10, false, 0),
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
        expect(queryByText(/union-linked/)).not.toBeInTheDocument();
    });

    describe('DownloadLimitInfo display logic', () => {
        test('displays DownloadLimitInfo when user is logged in and locations count exceeds limit', () => {
            const { getByTestId } = renderComponent({
                preloadedState: {
                    facilities: {
                        ...createFacilitiesState(6000, true), // Exceeds 5000 limit.
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
                        ...createFacilitiesState(6000, true), // Exceeds limit.
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
                        ...createFacilitiesState(3000, true), // Within 5000 limit.
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
                        ...createFacilitiesState(6000, true), // Exceeds limit.
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
                        ...createFacilitiesState(6000, true),
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
                        ...createFacilitiesState(6000, true), // Exceeds limit.
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
                        ...createFacilitiesState(6000, true), // Exceeds limit.
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

        test('does not display DownloadLimitInfo when filters have not been applied', () => {
            const { queryByTestId } = renderComponent({
                preloadedState: {
                    facilities: {
                        ...createFacilitiesState(6000, false), // Exceeds limit.
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
            expect(
                queryByTestId('mock-download-limit-info'),
            ).not.toBeInTheDocument();
        });
    });
});

