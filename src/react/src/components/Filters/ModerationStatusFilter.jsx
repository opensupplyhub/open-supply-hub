import React from 'react';
import { bool, string, func } from 'prop-types';
import { connect } from 'react-redux';
import { updateModerationStatusFilter } from '../../actions/filters';
import { moderationStatusOptionsPropType } from '../../util/propTypes';
import { MODERATION_STATUSES } from '../../util/constants';
import { createOptionsFromConstants } from '../../util/util';

import StyledSelect from './StyledSelect';

const MODERATION_STATUS = 'MODERATION_STATUS';
const MODERATION_STATUSES_OPTIONS = Object.freeze(
    createOptionsFromConstants(MODERATION_STATUSES),
);

const ModerationStatusFilter = ({
    updateStatus,
    moderationStatuses,
    isDisabled,
    className,
    origin,
}) => (
    <div className={className}>
        <StyledSelect
            label="Moderation Status"
            name={MODERATION_STATUS}
            options={MODERATION_STATUSES_OPTIONS}
            value={moderationStatuses}
            onChange={updateStatus}
            isDisabled={isDisabled}
            origin={origin}
        />
    </div>
);

ModerationStatusFilter.defaultProps = {
    isDisabled: false,
    className: 'form__field',
    origin: null,
};

ModerationStatusFilter.propTypes = {
    updateStatus: func.isRequired,
    moderationStatuses: moderationStatusOptionsPropType.isRequired,
    isDisabled: bool,
    className: string,
    origin: string,
};

const mapStateToProps = ({ filters: { moderationStatuses } }) => ({
    moderationStatuses,
});
const mapDispatchToProps = dispatch => ({
    updateStatus: value => dispatch(updateModerationStatusFilter(value)),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(ModerationStatusFilter);
