import React from 'react';

import { GOOGLE_CLIENT_SIDE_API_KEY } from '../util/constants.facilitiesMap';

import { facilityPropType } from '../util/propTypes';

import { DEFAULT_COUNTRY_CODE } from '../util/constants';

const staticParams = 'zoom=18&size=320x200&maptype=satellite';
const apiKey = `key=${GOOGLE_CLIENT_SIDE_API_KEY}`;

const makeGoogleMapsStaticMapURL = ({ lat, lng }) =>
    `https:///maps.googleapis.com/maps/api/staticmap?center=${lat},${lng}&markers=icon:${window.location.origin}/images/static-selectedmarker.png%7C${lat},${lng}&region=${DEFAULT_COUNTRY_CODE}&${staticParams}&${apiKey}`;

function FacilityDetailsStaticMap({
    data: {
        geometry: {
            coordinates: [lng, lat],
        },
        properties: { name },
    },
    style = {},
}) {
    return (
        <img
            src={makeGoogleMapsStaticMapURL({
                lat,
                lng,
            })}
            alt={`Facility ${name} at latitude ${lat} and longitude ${lng}`}
            className="facility-detail_map"
            style={style}
        />
    );
}

FacilityDetailsStaticMap.propTypes = {
    data: facilityPropType.isRequired,
};

export default FacilityDetailsStaticMap;
