import React, { useState } from 'react';
import { arrayOf, bool, func, shape, string } from 'prop-types';
import { connect } from 'react-redux';
import Checkbox from '@material-ui/core/Checkbox';
import CircularProgress from '@material-ui/core/CircularProgress';
import Collapse from '@material-ui/core/Collapse';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import FormGroup from '@material-ui/core/FormGroup';
import Typography from '@material-ui/core/Typography';
import ExpandLess from '@material-ui/icons/ExpandLess';
import ExpandMore from '@material-ui/icons/ExpandMore';
import IconButton from '@material-ui/core/IconButton';
import { withStyles } from '@material-ui/core/styles';

import {
    setPartnerFieldGroupFilter,
    setPartnerFieldFilter,
} from '../../actions/filters';
import { fetchPartnerFieldGroupsIfNeeded } from '../../actions/partnerFieldGroups';
import { getPartnerGroupsForFilter } from '../../selectors/partnerFieldGroupsSelectors';

const styles = theme => ({
    root: {
        marginTop: theme.spacing.unit * 2,
        marginBottom: theme.spacing.unit,
    },
    label: {
        fontFamily: theme.typography.fontFamily,
        fontSize: '14px',
        fontWeight: 700,
        color: '#000',
        marginBottom: theme.spacing.unit,
    },
    groupRow: Object.freeze({
        display: 'flex',
        alignItems: 'center',
        cursor: 'pointer',
    }),
    groupLabel: {
        fontFamily: theme.typography.fontFamily,
        fontSize: '14px',
        fontWeight: 600,
        flex: 1,
    },
    partnerList: Object.freeze({
        paddingLeft: theme.spacing.unit * 4,
    }),
    partnerLabel: {
        fontFamily: theme.typography.fontFamily,
        fontSize: '13px',
    },
    loadingContainer: Object.freeze({
        display: 'flex',
        justifyContent: 'center',
        padding: theme.spacing.unit * 2,
    }),
});

const SpotlightDataPartnersFilter = ({
    classes,
    groups,
    fetching,
    selectedGroups,
    selectedPartnerFields,
    onGroupChange,
    onPartnerFieldChange,
    loadGroupsIfNeeded,
}) => {
    const [expandedGroups, setExpandedGroups] = useState({});
    const [isOpen, setIsOpen] = useState(false);

    const handleToggleOpen = () => {
        if (!isOpen) {
            loadGroupsIfNeeded();
        }
        setIsOpen(prev => !prev);
    };

    const handleGroupToggle = groupUuid => {
        const isSelected = selectedGroups.includes(groupUuid);
        onGroupChange(
            isSelected
                ? selectedGroups.filter(v => v !== groupUuid)
                : [...selectedGroups, groupUuid],
        );
    };

    const handlePartnerFieldToggle = (fieldName, groupUuid) => {
        const isSelected = selectedPartnerFields.includes(fieldName);
        const nextFields = isSelected
            ? selectedPartnerFields.filter(v => v !== fieldName)
            : [...selectedPartnerFields, fieldName];
        onPartnerFieldChange(nextFields);

        // Deselect the parent group if it was group-only selected
        if (!isSelected && selectedGroups.includes(groupUuid)) {
            onGroupChange(selectedGroups.filter(v => v !== groupUuid));
        }
    };

    const toggleGroupExpand = groupUuid => {
        setExpandedGroups(prev => ({
            ...prev,
            [groupUuid]: !prev[groupUuid],
        }));
    };

    const isGroupExpanded = groupUuid => !!expandedGroups[groupUuid];

    return (
        <div className="form__field">
            <div
                className={classes.groupRow}
                onClick={handleToggleOpen}
                role="button"
                tabIndex={0}
                onKeyPress={handleToggleOpen}
            >
                <Typography className={classes.label}>
                    Spotlight Data Partners
                </Typography>
                <IconButton size="small">
                    {isOpen ? <ExpandLess /> : <ExpandMore />}
                </IconButton>
            </div>

            <Collapse in={isOpen}>
                {fetching && (
                    <div className={classes.loadingContainer}>
                        <CircularProgress size={24} />
                    </div>
                )}

                {!fetching &&
                    groups.map(group => (
                        <div key={group.value}>
                            <div className={classes.groupRow}>
                                <FormControlLabel
                                    style={{ flex: 1 }}
                                    control={
                                        <Checkbox
                                            checked={selectedGroups.includes(
                                                group.value,
                                            )}
                                            onChange={() =>
                                                handleGroupToggle(group.value)
                                            }
                                            color="primary"
                                        />
                                    }
                                    label={
                                        <span className={classes.groupLabel}>
                                            {group.label}
                                        </span>
                                    }
                                />
                                {group.partnerFields.length > 0 && (
                                    <IconButton
                                        size="small"
                                        onClick={() =>
                                            toggleGroupExpand(group.value)
                                        }
                                    >
                                        {isGroupExpanded(group.value) ? (
                                            <ExpandLess />
                                        ) : (
                                            <ExpandMore />
                                        )}
                                    </IconButton>
                                )}
                            </div>

                            <Collapse in={isGroupExpanded(group.value)}>
                                <FormGroup className={classes.partnerList}>
                                    {group.partnerFields.map(pf => (
                                        <FormControlLabel
                                            key={pf.value}
                                            control={
                                                <Checkbox
                                                    checked={selectedPartnerFields.includes(
                                                        pf.value,
                                                    )}
                                                    onChange={() =>
                                                        handlePartnerFieldToggle(
                                                            pf.value,
                                                            group.value,
                                                        )
                                                    }
                                                    color="primary"
                                                />
                                            }
                                            label={
                                                <span
                                                    className={
                                                        classes.partnerLabel
                                                    }
                                                >
                                                    {pf.label}
                                                </span>
                                            }
                                        />
                                    ))}
                                </FormGroup>
                            </Collapse>
                        </div>
                    ))}
            </Collapse>
        </div>
    );
};

const partnerFieldPropType = shape({
    value: string.isRequired,
    label: string.isRequired,
});

const groupPropType = shape({
    value: string.isRequired,
    label: string.isRequired,
    partnerFields: arrayOf(partnerFieldPropType).isRequired,
});

SpotlightDataPartnersFilter.propTypes = {
    classes: shape({}).isRequired,
    groups: arrayOf(groupPropType).isRequired,
    fetching: bool.isRequired,
    selectedGroups: arrayOf(string).isRequired,
    selectedPartnerFields: arrayOf(string).isRequired,
    onGroupChange: func.isRequired,
    onPartnerFieldChange: func.isRequired,
    loadGroupsIfNeeded: func.isRequired,
};

const mapStateToProps = state => ({
    groups: getPartnerGroupsForFilter(state),
    fetching: state.partnerFieldGroups.fetching,
    selectedGroups: state.filters.partnerFieldGroups,
    selectedPartnerFields: state.filters.partnerFields,
});

const mapDispatchToProps = dispatch => ({
    onGroupChange: groups => dispatch(setPartnerFieldGroupFilter(groups)),
    onPartnerFieldChange: fields => dispatch(setPartnerFieldFilter(fields)),
    loadGroupsIfNeeded: () => dispatch(fetchPartnerFieldGroupsIfNeeded()),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(styles)(SpotlightDataPartnersFilter));
