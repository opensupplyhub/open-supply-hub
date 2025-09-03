import React from 'react';
import { arrayOf, bool, node } from 'prop-types';
import { connect } from 'react-redux';

import { featureFlagPropType } from '../util/propTypes';

import {
    convertFeatureFlagsObjectToListOfActiveFlags,
    filterFlagsIfAppIsEmbeded,
} from '../util/util';

function FeatureFlag({
    flag,
    children,
    alternative,
    activeFeatureFlags,
    fetching,
    isSameContributor,
}) {
    if (fetching) {
        return null;
    }

    const shouldRenderChildren =
        isSameContributor || activeFeatureFlags.includes(flag);

    return shouldRenderChildren ? <>{children}</> : alternative;
}

FeatureFlag.defaultProps = {
    alternative: null,
    isSameContributor: false,
};

FeatureFlag.propTypes = {
    flag: featureFlagPropType.isRequired,
    children: node.isRequired,
    alternative: node,
    activeFeatureFlags: arrayOf(featureFlagPropType).isRequired,
    fetching: bool.isRequired,
    isSameContributor: bool,
};

function mapStateToProps({
    featureFlags: { fetching, flags },
    embeddedMap: { embed: isEmbeded },
}) {
    const activeFeatureFlags = convertFeatureFlagsObjectToListOfActiveFlags(
        flags,
    );
    return {
        activeFeatureFlags: filterFlagsIfAppIsEmbeded(
            activeFeatureFlags,
            isEmbeded,
        ),
        fetching,
    };
}

export default connect(mapStateToProps)(FeatureFlag);
