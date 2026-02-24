import React from 'react';
import Typography from '@material-ui/core/Typography';
import { Link } from 'react-router-dom';

import {
    makeFacilityDetailLink,
    makeFacilityDetailLinkOnRedirect,
} from '../../../../util/util';

export default function getPrimaryText({
    report,
    isPending,
    isClosed,
    newOsId,
    classes,
    useProductionLocationPage,
    search,
    clearFacility,
}) {
    if (isPending) {
        return (
            <Typography className={classes.text} variant="subheading">
                This facility may be {report.closure_state.toLowerCase()}
            </Typography>
        );
    }

    if (isClosed && !!newOsId) {
        const movedToPathname = useProductionLocationPage
            ? makeFacilityDetailLinkOnRedirect(
                  newOsId,
                  search,
                  useProductionLocationPage,
              )
            : makeFacilityDetailLink(newOsId);
        return (
            <Typography className={classes.text} variant="subheading">
                This facility has moved to{' '}
                <Link
                    to={{
                        pathname: movedToPathname,
                        state: {
                            panMapToFacilityDetails: true,
                        },
                    }}
                    className={classes.text}
                    onClick={() => clearFacility()}
                >
                    {newOsId}
                </Link>
            </Typography>
        );
    }

    if (isClosed) {
        return (
            <Typography className={classes.text} variant="subheading">
                This facility is closed
            </Typography>
        );
    }

    return null;
}
