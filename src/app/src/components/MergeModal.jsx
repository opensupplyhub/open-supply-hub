import React from 'react';
import { connect } from 'react-redux';

import { withStyles } from '@material-ui/core';
import Modal from '@material-ui/core/Modal';
import Grid from '@material-ui/core/Grid';
import IconButton from '@material-ui/core/IconButton';
import CloseIcon from '@material-ui/icons/Close';

import DashboardMergeFacilities from './DashboardMergeFacilities';

import { toggleMergeModal } from '../actions/ui';

const mergeModalStyles = () =>
    Object.freeze({
        mergeModalWrapper: {
            height: '100%',
            overflowY: 'auto',
            backgroundColor: '#fff',
            '&:focus-visible': {
                outline: 'none',
            },
        },
        mergeModalInnerWrapper: {
            marginLeft: 'auto',
            marginRight: 'auto',
            paddingTop: '16px',
            paddingBottom: '100px',
        },
        closeButtonWrapper: {
            justifyContent: 'end',
        },
        closeButton: {
            marginRight: '20px',
        },
    });

const MergeModal = ({ mergeModalOpen, returnToFacilitySearch, classes }) => (
    <Modal open={mergeModalOpen}>
        <Grid className={classes.mergeModalWrapper} container item>
            <Grid
                className={classes.mergeModalInnerWrapper}
                item
                xs={12}
                sm={9}
            >
                <Grid container item className={classes.closeButtonWrapper}>
                    <IconButton
                        className={classes.closeButton}
                        aria-label="Close"
                        onClick={returnToFacilitySearch}
                    >
                        <CloseIcon />
                    </IconButton>
                </Grid>
                <DashboardMergeFacilities isModalMode />
            </Grid>
        </Grid>
    </Modal>
);

function mapStateToProps({ ui: { mergeModalOpen } }) {
    return {
        mergeModalOpen,
    };
}

function mapDispatchToProps(dispatch) {
    return {
        returnToFacilitySearch: () => dispatch(toggleMergeModal()),
    };
}

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(mergeModalStyles)(MergeModal));
