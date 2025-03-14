import React, { Component } from 'react';
import { connect } from 'react-redux';
import { withRouter } from 'react-router';
import { bool, func, number, shape, string } from 'prop-types';
import get from 'lodash/get';
import { CircularProgress } from '@material-ui/core';

import { setFiltersFromQueryString } from '../actions/filters';

import { fetchFacilities, resetFacilities } from '../actions/facilities';

import { filtersPropType } from '../util/propTypes';

import { createQueryStringFromSearchFilters } from '../util/util';

import { facilitiesRoute } from '../util/constants';

const getCleanPathname = pathname => {
    if (pathname && pathname[pathname.length - 1] === '/') {
        return pathname.slice(0, pathname.length - 1);
    }
    return pathname;
};

export default function withQueryStringSync(WrappedComponent) {
    const componentWithWrapper = class extends Component {
        state = { finishedInitialHydrate: false };

        componentDidMount() {
            const {
                history: {
                    replace,
                    location: { search, pathname },
                },
                match: { path },
                filters,
                hydrateFiltersFromQueryString,
                fetchFacilitiesForCurrentSearch,
                vectorTileFeatureIsActive,
                embeddedMap: { embed },
            } = this.props;

            if (vectorTileFeatureIsActive || search) {
                hydrateFiltersFromQueryString(search);

                // This check returns null when the component mounts on the facility details route
                // with a path like /facilities/hello-world?name=facility to stop all facilities
                // from loading in the background and superseding single facility for the details
                // page.
                //
                // In that case, `path` will be `/facilities` and `pathname` will be
                // `/facilities/hello-world`. In other cases -- `/` and `/facilities` -- these paths
                // will match.
                //
                // Furthermore, limits fetching facilities to the facilities route.
                const cleanPathname = getCleanPathname(pathname);
                const isFacilitiesRoute = path.includes(facilitiesRoute);
                const fetchFacilitiesOnMount =
                    cleanPathname === path && isFacilitiesRoute;

                if (fetchFacilitiesOnMount) {
                    fetchFacilitiesForCurrentSearch();
                }

                this.setState({ finishedInitialHydrate: true });
            } else if (!search) {
                this.setState({ finishedInitialHydrate: true });
            } else {
                replace(
                    `?${createQueryStringFromSearchFilters(filters, embed)}`,
                );
            }
        }

        componentDidUpdate({
            resetButtonClickCount: prevResetButtonClickCount,
            vectorTileFeatureIsActive: prevVectorTileFeatureIsActive,
        }) {
            const {
                filters,
                history: {
                    replace,
                    location: { search, pathname },
                },
                resetButtonClickCount,
                hydrateFiltersFromQueryString,
                vectorTileFeatureIsActive,
                embeddedMap: { embed },
                fetchFacilitiesForCurrentSearch,
            } = this.props;

            const newQueryString = `?${createQueryStringFromSearchFilters(
                filters,
                embed,
            )}`;

            if (
                resetButtonClickCount !== prevResetButtonClickCount &&
                vectorTileFeatureIsActive
            ) {
                replace(newQueryString);
                const fetchFacilitiesOnQSChange = true;
                return hydrateFiltersFromQueryString(
                    newQueryString,
                    fetchFacilitiesOnQSChange,
                );
            }

            if (!prevVectorTileFeatureIsActive && vectorTileFeatureIsActive) {
                fetchFacilitiesForCurrentSearch();
            }

            if (search === newQueryString) {
                return null;
            }

            if (!search && newQueryString.length === 1) {
                return null;
            }

            if (pathname !== facilitiesRoute) {
                return null;
            }

            return replace(newQueryString);
        }

        render() {
            return this.state.finishedInitialHydrate ? (
                <WrappedComponent {...this.props} />
            ) : (
                <CircularProgress />
            );
        }
    };

    componentWithWrapper.propTypes = {
        filters: filtersPropType.isRequired,
        hydrateFiltersFromQueryString: func.isRequired,
        clearFacilities: func.isRequired,
        history: shape({
            replace: func.isRequired,
            location: shape({
                search: string.isRequired,
            }),
        }).isRequired,
        resetButtonClickCount: number.isRequired,
        vectorTileFeatureIsActive: bool.isRequired,
        fetchingFeatureFlags: bool.isRequired,
    };

    function mapStateToProps({
        filters,
        ui: {
            facilitiesSidebarTabSearch: { resetButtonClickCount },
        },
        featureFlags: { flags, fetching: fetchingFeatureFlags },
        embeddedMap,
    }) {
        return {
            filters,
            resetButtonClickCount,
            vectorTileFeatureIsActive: get(flags, 'vector_tile', false),
            fetchingFeatureFlags,
            embeddedMap,
        };
    }

    function mapDispatchToProps(dispatch, { history: { push } }) {
        return {
            hydrateFiltersFromQueryString: qs => {
                dispatch(setFiltersFromQueryString(qs));
            },
            fetchFacilitiesForCurrentSearch: () =>
                dispatch(
                    fetchFacilities({
                        ...push,
                        activateFacilitiesTab: false,
                    }),
                ),
            clearFacilities: () => dispatch(resetFacilities()),
        };
    }

    return withRouter(
        connect(mapStateToProps, mapDispatchToProps)(componentWithWrapper),
    );
}
